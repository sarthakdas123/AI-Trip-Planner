from flask import render_template
import os
from extensions import create_app, mysql, bcrypt, groq_client
from datetime import datetime, timedelta

# Create Flask app
app = create_app()

# Import routes (after app is created to avoid circular imports)
from routes.auth_routes import auth_bp
from routes.trip_routes import trip_bp
from routes.booking_routes import booking_bp
from routes.weather_routes import weather_bp
from routes.review_routes import review_bp
from routes.api_routes import api_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(trip_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(review_bp)
app.register_blueprint(api_bp)

# Context processor to make variables available to all templates
@app.context_processor
def inject_now():
    return {
        'now': datetime.now(),
        'timedelta': timedelta
    }

@app.route('/')
def index():
    return render_template('index.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', 'True').lower() == 'true')