-- GraphTriage MySQL Schema (Day 2, Step 4)
--
-- Matches docs/design.md Section 1, with ONE addition: a `dataset_split`
-- column on `ticket` (VARCHAR: 'train' / 'val' / 'test'). design.md's original
-- schema didn't need this since it was written before we decided how splits
-- would be tracked end-to-end. This decision is logged in docs/memory.md
-- Section 3 (Key Decisions Log) — docs/design.md has also been updated to
-- match, so this file is not a silent deviation from the design doc.

CREATE TABLE IF NOT EXISTS service (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    owning_team VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS component (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    service_id INT,
    FOREIGN KEY (service_id) REFERENCES service(id)
);

CREATE TABLE IF NOT EXISTS ticket (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    service_id INT,
    component_id INT,
    status VARCHAR(30) DEFAULT 'OPEN',
    priority VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    dataset_split VARCHAR(10) DEFAULT NULL,
    FOREIGN KEY (service_id) REFERENCES service(id),
    FOREIGN KEY (component_id) REFERENCES component(id)
);

CREATE TABLE IF NOT EXISTS bug (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    category VARCHAR(100),
    severity VARCHAR(20),
    FOREIGN KEY (ticket_id) REFERENCES ticket(id)
);

CREATE TABLE IF NOT EXISTS fix (
    id INT PRIMARY KEY AUTO_INCREMENT,
    bug_id INT NOT NULL,
    description TEXT,
    resolution_time_hours FLOAT,
    FOREIGN KEY (bug_id) REFERENCES bug(id)
);

CREATE TABLE IF NOT EXISTS prediction_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    predicted_service VARCHAR(100),
    predicted_root_cause VARCHAR(150),
    predicted_resolution_hours FLOAT,
    confidence FLOAT,
    explanation TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES ticket(id)
);
