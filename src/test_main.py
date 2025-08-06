#!/usr/bin/env python3
"""
Unit tests for the Ping-Pong Flask Application using pytest.
"""

import json
from datetime import datetime

import pytest

from main import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_ping_endpoint(client):
    """Test the /ping endpoint returns correct response."""
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = response.get_json()
    assert data["message"] == "pong"


def test_hello_endpoint_valid_json(client):
    """Test the /hello endpoint with valid JSON input."""
    test_data = {"name": "TestUser"}
    response = client.post("/hello", data=json.dumps(test_data), content_type="application/json")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = response.get_json()
    assert "Hello TestUser" in data["message"]
    assert "current time is" in data["message"]


def test_hello_endpoint_missing_name(client):
    """Test the /hello endpoint with missing name field."""
    test_data = {"invalid": "data"}
    response = client.post("/hello", data=json.dumps(test_data), content_type="application/json")

    assert response.status_code == 400
    assert response.content_type == "application/json"

    data = response.get_json()
    assert "Missing 'name' field in JSON payload" in data["error"]


def test_hello_endpoint_no_json(client):
    """Test the /hello endpoint with no JSON payload."""
    response = client.post("/hello")

    # When no Content-Type is set, Flask returns 500 due to JSON parsing error
    assert response.status_code == 500
    assert response.content_type == "application/json"

    data = response.get_json()
    assert "error" in data
    assert "Internal server error" in data["error"]


def test_health_endpoint(client):
    """Test the /health endpoint returns correct health status."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = response.get_json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "ping-pong"  # Default APP_NAME
    assert data["version"] == "1.0.0"


def test_home_endpoint(client):
    """Test the home endpoint returns HTML content."""
    response = client.get("/")

    assert response.status_code == 200
    # Note: This will return 404 if template doesn't exist, but that's expected
    # in a minimal test environment. The endpoint logic is still tested.


def test_app_creation():
    """Test that the Flask app can be created successfully."""
    app = create_app()
    assert app is not None
    assert app.config["TESTING"] == False  # Default value


def test_app_import():
    """Test that the main module can be imported successfully."""
    import main

    assert hasattr(main, "create_app")
    assert hasattr(main, "app")
    assert main.app is not None


class TestEndpointIntegration:
    """Integration tests for endpoint workflows."""

    def test_ping_hello_health_workflow(self, client):
        """Test a complete workflow using multiple endpoints."""
        # Test ping
        ping_response = client.get("/ping")
        assert ping_response.status_code == 200
        assert ping_response.get_json()["message"] == "pong"

        # Test hello
        hello_data = {"name": "Integration"}
        hello_response = client.post("/hello", data=json.dumps(hello_data), content_type="application/json")
        assert hello_response.status_code == 200
        assert "Hello Integration" in hello_response.get_json()["message"]

        # Test health
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.get_json()["status"] == "healthy"


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_hello_endpoint_invalid_json(self, client):
        """Test the /hello endpoint with invalid JSON."""
        response = client.post("/hello", data="invalid json", content_type="application/json")

        # Should handle JSON parsing errors gracefully
        assert response.status_code in [400, 500]

    def test_nonexistent_endpoint(self, client):
        """Test accessing a non-existent endpoint."""
        response = client.get("/nonexistent")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__])
