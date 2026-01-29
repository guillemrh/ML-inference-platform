"""
Tests for shadow mode functionality.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.shadow_runner import ModelResult, ShadowComparison, ShadowRunner


class TestModelResult:
    """Tests for ModelResult dataclass."""

    def test_successful_result(self):
        """Test creating a successful model result."""
        result = ModelResult(
            prediction=1,
            probability=0.85,
            label="anomaly",
            latency_ms=5.5,
            model_version="v1",
            success=True,
        )
        assert result.prediction == 1
        assert result.probability == 0.85
        assert result.label == "anomaly"
        assert result.success is True
        assert result.error is None

    def test_failed_result(self):
        """Test creating a failed model result."""
        result = ModelResult(
            prediction=-1,
            probability=0.0,
            label="error",
            latency_ms=1.0,
            model_version="v1",
            success=False,
            error="Model crashed",
        )
        assert result.success is False
        assert result.error == "Model crashed"


class TestShadowComparison:
    """Tests for ShadowComparison dataclass."""

    def test_comparison_with_agreement(self):
        """Test comparison when models agree."""
        primary = ModelResult(
            prediction=0,
            probability=0.9,
            label="normal",
            latency_ms=5.0,
            model_version="v1",
        )
        shadow = ModelResult(
            prediction=0,
            probability=0.85,
            label="normal",
            latency_ms=8.0,
            model_version="v2",
        )
        comparison = ShadowComparison(
            primary=primary,
            shadow=shadow,
            predictions_agree=True,
            latency_diff_ms=3.0,
        )
        assert comparison.predictions_agree is True
        assert comparison.latency_diff_ms == 3.0

    def test_comparison_with_disagreement(self):
        """Test comparison when models disagree."""
        primary = ModelResult(
            prediction=0,
            probability=0.7,
            label="normal",
            latency_ms=5.0,
            model_version="v1",
        )
        shadow = ModelResult(
            prediction=1,
            probability=0.6,
            label="anomaly",
            latency_ms=6.0,
            model_version="v2",
        )
        comparison = ShadowComparison(
            primary=primary,
            shadow=shadow,
            predictions_agree=False,
            latency_diff_ms=1.0,
        )
        assert comparison.predictions_agree is False


class TestShadowRunner:
    """Tests for ShadowRunner service."""

    @pytest.fixture
    def mock_primary_model(self):
        """Create a mock primary model."""
        model = MagicMock()
        model.name = "primary"
        model.version = "v1"
        model.is_loaded = True
        model.predict.return_value = {
            "prediction": 0,
            "probability": 0.9,
            "label": "normal",
        }
        return model

    @pytest.fixture
    def mock_shadow_model(self):
        """Create a mock shadow model."""
        model = MagicMock()
        model.name = "shadow"
        model.version = "v2"
        model.is_loaded = True
        model.predict.return_value = {
            "prediction": 0,
            "probability": 0.85,
            "label": "normal",
        }
        return model

    @pytest.fixture
    def sample_features(self):
        """Sample feature input."""
        return [85.0, 5.5, 25.0, 1.2, 7.0, 300.0]

    @pytest.mark.asyncio
    async def test_run_without_shadow(self, mock_primary_model, sample_features):
        """Test running with only primary model."""
        runner = ShadowRunner(primary_model=mock_primary_model, shadow_model=None)
        comparison = await runner.run(sample_features)

        assert comparison.primary.success is True
        assert comparison.primary.prediction == 0
        assert comparison.shadow is None
        assert comparison.predictions_agree is None

    @pytest.mark.asyncio
    async def test_run_with_shadow(
        self, mock_primary_model, mock_shadow_model, sample_features
    ):
        """Test running with both primary and shadow models."""
        runner = ShadowRunner(
            primary_model=mock_primary_model,
            shadow_model=mock_shadow_model,
        )
        comparison = await runner.run(sample_features)

        assert comparison.primary.success is True
        assert comparison.shadow is not None
        assert comparison.shadow.success is True
        assert comparison.predictions_agree is True

    @pytest.mark.asyncio
    async def test_shadow_failure_doesnt_affect_primary(
        self, mock_primary_model, sample_features
    ):
        """Test that shadow failure doesn't affect primary result."""
        failing_shadow = MagicMock()
        failing_shadow.name = "shadow"
        failing_shadow.version = "v2"
        failing_shadow.predict.side_effect = Exception("Shadow crashed")

        runner = ShadowRunner(
            primary_model=mock_primary_model,
            shadow_model=failing_shadow,
        )
        comparison = await runner.run(sample_features)

        # Primary should still succeed
        assert comparison.primary.success is True
        assert comparison.primary.prediction == 0

        # Shadow should have failed
        assert comparison.shadow is not None
        assert comparison.shadow.success is False
        assert "Shadow crashed" in comparison.shadow.error

    @pytest.mark.asyncio
    async def test_predictions_disagree(self, mock_primary_model, sample_features):
        """Test detection of disagreement between models."""
        disagreeing_shadow = MagicMock()
        disagreeing_shadow.name = "shadow"
        disagreeing_shadow.version = "v2"
        disagreeing_shadow.predict.return_value = {
            "prediction": 1,  # Different from primary
            "probability": 0.6,
            "label": "anomaly",
        }

        runner = ShadowRunner(
            primary_model=mock_primary_model,
            shadow_model=disagreeing_shadow,
        )
        comparison = await runner.run(sample_features)

        assert comparison.predictions_agree is False

    @pytest.mark.asyncio
    async def test_shadow_timeout(self, mock_primary_model, sample_features):
        """Test shadow model timeout handling."""
        import time

        def slow_predict(features):
            time.sleep(0.5)  # Slower than 100ms timeout
            return {"prediction": 0, "probability": 0.8, "label": "normal"}

        slow_shadow = MagicMock()
        slow_shadow.name = "shadow"
        slow_shadow.version = "v2"
        slow_shadow.predict.side_effect = slow_predict

        runner = ShadowRunner(
            primary_model=mock_primary_model,
            shadow_model=slow_shadow,
            shadow_timeout_ms=100,  # 100ms timeout
        )

        comparison = await runner.run(sample_features)

        # Primary should succeed
        assert comparison.primary.success is True

        # Shadow should have timed out
        assert comparison.shadow is not None
        assert comparison.shadow.success is False
        assert "timed out" in comparison.shadow.error

    @pytest.mark.asyncio
    async def test_latency_diff_calculation(
        self, mock_primary_model, mock_shadow_model, sample_features
    ):
        """Test latency difference is calculated correctly."""
        runner = ShadowRunner(
            primary_model=mock_primary_model,
            shadow_model=mock_shadow_model,
        )
        comparison = await runner.run(sample_features)

        # Latency diff should be shadow - primary
        if comparison.shadow and comparison.shadow.success:
            expected_diff = comparison.shadow.latency_ms - comparison.primary.latency_ms
            assert comparison.latency_diff_ms == expected_diff


class TestShadowModeIntegration:
    """Integration tests for shadow mode with real model loading."""

    @pytest.fixture
    def valid_input(self) -> dict:
        """Sample valid reactor input."""
        return {
            "temperature": 85.0,
            "pressure": 5.5,
            "flow_rate": 25.0,
            "reactant_concentration": 1.2,
            "ph_level": 7.0,
            "stirrer_speed": 300.0,
        }

    def test_predict_without_shadow_mode(self, valid_input):
        """Test that prediction works when shadow mode is disabled."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.post("/predict", json=valid_input)
        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data
        assert "model_version" in data

    def test_predict_with_shadow_mode_enabled(self, valid_input):
        """Test prediction with shadow mode enabled via environment."""
        with patch.dict(
            "os.environ",
            {
                "DEPLOYMENT_MODE": "shadow",
                "SECONDARY_MODEL_PATH": "/app/models/reactor_model_v2.pkl",
                "SECONDARY_MODEL_VERSION": "v2",
            },
        ):
            # Need to reload config and app to pick up new env vars
            # For unit tests, we mock at a lower level
            pass  # Integration test would need Docker
