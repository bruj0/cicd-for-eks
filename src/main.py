#!/usr/bin/env python3
"""
Ping-Pong Flask Application
A simple Flask application for testing CICD pipeline to EKS.
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template

# Initialize Flask app
app = Flask(__name__, template_folder='html')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables configuration
PORT = int(os.environ.get('PORT', 5000))
HOST = os.environ.get('HOST', '0.0.0.0')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
APP_NAME = os.environ.get('APP_NAME', 'ping-pong')

@app.route('/', methods=['GET'])
def home():
    """Serve the home page with EKS cluster status."""
    logger.info("Home page accessed")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    return render_template(
        'index.html',
        app_name=APP_NAME,
        current_time=current_time
    )

@app.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint that responds with 'pong'."""
    logger.info("Ping endpoint accessed")
    return "pong"

@app.route('/hello', methods=['POST'])
def hello():
    """
    Endpoint that accepts JSON with name and returns personalized message.
    Expected JSON: {"name": "your_name"}
    Returns: {"message": "Hello your_name, current time is timestamp"}
    """
    logger.info("Hello endpoint accessed")
    
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data provided")
            return jsonify({"error": "No JSON data provided"}), 400
        
        if 'name' not in data:
            logger.warning("Missing 'name' field in JSON")
            return jsonify({"error": "Missing 'name' field in JSON"}), 400
        
        name = data['name']
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        response_message = f"Hello {name}, current time is {current_time}"
        logger.info(f"Greeting generated for: {name}")
        
        return jsonify({"message": response_message})
    
    except Exception as e:
        logger.error(f"Error processing hello request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Kubernetes readiness/liveness probes."""
    logger.info("Health check accessed")
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "app": APP_NAME
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.url}")
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info(f"Starting {APP_NAME} application")
    logger.info(f"Running on {HOST}:{PORT}")
    logger.info(f"Debug mode: {DEBUG}")
    
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )
