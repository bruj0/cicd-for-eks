#!/usr/bin/env python3
"""
Ping-Pong Flask Application
A simple Flask application for testing CICD pipeline to EKS.
"""

import logging
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Environment variables configuration
PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")  # nosec B104
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
APP_NAME = os.environ.get("APP_NAME", "ping-pong")


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="html")

    @app.route("/", methods=["GET"])
    def home():
        """Serve the home page with EKS cluster status."""
        logger.info("Home page accessed")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

        return render_template("index.html", app_name=APP_NAME, current_time=current_time)

    @app.route("/ping", methods=["GET"])
    def ping():
        """Health check endpoint that responds with 'pong'."""
        logger.info("Ping endpoint accessed")
        return jsonify({"message": "pong"})

    @app.route("/iseven", methods=["POST"])
    def iseven():
        logger.info("Iseven endpoint accessed")
        try:
            data = request.get_json()
            number = data["number"]
            if number % 2 == 0:
                return 200
            else:
                return 400

          except Exception as e:
            logger.error(f"Error processing hello request: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
        
    @app.route("/hello", methods=["POST"])
    def hello():
        """
        Endpoint that accepts JSON with name and returns personalized message.
        Expected JSON: {"name": "your_name"}
        """
        logger.info("Hello endpoint accessed")

        try:
            data = request.get_json()

            if not data or "name" not in data:
                return jsonify({"error": "Missing 'name' field in JSON payload"}), 400

            name = data["name"]
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

            response = {"message": f"Hello {name}, current time is {current_time}"}

            logger.info(f"Hello response sent for name: {name}")
            return jsonify(response)

        except Exception as e:
            logger.error(f"Error processing hello request: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint for Kubernetes probes."""
        logger.info("Health check endpoint accessed")

        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "service": APP_NAME,
            "version": "1.0.0",
        }

        return jsonify(health_data)

    return app


# Create app instance for imports (used by tests and WSGI servers)
app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting {APP_NAME} application")
    logger.info(f"Running on {HOST}:{PORT}")
    logger.info(f"Debug mode: {DEBUG}")

    app.run(host=HOST, port=PORT, debug=DEBUG)
