#!/usr/bin/env python3
"""
Setup script for FetchHire database
"""
from database.snowflake_manager import FetchHireSnowflakeManager

def setup_database():
    """Set up the FetchHire database"""
    print("🔧 Setting up FetchHire database...")
    
    sf_manager = FetchHireSnowflakeManager()
    
    if not sf_manager.connect_connector():
        print("❌ Failed to connect to Snowflake")
        return False
    
    try:
        # Drop existing table if it exists
        drop_query = "DROP TABLE IF EXISTS JOB_POSTINGS"
        sf_manager.execute_query(drop_query)
        print("✅ Dropped existing table")
        
        # Create the job postings table
        create_query = """
        CREATE TABLE JOB_POSTINGS (
            "JOB_ID" VARCHAR(255) PRIMARY KEY,
            "TITLE" VARCHAR(500),
            "COMPANY" VARCHAR(255),
            "LOCATION" VARCHAR(255),
            "SALARY" VARCHAR(255),
            "SOURCE" VARCHAR(100),
            "SOURCE_URL" VARCHAR(1000),
            "POSTED_DATE" DATE,
            "TAGS" TEXT,
            "DESCRIPTION" TEXT
        )
        """
        sf_manager.execute_query(create_query)
        print("✅ JOB_POSTINGS table created successfully!")
        
        # Test the table
        test_query = "SELECT COUNT(*) FROM JOB_POSTINGS"
        result = sf_manager.execute_query(test_query)
        if result:
            print(f"✅ Table test successful. Current job count: {result[0][0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    finally:
        sf_manager.close()

if __name__ == "__main__":
    setup_database() 