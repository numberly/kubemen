import json


def test_get(client):
    response = client.get("/")
    assert response.status_code == 200


# TODO: test with full and valid admission review object
def test_post(client):
    payload = {
        "request": {
            "uid": 42,
            "userInfo": {"username": "deep_thought"}
        }
    }
    response = client.post("/", data=json.dumps(payload))
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["response"]["uid"] == payload["request"]["uid"]
    assert data["response"]["allowed"] is True
