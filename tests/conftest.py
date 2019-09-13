import pytest
import requests

from kubemen.connectors.base import Connector


class FakeConnector(Connector):
    pass


@pytest.fixture
def connector(mocker):
    FakeConnector.send = mocker.stub()
    return FakeConnector


@pytest.fixture
def app():
    from kubemen.app import app
    app.config["AVAILABLE_CONNECTORS"] = (
        "tests.conftest.FakeConnector",
    )
    app.config["FAKECONNECTOR_ENABLE"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def mattermock(mocker):
    mocker.patch.object(requests, "post")


@pytest.fixture
def review():
    return {
        "kind": "AdmissionReview",
        "request": {
            "namespace": "magrathea",
            "object": {
                "kind": "Deployment",
                "metadata": {
                    "annotations": {
                        "foo/bar": "baz",
                        "kubemen.numberly.com/fancyness-level": "1",
                        "kubemen.numberly.com/mattermost.fancyness-level": "2"
                    },
                    "name": "the-answer-to-the-ultimate-question"
                },
                "spec": {
                    "template": {"spec": {"containers": [{"image": "6.9"}]}}
                }
            },
            "oldObject": {
                "kind": "Deployment",
                "metadata": {
                    "annotations": {
                        "foo/bar": "baz",
                        "kubemen.numberly.com/fancyness-level": "1",
                        "kubemen.numberly.com/mattermost.fancyness-level": "2"
                    },
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
