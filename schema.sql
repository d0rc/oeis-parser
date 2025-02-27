-- OEIS Parser Database Schema

-- Sequences table to store main sequence data
CREATE TABLE IF NOT EXISTS sequences (
    a_number TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    terms TEXT,  -- JSON array of integers
    comments TEXT,
    formula TEXT,
    example TEXT,
    data TEXT,  -- Raw JSON payload
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Implementations table to store code implementations
CREATE TABLE IF NOT EXISTS implementations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    a_number TEXT,
    language TEXT,  -- Map from program field (e.g. 'gp', 'mma')
    code TEXT,
    FOREIGN KEY (a_number) REFERENCES sequences(a_number)
);

-- Cross references table to store relationships between sequences
CREATE TABLE IF NOT EXISTS cross_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_a_number TEXT,
    target_a_number TEXT,
    reference_type TEXT,
    FOREIGN KEY (source_a_number) REFERENCES sequences(a_number)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_implementations_a_number ON implementations(a_number);
CREATE INDEX IF NOT EXISTS idx_cross_references_source ON cross_references(source_a_number);
CREATE INDEX IF NOT EXISTS idx_cross_references_target ON cross_references(target_a_number);
