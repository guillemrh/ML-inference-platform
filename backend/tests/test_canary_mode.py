"""
Tests for canary deployment functionality.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.services.traffic_router import TrafficRouter, TrafficSplit


class TestTrafficRouter:
    """Tests for TrafficRouter."""

    def test_default_weight_is_zero(self):
        """Test that default canary weight is 0."""
        router = TrafficRouter()
        assert router.canary_weight == 0

    def test_initial_weight(self):
        """Test setting initial weight via constructor."""
        router = TrafficRouter(canary_weight=25)
        assert router.canary_weight == 25

    def test_set_canary_weight(self):
        """Test updating canary weight."""
        router = TrafficRouter()
        router.set_canary_weight(50)
        assert router.canary_weight == 50

    def test_set_weight_zero(self):
        """Test setting weight to 0 (rollback)."""
        router = TrafficRouter(canary_weight=50)
        router.set_canary_weight(0)
        assert router.canary_weight == 0

    def test_set_weight_100(self):
        """Test setting weight to 100 (full promotion)."""
        router = TrafficRouter()
        router.set_canary_weight(100)
        assert router.canary_weight == 100

    def test_set_invalid_weight_negative(self):
        """Test that negative weight raises ValueError."""
        router = TrafficRouter()
        with pytest.raises(ValueError, match="between 0 and 100"):
            router.set_canary_weight(-1)

    def test_set_invalid_weight_over_100(self):
        """Test that weight over 100 raises ValueError."""
        router = TrafficRouter()
        with pytest.raises(ValueError, match="between 0 and 100"):
            router.set_canary_weight(101)

    def test_get_split(self):
        """Test traffic split calculation."""
        router = TrafficRouter(canary_weight=30)
        split = router.get_split()
        assert split.canary_weight == 30
        assert split.primary_weight == 70

    def test_weight_zero_never_routes_to_canary(self):
        """Test that weight 0 always routes to primary."""
        router = TrafficRouter(canary_weight=0)
        results = [router.should_route_to_canary() for _ in range(1000)]
        assert not any(results)

    def test_weight_100_always_routes_to_canary(self):
        """Test that weight 100 always routes to canary."""
        router = TrafficRouter(canary_weight=100)
        results = [router.should_route_to_canary() for _ in range(1000)]
        assert all(results)

    def test_weight_50_distributes(self):
        """Test that weight 50 gives roughly even distribution."""
        router = TrafficRouter(canary_weight=50)
        results = [router.should_route_to_canary() for _ in range(10000)]
        canary_count = sum(results)
        # Should be between 45% and 55% with 10k samples
        assert 4500 <= canary_count <= 5500, f"Expected ~5000, got {canary_count}"


class TestTrafficSplit:
    """Tests for TrafficSplit dataclass."""

    def test_split_values(self):
        """Test TrafficSplit holds correct values."""
        split = TrafficSplit(primary_weight=90, canary_weight=10)
        assert split.primary_weight == 90
        assert split.canary_weight == 10


class TestCanaryAdminAPI:
    """Tests for admin traffic split endpoints."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        return TestClient(app)

    def test_get_traffic_split(self, client):
        """Test GET /admin/traffic-split returns current config."""
        response = client.get("/admin/traffic-split")
        assert response.status_code == 200

        data = response.json()
        assert "canary_weight" in data
        assert "primary_weight" in data
        assert "canary_model_version" in data
        assert "primary_model_version" in data
        assert data["canary_weight"] + data["primary_weight"] == 100

    def test_post_traffic_split_requires_canary_mode(self, client):
        """Test POST /admin/traffic-split fails when not in canary mode."""
        with patch("app.api.routes.admin.get_model_manager") as mock_get_mm:
            mm = MagicMock()
            mm.canary_enabled = False
            mock_get_mm.return_value = mm

            response = client.post("/admin/traffic-split", json={"canary_weight": 50})
            assert response.status_code == 409

    def test_post_traffic_split_validates_weight(self, client):
        """Test POST /admin/traffic-split validates weight range."""
        response = client.post("/admin/traffic-split", json={"canary_weight": 150})
        assert response.status_code == 422

    def test_post_traffic_split_rejects_negative(self, client):
        """Test POST /admin/traffic-split rejects negative weight."""
        response = client.post("/admin/traffic-split", json={"canary_weight": -5})
        assert response.status_code == 422


class TestCanaryMetrics:
    """Tests for canary-specific metrics."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        return TestClient(app)

    def test_metrics_contain_canary_definitions(self, client):
        """Test that canary metric definitions exist in /metrics."""
        response = client.get("/metrics")
        content = response.text

        assert "canary_requests_total" in content or "canary_weight_percent" in content

    def test_predictions_have_model_version_label(self, client):
        """Test that predictions_total includes model_version label."""
        valid_input = {
            "temperature": 85.0,
            "pressure": 5.5,
            "flow_rate": 25.0,
            "reactant_concentration": 1.2,
            "ph_level": 7.0,
            "stirrer_speed": 300.0,
        }
        client.post("/predict", json=valid_input)

        response = client.get("/metrics")
        content = response.text

        assert "model_version=" in content
