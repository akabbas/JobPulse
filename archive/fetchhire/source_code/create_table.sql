-- Create JOB_POSTINGS table in Snowflake
CREATE TABLE IF NOT EXISTS JOB_POSTINGS (
    job_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500),
    company VARCHAR(255),
    location VARCHAR(255),
    salary VARCHAR(255),
    source VARCHAR(100),
    source_url VARCHAR(1000),
    posted_date DATE,
    tags VARCHAR(1000),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
); 