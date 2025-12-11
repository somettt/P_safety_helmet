CREATE DATABASE IF NOT EXISTS smart_helmet;
USE smart_helmet;

DROP TABLE IF EXISTS risk_result;
DROP TABLE IF EXISTS sensor_log;
DROP TABLE IF EXISTS case_library;

CREATE TABLE sensor_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(50),
    worker_id VARCHAR(50),
    helmet TINYINT,   -- 0 or 1
    temp   FLOAT,
    noise  FLOAT,
    ts     DATETIME
);

CREATE TABLE risk_result (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id  INT,
    risk_level VARCHAR(20),  -- HIGH / MID / LOW
    risk_score FLOAT,
    reason     VARCHAR(255),
    created_at DATETIME,
    FOREIGN KEY (sensor_id) REFERENCES sensor_log(id)
);

CREATE TABLE case_library (
    id INT AUTO_INCREMENT PRIMARY KEY,
    helmet    TINYINT,
    temp      FLOAT,
    noise     FLOAT,
    risk_level VARCHAR(20),  -- HIGH / MID / LOW
    note       VARCHAR(255),
    created_at DATETIME
);