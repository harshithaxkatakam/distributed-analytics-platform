import json
import random
import time
from datetime import datetime
from confluent_kafka import Producer

# Kafka configuration
KAFKA_TOPIC = "kafka-topic"
KAFKA_BROKER = "localhost:9092"  # Kafka broker address

# Kafka producer configuration
producer_config = {
    "bootstrap.servers": KAFKA_BROKER  # Kafka broker connection
}
producer = Producer(producer_config)

# **Data Ingestion Pipeline**

# Predefined sensor types
SENSOR_TYPES = ['sensor-1', 'sensor-2', 'sensor-3', 'sensor-4', 'sensor-5']

# Function to simulate sensor data
def simulate_data():
    return {
        "sensor_id": random.choice(SENSOR_TYPES),  # Pick a random sensor type
        "timestamp": datetime.utcnow().isoformat(),  # Current UTC time
        "temperature": round(random.uniform(20.0, 30.0), 2),  # Random temperature
        "humidity": round(random.uniform(40.0, 60.0), 2)  # Random humidity
    }

def ingest_data_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

if __name__ == "__main__":
    print(f"Producing messages to Kafka topic '{KAFKA_TOPIC}'...")
    try:
        while True:
            # Generate random sensor data
            sensor_data = simulate_data()
            
            # Convert to JSON
            sensor_data_json = json.dumps(sensor_data)
            
            # Send message to Kafka
            producer.produce(
                KAFKA_TOPIC,
                key=sensor_data["sensor_id"],
                value=sensor_data_json,
                callback=ingest_data_report
            )
            producer.flush()
            print(f"Produced data: {sensor_data}")
            time.sleep(2)

    except KeyboardInterrupt:
        print("Shutting down producer...")
    finally:
        producer.flush()  # Ensure all messages are sent before exit
