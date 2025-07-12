import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

def get_db_path():
    """Get the path to the SQLite database file."""
    db_dir = Path(__file__).parent / "data"
    db_dir.mkdir(exist_ok=True)
    return db_dir / "usage_tracking.db"

def init_db():
    """Initialize the database with required tables."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create usage tracking table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hashed_api_key TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        schema_used TEXT NOT NULL,
        status TEXT NOT NULL,
        error_message TEXT
    )
    ''')
    
    # Create an index for faster lookups by hashed API key
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_hashed_key 
    ON api_usage(hashed_api_key)
    ''')
    
    conn.commit()
    conn.close()

def hash_api_key(api_key: str) -> str:
    """Hash the API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def log_usage(hashed_api_key: str, schema_used: str, status: str = "success", error_message: str = None):
    """Log API usage to the database."""
    try:
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO api_usage (hashed_api_key, timestamp, schema_used, status, error_message)
        VALUES (?, datetime('now'), ?, ?, ?)
        ''', (hashed_api_key, schema_used, status, error_message))
        
        conn.commit()
    except Exception as e:
        print(f"Error logging usage: {e}")
    finally:
        conn.close()

def get_usage_stats():
    """Get usage statistics from the database."""
    try:
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        # Get total requests
        cursor.execute('SELECT COUNT(*) FROM api_usage')
        total_requests = cursor.fetchone()[0]
        
        # Get requests by schema
        cursor.execute('''
            SELECT schema_used, COUNT(*) as count 
            FROM api_usage 
            GROUP BY schema_used 
            ORDER BY count DESC
        ''')
        schema_stats = cursor.fetchall()
        
        # Get unique API keys count
        cursor.execute('SELECT COUNT(DISTINCT hashed_api_key) FROM api_usage')
        unique_users = cursor.fetchone()[0]
        
        # Get recent activity
        cursor.execute('''
            SELECT timestamp, schema_used, status 
            FROM api_usage 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        recent_activity = cursor.fetchall()
        
        return {
            'total_requests': total_requests,
            'unique_users': unique_users,
            'schema_usage': dict(schema_stats),
            'recent_activity': recent_activity
        }
        
    except Exception as e:
        print(f"Error getting usage stats: {e}")
        return {}
    finally:
        conn.close()
