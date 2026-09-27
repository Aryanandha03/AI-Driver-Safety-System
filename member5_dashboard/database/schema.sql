PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS drivers (
    driver_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id TEXT PRIMARY KEY,
    description TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    driver_id TEXT,
    vehicle_id TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    FOREIGN KEY(driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
);
CREATE TABLE IF NOT EXISTS gps_locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    timestamp TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'mock',
    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);
CREATE TABLE IF NOT EXISTS safety_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    event_type TEXT NOT NULL,
    value TEXT,
    details_json TEXT NOT NULL DEFAULT '{}',
    timestamp TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);
CREATE TABLE IF NOT EXISTS emergencies (
    emergency_id TEXT PRIMARY KEY,
    session_id TEXT,
    driver_id TEXT,
    vehicle_id TEXT,
    reason TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    location_timestamp TEXT,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    details_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(session_id) REFERENCES sessions(session_id),
    FOREIGN KEY(driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
);
CREATE INDEX IF NOT EXISTS idx_events_time ON safety_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_gps_time ON gps_locations(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_emergency_time ON emergencies(created_at DESC);
