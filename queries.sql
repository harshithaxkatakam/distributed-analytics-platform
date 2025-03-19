-- Retrieve all data
select * from sensor_data_keyspace.sensor_data ;

-- Retrieve data for a specific sensor in a specific time-range
SELECT * FROM sensor_data_keyspace.sensor_data 
WHERE sensor_id = 'sensor-5' 
AND timestamp > '2024-12-02T18:42:50' 
AND timestamp < '2024-12-02T18:43:00';

-- Retrieve the most recent data for a specific sensor
SELECT * FROM sensor_data_keyspace.sensor_data 
WHERE sensor_id = 'sensor-4' 
ORDER BY timestamp DESC 
LIMIT 5;

-- Detect anamolies
SELECT sensor_id, temperature, timestamp 
FROM sensor_data_keyspace.sensor_data 
WHERE temperature > 28.0;

-- Secondary index
CREATE INDEX IF NOT EXISTS humidity_index ON sensor_data_keyspace.sensor_data (humidity);
SELECT * FROM sensor_data 
WHERE humidity > 50.0 AND humidity < 55.0;


-- Calculate aggregates
SELECT AVG(temperature) AS avg_temp, AVG(humidity) AS avg_hum FROM sensor_data_keyspace.sensor_data;

SELECT MAX(temperature) AS max_temperature 
FROM sensor_data_keyspace.sensor_data 
WHERE sensor_id = 'sensor-1'

SELECT sensor_id, COUNT(*) AS total_readings 
FROM sensor_data_keyspace.sensor_data 
GROUP BY sensor_id;


-- Create Materialized views and query them
CREATE MATERIALIZED VIEW sensor_data_keyspace.sensor_data_by_temperature AS
SELECT sensor_id, timestamp, temperature, humidity
FROM sensor_data_keyspace.sensor_data
WHERE temperature IS NOT NULL
PRIMARY KEY (temperature, timestamp, sensor_id);

SELECT * FROM sensor_data_keyspace.sensor_data_by_temperature 
WHERE temperature > 25.0 AND temperature < 30.0;


-- Set TTL
INSERT INTO sensor_data_keyspace.sensor_data (sensor_id, timestamp, temperature, humidity)
VALUES ('sensor-2', '2024-12-02T18:43:00', 25.0, 50.0)
USING TTL 86400;  -- 1 day
