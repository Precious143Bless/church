"""
Database initialization script for Church Registry System
Run this script to create the MySQL database
"""

import MySQLdb
import sys

def create_database():
    """Create the church registry database if it doesn't exist"""
    try:
        # Connect to MySQL server (without selecting a database)
        connection = MySQLdb.connect(
            host='localhost',
            user='root',
            password='',  # Change this to your MySQL password
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS church_registry_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("Database 'church_registry_db' created successfully!")
        
        cursor.close()
        connection.close()
        
    except MySQLdb.Error as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

def test_connection():
    """Test database connection"""
    try:
        connection = MySQLdb.connect(
            host='localhost',
            user='root',
            password='',  # Change this to your MySQL password
            database='church_registry_db',
            charset='utf8mb4'
        )
        print("Database connection successful!")
        connection.close()
        return True
    except MySQLdb.Error as e:
        print(f"Database connection error: {e}")
        return False

if __name__ == "__main__":
    print("Church Registry System - Database Setup")
    print("=" * 50)
    
    # Create database
    create_database()
    
    # Test connection
    if test_connection():
        print("\nDatabase setup completed successfully!")
        print("\nNext steps:")
        print("1. Update MySQL password in backend/backend/settings.py if needed")
        print("2. Run: python backend/manage.py makemigrations")
        print("3. Run: python backend/manage.py migrate")
        print("4. Run: python backend/manage.py createsuperuser")
        print("5. Run: python backend/manage.py runserver")
    else:
        print("\nPlease ensure MySQL is running and credentials are correct.")