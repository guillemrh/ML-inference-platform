"""API integration tests for model registry endpoints."""


def _register_model(client, name="reactor_model", version="v1", file_path="/app/models/reactor_model_v1.pkl"):
    return client.post("/api/v1/models", json={"name": name, "version": version, "file_path": file_path})


class TestRegisterModel:
    def test_register_success(self, client):
        resp = _register_model(client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "reactor_model"
        assert data["version"] == "v1"
        assert data["status"] == "registered"

    def test_register_duplicate_returns_409(self, client):
        _register_model(client)
        resp = _register_model(client)
        assert resp.status_code == 409

    def test_register_with_metadata(self, client):
        resp = client.post(
            "/api/v1/models",
            json={"name": "m", "version": "v1", "file_path": "/p", "metadata": {"accuracy": 0.95}},
        )
        assert resp.status_code == 201
        assert resp.json()["metadata"] == {"accuracy": 0.95}


class TestListModels:
    def test_list_empty(self, client):
        resp = client.get("/api/v1/models")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_with_filter(self, client):
        _register_model(client, version="v1")
        _register_model(client, name="other_model", version="v1")
        resp = client.get("/api/v1/models", params={"name": "reactor_model"})
        assert len(resp.json()) == 1


class TestPromoteModel:
    def test_promote_success(self, client):
        _register_model(client)
        resp = client.post("/api/v1/models/1/promote", json={"deployment_mode": "primary"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "active"

    def test_promote_nonexistent_returns_404(self, client):
        resp = client.post("/api/v1/models/999/promote", json={"deployment_mode": "primary"})
        assert resp.status_code == 404

    def test_promote_replaces_previous(self, client):
        _register_model(client, version="v1")
        _register_model(client, version="v2")
        client.post("/api/v1/models/1/promote", json={"deployment_mode": "primary"})
        client.post("/api/v1/models/2/promote", json={"deployment_mode": "primary"})

        # v1 should now be deprecated
        models = client.get("/api/v1/models", params={"status": "deprecated"}).json()
        assert len(models) == 1
        assert models[0]["version"] == "v1"


class TestGetActiveModel:
    def test_active_returns_promoted_model(self, client):
        _register_model(client)
        client.post("/api/v1/models/1/promote", json={"deployment_mode": "primary"})
        resp = client.get("/api/v1/models/active", params={"name": "reactor_model", "mode": "primary"})
        assert resp.status_code == 200
        assert resp.json()["version"] == "v1"

    def test_active_not_found(self, client):
        resp = client.get("/api/v1/models/active", params={"name": "nonexistent", "mode": "primary"})
        assert resp.status_code == 404


class TestRollback:
    def test_rollback_success(self, client):
        _register_model(client, version="v1")
        _register_model(client, version="v2")
        client.post("/api/v1/models/1/promote", json={"deployment_mode": "primary"})
        client.post("/api/v1/models/2/promote", json={"deployment_mode": "primary"})

        resp = client.post(
            "/api/v1/models/rollback",
            json={"name": "reactor_model", "deployment_mode": "primary"},
        )
        assert resp.status_code == 200
        assert resp.json()["version"] == "v1"
        assert resp.json()["status"] == "active"

    def test_rollback_no_deployment_returns_404(self, client):
        resp = client.post(
            "/api/v1/models/rollback",
            json={"name": "nonexistent", "deployment_mode": "primary"},
        )
        assert resp.status_code == 404


class TestModelHistory:
    def test_history_after_register_and_promote(self, client):
        _register_model(client)
        client.post("/api/v1/models/1/promote", json={"deployment_mode": "primary"})
        resp = client.get("/api/v1/models/1/history")
        assert resp.status_code == 200
        actions = [h["action"] for h in resp.json()]
        assert "registered" in actions
        assert "promoted" in actions

    def test_history_nonexistent_returns_404(self, client):
        resp = client.get("/api/v1/models/999/history")
        assert resp.status_code == 404
