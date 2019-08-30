import json


def test_get(client):
    response = client.get("/")
    assert response.status_code == 200


def test_post_skip_alerting_service_account(client):
    payload = {
        "kind": "AdmissionReview",
        "request": {
            "namespace": "magrathea",
            "object": {
                "kind": "Secret",
                "metadata": {
                    "name": "the-answer-to-the-ultimate-question"
                }
            },
            "operation": "CREATE",
            "uid": "121593ce-bb88-4c69-1fa2-c4ea619cfa4c",
            "userInfo": {"username": "serviceaccount:slartibartfast"}
        }
    }
    response = client.post("/", data=json.dumps(payload))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == payload["request"]["uid"]
    assert data["response"]["allowed"] is True


def test_post_skip_alerting_no_domain(client):
    payload = {
        "kind": "AdmissionReview",
        "request": {
            "namespace": "magrathea",
            "object": {
                "kind": "Secret",
                "metadata": {
                    "name": "the-answer-to-the-ultimate-question"
                }
            },
            "operation": "CREATE",
            "uid": "121593ce-bb88-4c69-1fa2-c4ea619cfa4c",
            "userInfo": {"username": "deep_thought"}
        }
    }
    response = client.post("/", data=json.dumps(payload))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == payload["request"]["uid"]
    assert data["response"]["allowed"] is True


# TODO: test message content
# TODO: test images in message field
def test_post_create_deployment(client):
    payload = {
        "kind": "AdmissionReview",
        "request": {
            "namespace": "magrathea",
            "object": {
                "kind": "Deployment",
                "metadata": {
                    "name": "the-answer-to-the-ultimate-question"
                }
            },
            "oldObject": {
                "kind": "Secret",
                "metadata": {
                    "name": "the-answer-to-the-ultimate-question"
                }
            },
            "operation": "CREATE",
            "uid": "121593ce-bb88-4c69-1fa2-c4ea619cfa4c",
            "userInfo": {"username": "deep_thought@numberly.com"}
        }
    }
    response = client.post("/", data=json.dumps(payload))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == payload["request"]["uid"]
    assert data["response"]["allowed"] is True
    # requests.post.assert_called_once_with(data={"channel_id": "bot"})


# TODO: test message content
# TODO: test diff in message field
# TODO: test diff corner cases (useless paths + exceptions)
def test_post_update(client):
    payload = {
        "kind": "AdmissionReview",
        "request": {
            "namespace": "magrathea",
            "object": {
                "kind": "Deployment",
                "metadata": {
                    "name": "the-answer-to-the-ultimate-question"
                },
                "spec": {
                    "template": {"spec": {"containers": [{"image": "6.9"}]}}
                }
            },
            "oldObject": {
                "kind": "Deployment",
                "metadata": {
                    "name": "the-answer-to-the-ultimate-question"
                },
                "spec": {
                    "template": {"spec": {"containers": [{"image": "4.2"}]}}
                }
            },
            "operation": "UPDATE",
            "uid": "121593ce-bb88-4c69-1fa2-c4ea619cfa4c",
            "userInfo": {"username": "deep_thought@numberly.com"}
        }
    }
    response = client.post("/", data=json.dumps(payload))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == payload["request"]["uid"]
    assert data["response"]["allowed"] is True


# TODO: test message content
def test_post_reloaded(client):
    payload = {
        "kind": "AdmissionReview",
        "request": {
            "namespace": "magrathea",
            "object": {
                "kind": "Deployment",
                "metadata": {
                    "name": "the-answer-to-the-ultimate-question"
                }
            },
            "oldObject": {
                "kind": "Deployment",
                "metadata": {
                    "name": "the-answer-to-the-ultimate-question"
                }
            },
            "operation": "UPDATE",
            "uid": "121593ce-bb88-4c69-1fa2-c4ea619cfa4c",
            "userInfo": {"username": "deep_thought@numberly.com"}
        }
    }
    response = client.post("/", data=json.dumps(payload))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == payload["request"]["uid"]
    assert data["response"]["allowed"] is True


# TODO: test message content
def test_post_delete(client):
    payload = {
        "kind": "AdmissionReview",
        "request": {
            "namespace": "magrathea",
            "oldObject": {
                "kind": "Secret",
                "metadata": {
                    "name": "the-answer-to-the-ultimate-question"
                }
            },
            "operation": "DELETE",
            "uid": "121593ce-bb88-4c69-1fa2-c4ea619cfa4c",
            "userInfo": {"username": "deep_thought@numberly.com"}
        }
    }
    response = client.post("/", data=json.dumps(payload))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == payload["request"]["uid"]
    assert data["response"]["allowed"] is True
