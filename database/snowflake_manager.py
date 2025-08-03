#!/usr/bin/env python3
"""
Enhanced Snowflake Manager for JobPulse Analytics
Provides advanced Snowflake integration with batch operations, analytics, and real-time features
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd

try:
    import snowflake.connector
    from snowflake.connector.pandas_tools import write_pandas
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    logging.warning("Snowflake connector not available. Install with: pip install snowflake-connector-python")

try:
    from snowflake.snowpark import Session
    SNOWPARK_AVAILABLE = True
except ImportError:
    SNOWPARK_AVAILABLE = False
    logging.warning("Snowpark not available. Install with: pip install snowflake-snowpark-python")

class JobPulseSnowflakeManager:
    """Advanced Snowflake manager for JobPulse Analytics"""
    
    def __init__(self):
        self.connection = None
        self.session = None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for Snowflake operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('JobPulseSnowflake')
        
    def get_connection_params(self) -> Dict[str, str]:
        """Get Snowflake connection parameters from environment variables"""
        return {
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA')
        }
        
    def connect_connector(self) -> bool:
        """Connect using snowflake-connector-python"""
        if not SNOWFLAKE_AVAILABLE:
            self.logger.error("Snowflake connector not available")
            return False
            
        try:
            params = self.get_connection_params()
            self.connection = snowflake.connector.connect(**params)
            self.logger.info("✅ Connected to Snowflake using connector")
            return True
        except Exception as e:
            self.logger.error(f"❌ Snowflake connection failed: {e}")
            return False
            
    def connect_snowpark(self) -> bool:
        """Connect using Snowpark for advanced analytics"""
        if not SNOWPARK_AVAILABLE:
            self.logger.error("Snowpark not available")
            return False
            
        try:
            params = self.get_connection_params()
            self.session = Session.builder.configs(params).create()
            self.logger.info("✅ Connected to Snowflake using Snowpark")
            return True
        except Exception as e:
            self.logger.error(f"❌ Snowpark connection failed: {e}")
            return False
            
    def save_jobs_advanced(self, jobs_data: List[Dict[str, Any]]) -> bool:
        """Save jobs with advanced batch processing"""
        if not self.connection:
            if not self.connect_connector():
                return False
                
        try:
            # Convert to DataFrame
            df = pd.DataFrame(jobs_data)
            
            # Add metadata
            df['CREATED_AT'] = datetime.now()
            df['UPDATED_AT'] = datetime.now()
            
            # Batch insert using pandas
            success, nchunks, nrows, _ = write_pandas(
                self.connection,
                df,
                'JOB_POSTINGS',
                auto_create_table=False,
                overwrite=False
            )
            
            self.logger.info(f"✅ Saved {nrows} jobs in {nchunks} chunks")
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save jobs: {e}")
            return False
            
    def get_advanced_analytics(self) -> Dict[str, Any]:
        """Get advanced analytics using Snowpark"""
        if not self.session:
            if not self.connect_snowpark():
                return {}
                
        try:
            # Query materialized view
            df = self.session.sql("""
                SELECT 
                    SKILLS,
                    job_count,
                    avg_salary_min,
                    avg_salary_max,
                    SOURCE,
                    JOB_TYPE
                FROM SKILL_ANALYTICS
                ORDER BY job_count DESC
                LIMIT 20
            """).collect()
            
            analytics = {
                'skill_analytics': [dict(row) for row in df],
                'total_skills': len(df),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Retrieved {len(df)} skill analytics")
            return analytics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get analytics: {e}")
            return {}
            
    def get_top_companies(self) -> List[Dict[str, Any]]:
        """Get top companies using view"""
        if not self.connection:
            if not self.connect_connector():
                return []
                
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT 
                    COMPANY,
                    job_count,
                    avg_salary_min,
                    avg_salary_max,
                    job_types_count
                FROM TOP_COMPANIES
                LIMIT 10
            """)
            
            results = cursor.fetchall()
            companies = []
            
            for row in results:
                companies.append({
                    'company': row[0],
                    'job_count': row[1],
                    'avg_salary_min': row[2],
                    'avg_salary_max': row[3],
                    'job_types_count': row[4]
                })
                
            self.logger.info(f"✅ Retrieved {len(companies)} top companies")
            return companies
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get top companies: {e}")
            return []
            
    def get_stream_changes(self) -> List[Dict[str, Any]]:
        """Get changes from stream"""
        if not self.connection:
            if not self.connect_connector():
                return []
                
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT 
                    METADATA$ACTION,
                    METADATA$ISUPDATE,
                    METADATA$ROW_ID,
                    TITLE,
                    COMPANY,
                    SOURCE
                FROM JOB_POSTINGS_STREAM
                LIMIT 50
            """)
            
            results = cursor.fetchall()
            changes = []
            
            for row in results:
                changes.append({
                    'action': row[0],
                    'is_update': row[1],
                    'row_id': row[2],
                    'title': row[3],
                    'company': row[4],
                    'source': row[5]
                })
                
            self.logger.info(f"✅ Retrieved {len(changes)} stream changes")
            return changes
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get stream changes: {e}")
            return []
            
    def create_time_travel_backup(self) -> bool:
        """Create a time travel backup"""
        if not self.connection:
            if not self.connect_connector():
                return False
                
        try:
            cursor = self.connection.cursor()
            
            # Create backup table with time travel
            cursor.execute("""
                CREATE TABLE JOB_POSTINGS_BACKUP AS 
                SELECT * FROM JOB_POSTINGS
                AT (TIMESTAMP => DATEADD(hour, -1, CURRENT_TIMESTAMP()))
            """)
            
            self.logger.info("✅ Created time travel backup")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create backup: {e}")
            return False
            
    def close(self):
        """Close connections"""
        if self.connection:
            self.connection.close()
        if self.session:
            self.session.close()
        self.logger.info("✅ Closed Snowflake connections")
