import json
import uuid
from cassandra.cluster import Cluster
from confluent_kafka import Consumer, KafkaError

# Kafka configuration
KAFKA_TOPIC = "kafka-topic"
KAFKA_BROKER = "localhost:9092"
GROUP_ID = "consumer-group"

# Cassandra configuration
CASSANDRA_KEYSPACE = "sensor_data_keyspace"
CASSANDRA_TABLE = "sensor_data"

# **Cassandra Setup**
def cassandra_setup():
    cluster = Cluster(['127.0.0.1'])  # Replace with your Cassandra IP
    session = cluster.connect()
    
    # Create keyspace and table if not exist
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': 3 }};
    """)
    session.set_keyspace(CASSANDRA_KEYSPACE)
    
    session.execute(f"""
        CREATE TABLE IF NOT EXISTS {CASSANDRA_TABLE} (
            sensor_id TEXT,
            timestamp TIMESTAMP,
            temperature FLOAT,
            humidity FLOAT,
            PRIMARY KEY (sensor_id, timestamp)
        ) WITH CLUSTERING ORDER BY (timestamp DESC);
    """)
    return session

# Insert data into Cassandra
def insert_data_to_cassandra(session, data):
    session.execute(f"""
        INSERT INTO {CASSANDRA_TABLE} (sensor_id, timestamp, temperature, humidity)
        VALUES (%s, %s, %s, %s)
    """, (data["sensor_id"], data["timestamp"], data["temperature"], data["humidity"]))

# Query data from Cassandra
def query_data(session, sensor_id):
    rows = session.execute(f"""
        SELECT * FROM {CASSANDRA_TABLE} WHERE sensor_id = %s LIMIT 5;
    """, (sensor_id,))
    print(f"Recent data for sensor {sensor_id}:")
    for row in rows:
        print(row)

# **Kafka Consumer Setup**
def kafka_consumer_setup():
    consumer_config = {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe([KAFKA_TOPIC])
    return consumer

if __name__ == "__main__":
    # Set up Cassandra
    cassandra_session = cassandra_setup()
    
    # Set up Kafka Consumer
    kafka_consumer = kafka_consumer_setup()
    print(f"Subscribed to Kafka topic '{KAFKA_TOPIC}'...")

    try:
        while True:
            msg = kafka_consumer.poll(1.0)  # Poll messages with a timeout of 1 second
            
            if msg is None:  # No new message
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    continue
                else:
                    print(f"Error: {msg.error()}")
                    continue

            # Parse Kafka message
            sensor_data = json.loads(msg.value().decode('utf-8'))
            print(f"Received data: {sensor_data}")

            # Insert data into Cassandra
            insert_data_to_cassandra(cassandra_session, sensor_data)

            # Perform query for recent data for the same sensor ID
            query_data(cassandra_session, sensor_data["sensor_id"])

    except KeyboardInterrupt:
        print("Shutting down consumer...")
    finally:
        kafka_consumer.close()
