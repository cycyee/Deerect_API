from flask import Flask

# Initialize the Flask app instance
app = Flask(__name__)

# Import the app route from app.py
from .app import api_scrape

# Register the route(s) in the app
app.add_url_rule('/api_scrape', 'api_scrape', api_scrape)