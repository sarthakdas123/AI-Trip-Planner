from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
mysql = MySQL()
bcrypt = Bcrypt()

# Initialize Groq client
groq_api_key = os.getenv('GROQ_API_KEY')
groq_client = None

# Try to initialize Groq client with better error handling
if groq_api_key:
    try:
        print(f"Initializing Groq client with API key: {groq_api_key[:4]}...{groq_api_key[-4:]}")
        groq_client = groq.Client(api_key=groq_api_key)
        print("Groq client initialized successfully")
    except Exception as e:
        print(f"Error initializing Groq client: {e}")
        print("Will use mock data for itineraries")
else:
    print("No Groq API key found. Will use mock data for itineraries")

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
    
    # Configure MySQL
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'trip_planner2')
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    
    # Initialize extensions with app
    mysql.init_app(app)
    bcrypt.init_app(app)
    
    return app