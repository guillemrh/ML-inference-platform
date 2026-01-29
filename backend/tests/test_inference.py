"""
Tests for inference endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestPredictEndpoint:
    """Tests for /predict endpoint."""

    @pytest.fixture
    def valid_input(self) -> dict:
        """Sample valid reactor input within normal ranges."""
        return {
            "temperature": 85.0,
            "pressure": 5.5,
            "flow_rate": 25.0,
            "reactant_concentration": 1.2,
            "ph_level": 7.0,
            "stirrer_speed": 300.0,
        }

    @pytest.fixture
    def anomaly_input(self) -> dict:
        """Sample input likely to be classified as anomaly."""
        return {
            "temperature": 115.0,  # High temp
            "pressure": 9.0,  # High pressure
            "flow_rate": 25.0,
            "reactant_concentration": 1.8,
            "ph_level": 4.5,  # Low pH
            "stirrer_speed": 150.0,  # Low stirrer with high concentration
        }

    def test_predict_returns_200(self, valid_input: dict):
        """Test that valid input returns 200 OK."""
        response = client.post("/predict", json=valid_input)
        assert response.status_code == 200

    def test_predict_response_schema(self, valid_input: dict):
        """Test that response contains all required fields."""
        response = client.post("/predict", json=valid_input)
        data = response.json()

        assert "prediction" in data
        assert "probability" in data
        assert "label" in data
        assert "model_version" in data
        assert "latency_ms" in data

    def test_predict_response_types(self, valid_input: dict):
        """Test that response fields have correct types."""
        response = client.post("/predict", json=valid_input)
        data = response.json()

        assert isinstance(data["prediction"], int)
        assert data["prediction"] in [0, 1]
        assert isinstance(data["probability"], float)
        assert 0 <= data["probability"] <= 1
        assert data["label"] in ["normal", "anomaly"]
        assert isinstance(data["model_version"], str)
        assert isinstance(data["latency_ms"], float)
        assert data["latency_ms"] >= 0

    def test_predict_label_matches_prediction(self, valid_input: dict):
        """Test that label matches prediction value."""
        response = client.post("/predict", json=valid_input)
        data = response.json()

        if data["prediction"] == 0:
            assert data["label"] == "normal"
        else:
            assert data["label"] == "anomaly"

    def test_predict_missing_field_returns_422(self, valid_input: dict):
        """Test that missing required field returns 422."""
        del valid_input["temperature"]
        response = client.post("/predict", json=valid_input)
        assert response.status_code == 422

    def test_predict_empty_body_returns_422(self):
        """Test that empty body returns 422."""
        response = client.post("/predict", json={})
        assert response.status_code == 422

    def test_predict_invalid_type_returns_422(self, valid_input: dict):
        """Test that invalid type returns 422."""
        valid_input["temperature"] = "not a number"
        response = client.post("/predict", json=valid_input)
        assert response.status_code == 422

    def test_predict_out_of_range_returns_422(self, valid_input: dict):
        """Test that out-of-range values return 422."""
        valid_input["temperature"] = 300.0  # Above max 200
        response = client.post("/predict", json=valid_input)
        assert response.status_code == 422

    def test_predict_negative_value_returns_422(self, valid_input: dict):
        """Test that negative values return 422."""
        valid_input["pressure"] = -5.0
        response = client.post("/predict", json=valid_input)
        assert response.status_code == 422

    def test_predict_latency_is_reasonable(self, valid_input: dict):
        """Test that inference latency is under 100ms."""
        response = client.post("/predict", json=valid_input)
        data = response.json()
        assert data["latency_ms"] < 100, f"Latency too high: {data['latency_ms']}ms"

    def test_predict_deterministic(self, valid_input: dict):
        """Test that same input produces same output."""
        response1 = client.post("/predict", json=valid_input)
        response2 = client.post("/predict", json=valid_input)

        data1 = response1.json()
        data2 = response2.json()

        assert data1["prediction"] == data2["prediction"]
        assert data1["probability"] == data2["probability"]
        assert data1["label"] == data2["label"]


class TestPredictEndpointEdgeCases:
    """Edge case tests for /predict endpoint."""

    def test_predict_boundary_values(self):
        """Test prediction with boundary values."""
        boundary_input = {
            "temperature": 0.0,  # Minimum
            "pressure": 0.0,
            "flow_rate": 0.0,
            "reactant_concentration": 0.0,
            "ph_level": 0.0,
            "stirrer_speed": 0.0,
        }
        response = client.post("/predict", json=boundary_input)
        assert response.status_code == 200

    def test_predict_maximum_values(self):
        """Test prediction with maximum allowed values."""
        max_input = {
            "temperature": 200.0,
            "pressure": 20.0,
            "flow_rate": 100.0,
            "reactant_concentration": 5.0,
            "ph_level": 14.0,
            "stirrer_speed": 1000.0,
        }
        response = client.post("/predict", json=max_input)
        assert response.status_code == 200

    def test_predict_float_precision(self):
        """Test that float precision is handled correctly."""
        precise_input = {
            "temperature": 85.123456789,
            "pressure": 5.999999999,
            "flow_rate": 25.000000001,
            "reactant_concentration": 1.2,
            "ph_level": 7.0,
            "stirrer_speed": 300.0,
        }
        response = client.post("/predict", json=precise_input)
        assert response.status_code == 200
