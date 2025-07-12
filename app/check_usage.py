import sqlite3
from pathlib import Path
import pandas as pd
from datetime import datetime
import csv
import os

def get_db_path():
    """Get the path to the SQLite database file."""
    db_dir = Path(__file__).parent / "data"
    return db_dir / "usage_tracking.db"

def get_connection():
    """Create and return a database connection."""
    db_path = get_db_path()
    if not db_path.exists():
        print("No database file found. The app needs to be run at least once to create the database.")
        return None
    return sqlite3.connect(str(db_path))

def show_summary():
    """Show a summary of the usage statistics."""
    conn = get_connection()
    if not conn:
        return
        
    try:
        print("\n=== Usage Statistics ===")
        
        # Total requests
        total = pd.read_sql("SELECT COUNT(*) as total FROM api_usage", conn).iloc[0,0]
        print(f"Total Requests: {total}")
        
        # Unique users
        unique_users = pd.read_sql("SELECT COUNT(DISTINCT hashed_api_key) FROM api_usage", conn).iloc[0,0]
        print(f"Unique Users: {unique_users}")
        
        # Requests by schema
        print("\nRequests by Schema:")
        schema_counts = pd.read_sql(
            """
            SELECT 
                schema_used, 
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM api_usage), 1) as percentage
            FROM api_usage 
            GROUP BY schema_used 
            ORDER BY count DESC
            """, 
            conn
        )
        print(schema_counts.to_string(index=False))
        
        # Success rate
        success_rate = pd.read_sql(
            """
            SELECT 
                status,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM api_usage), 1) as percentage
            FROM api_usage 
            GROUP BY status
            ORDER BY count DESC
            """, 
            conn
        )
        print("\nStatus Summary:")
        print(success_rate.to_string(index=False))
        
    finally:
        conn.close()

def show_recent_activity(limit=10):
    """Show recent activity from the database."""
    conn = get_connection()
    if not conn:
        return
        
    try:
        print(f"\n=== Last {limit} Activities ===")
        recent = pd.read_sql(
            f"""
            SELECT 
                datetime(timestamp, 'localtime') as timestamp,
                schema_used,
                status,
                error_message
            FROM api_usage 
            ORDER BY timestamp DESC 
            LIMIT {limit}
            """, 
            conn
        )
        
        # Format the timestamp for better readability
        if not recent.empty:
            recent['timestamp'] = pd.to_datetime(recent['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            print(recent.to_string(index=False))
        else:
            print("No activity found.")
            
    finally:
        conn.close()

def get_raw_data(limit=None):
    """Get raw data from the database."""
    conn = get_connection()
    if not conn:
        return None
        
    try:
        query = """
        SELECT 
            id,
            hashed_api_key,
            datetime(timestamp, 'localtime') as timestamp,
            schema_used,
            status,
            error_message
        FROM api_usage 
        ORDER BY timestamp DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
            
        return pd.read_sql(query, conn)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    finally:
        conn.close()

def show_raw_data(limit=10):
    """Show raw data from the database."""
    data = get_raw_data(limit)
    if data is not None and not data.empty:
        print("\n=== Raw Data ===")
        # Display a preview with masked API keys
        display_data = data.copy()
        display_data['hashed_api_key'] = display_data['hashed_api_key'].apply(lambda x: f"{x[:8]}..." if pd.notnull(x) else "")
        print(display_data.to_string(index=False))
    else:
        print("No data found.")

def export_to_csv(filename=None):
    """Export all data to a CSV file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"usage_export_{timestamp}.csv"
    
    data = get_raw_data()
    if data is not None and not data.empty:
        try:
            # Ensure the exports directory exists
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            filepath = export_dir / filename
            data.to_csv(filepath, index=False, quoting=csv.QUOTE_ALL)
            print(f"\n✅ Data exported successfully to: {filepath}")
            print(f"Total records exported: {len(data)}")
            return True
        except Exception as e:
            print(f"\n❌ Error exporting data: {e}")
            return False
    else:
        print("No data to export.")
        return False

def print_menu():
    print("\nOptions:")
    print("1. Show summary")
    print("2. Show recent activity")
    print("3. Show raw data")
    print("4. Export all data to CSV")
    print("5. Exit")

def main():
    print("=== Usage Statistics Viewer ===\n")
    print("This tool helps you monitor and export usage statistics from your app.\n")
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            show_summary()
        elif choice == '2':
            limit = input("Number of recent activities to show (default 10): ").strip()
            show_recent_activity(int(limit) if limit.isdigit() else 10)
        elif choice == '3':
            limit = input("Number of rows to show (default 10, 'all' for all): ").strip().lower()
            if limit == 'all':
                show_raw_data(limit=None)
            else:
                show_raw_data(int(limit) if limit.isdigit() else 10)
        elif choice == '4':
            print("\nExporting all data to CSV...")
            custom_name = input("Enter filename (leave blank for default): ").strip()
            if custom_name and not custom_name.endswith('.csv'):
                custom_name += '.csv'
            export_to_csv(custom_name if custom_name else None)
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
