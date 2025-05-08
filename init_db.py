import mysql.connector
import os
from dotenv import load_dotenv
import bcrypt

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the database with schema and sample data"""
    # Database connection parameters
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
    }
    
    # Connect to MySQL server
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS trip_planner2")
    cursor.execute("USE trip_planner2")
    
    # Read schema file
    with open('database/schema.sql', 'r') as f:
        schema = f.read()
    
    # Split schema into individual statements
    statements = schema.split(';')
    
    # Execute each statement
    for statement in statements:
        if statement.strip():
            cursor.execute(statement)
    
    # Commit changes
    conn.commit()
    
    # Check if admin user exists
    cursor.execute("SELECT * FROM users WHERE email = 'admin@example.com'")
    admin = cursor.fetchone()
    
    # Create admin user if it doesn't exist
    if not admin:
        # Hash password
        password = 'admin123'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert admin user
        cursor.execute("""
            INSERT INTO users (username, email, password, is_admin) 
            VALUES (%s, %s, %s, %s)
        """, ('admin', 'admin@example.com', hashed_password, 1))
        
        # Commit changes
        conn.commit()
        print("Admin user created")
    
    # Close connection
    cursor.close()
    conn.close()
    
    print("Database initialized successfully")

if __name__ == '__main__':
    init_database()