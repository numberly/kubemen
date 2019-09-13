import json


def _is_allowed(response):
    return (response.status_code == 200
            and response.get_json()["response"]["allowed"] is True)


def test_get(client, connector):
    response = client.get("/")
    assert response.status_code == 200
    assert "response" not in response.get_json()
    assert connector.send.call_count == 0


def test_post(client, review, connector):
    response = client.post("/", data=json.dumps(review))
    assert _is_allowed(response)
    assert connector.send.call_count == 1


def test_post_skip_alerting_service_account(client, review, connector):
    review["request"]["userInfo"]["username"] = "serviceaccount:foo"
    response = client.post("/", data=json.dumps(review))
    assert _is_allowed(response)
    assert connector.send.call_count == 0


def test_post_skip_alerting_no_domain(client, review, connector):
    review["request"]["userInfo"]["username"] = "deep_thought"
    response = client.post("/", data=json.dumps(review))
    assert _is_allowed(response)
    assert connector.send.call_count == 0


def test_post_create_deployment(client, review, connector):
    review["request"]["operation"] = "CREATE"
    del review["request"]["oldObject"]
    response = client.post("/", data=json.dumps(review))
    assert _is_allowed(response)
    assert connector.send.call_count == 1
    assert connector.send.call_args[0][0].operation == "CREATE"


def test_post_reload(client, review, connector):
    del review["request"]["oldObject"]["spec"]
    del review["request"]["object"]["spec"]
    response = client.post("/", data=json.dumps(review))
    assert _is_allowed(response)
    assert connector.send.call_count == 1
    assert connector.send.call_args[0][0].operation == "RELOAD"


def test_post_delete(client, review, connector):
    review["request"]["operation"] = "DELETE"
    del review["request"]["object"]
    response = client.post("/", data=json.dumps(review))
    assert _is_allowed(response)
    assert connector.send.call_count == 1
    assert connector.send.call_args[0][0].operation == "DELETE"


def test_invalid_connector(client, review, connector, caplog):
    from kubemen.app import app

    app.config["AVAILABLE_CONNECTORS"] = ["invalid"]
    response = client.post("/", data=json.dumps(review))
    assert _is_allowed(response)
    assert connector.send.call_count == 0
    assert "invalid" in caplog.text
