from app import app
from database.init_db import init_database
import os

if __name__ == '__main__':
    # Check if database initialization is needed
    if os.getenv('INIT_DB', 'False').lower() == 'true':
        print("Initializing database...")
        init_database()
    
    # Run the application
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=os.getenv('DEBUG', 'True').lower() == 'true')