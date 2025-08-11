import os
import logging
from snowflake.connector import connect
from snowflake.connector.errors import ProgrammingError, DatabaseError

class FetchHireSnowflakeManager:
    def __init__(self):
        self.connection = None
        self.session = None
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def connect_connector(self):
        """Connect to Snowflake using environment variables"""
        try:
            # Get credentials from environment variables
            account = os.getenv('SNOWFLAKE_ACCOUNT')
            user = os.getenv('SNOWFLAKE_USER')
            password = os.getenv('SNOWFLAKE_PASSWORD')
            warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
            database = os.getenv('SNOWFLAKE_DATABASE')
            schema = os.getenv('SNOWFLAKE_SCHEMA')
            
            # Validate required environment variables
            if not all([account, user, password, warehouse, database, schema]):
                missing_vars = []
                if not account: missing_vars.append('SNOWFLAKE_ACCOUNT')
                if not user: missing_vars.append('SNOWFLAKE_USER')
                if not password: missing_vars.append('SNOWFLAKE_PASSWORD')
                if not warehouse: missing_vars.append('SNOWFLAKE_WAREHOUSE')
                if not database: missing_vars.append('SNOWFLAKE_DATABASE')
                if not schema: missing_vars.append('SNOWFLAKE_SCHEMA')
                
                self.logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
                return False
            
            # Connect to Snowflake
            self.connection = connect(
                account=account,
                user=user,
                password=password,
                warehouse=warehouse,
                database=database,
                schema=schema
            )
            
            # Test the connection
            cursor = self.connection.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            cursor.close()
            
            self.logger.info(f"✅ Connected to Snowflake successfully! Version: {version}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Snowflake: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            if not self.connection:
                self.logger.error("❌ No active connection to Snowflake")
                return None
                
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            results = cursor.fetchall()
            cursor.close()
            
            self.logger.info(f"✅ Query executed successfully. Rows returned: {len(results)}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Query execution failed: {e}")
            return None
    
    def create_backup_table(self):
        """Create a backup table with time travel"""
        try:
            if not self.connection:
                self.logger.error("❌ No active connection to Snowflake")
                return False
                
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