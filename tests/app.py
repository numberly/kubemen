import json


def test_get(client):
    response = client.get("/")
    assert response.status_code == 200


def test_post_skip_alerting_service_account(client, review):
    review["request"]["userInfo"]["username"] = "serviceaccount:foo"
    response = client.post("/", data=json.dumps(review))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == review["request"]["uid"]
    assert data["response"]["allowed"] is True


def test_post_skip_alerting_no_domain(client, review):
    review["request"]["userInfo"]["username"] = "deep_thought"
    response = client.post("/", data=json.dumps(review))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == review["request"]["uid"]
    assert data["response"]["allowed"] is True


# TODO: test message content
# TODO: test images in message field
def test_post_create_deployment(client, review):
    review["request"]["operation"] = "CREATE"
    del review["request"]["oldObject"]
    response = client.post("/", data=json.dumps(review))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == review["request"]["uid"]
    assert data["response"]["allowed"] is True
    # requests.post.assert_called_once_with(data={"channel_id": "bot"})


# TODO: test message content
# TODO: test diff in message field
# TODO: test diff corner cases (useless paths + exceptions)
def test_post_update(client, review):
    response = client.post("/", data=json.dumps(review))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == review["request"]["uid"]
    assert data["response"]["allowed"] is True


# TODO: test message content
def test_post_reloaded(client, review):
    del review["request"]["oldObject"]["spec"]
    del review["request"]["object"]["spec"]
    response = client.post("/", data=json.dumps(review))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == review["request"]["uid"]
    assert data["response"]["allowed"] is True


# TODO: test message content
def test_post_delete(client, review):
    review["request"]["operation"] = "DELETE"
    del review["request"]["object"]
    response = client.post("/", data=json.dumps(review))
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"]["uid"] == review["request"]["uid"]
    assert data["response"]["allowed"] is True
