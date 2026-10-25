
from app import app


def test_health_endpoint():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}
