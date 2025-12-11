PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS risk_result;
DROP TABLE IF EXISTS sensor_log;

CREATE TABLE sensor_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    temp REAL NOT NULL,
    noise REAL NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE TABLE risk_result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    reason TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (sensor_id) REFERENCES sensor_log(id)
);
