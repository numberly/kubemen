import pytest
import requests

from kubemen.connectors.base import Connector
from kubemen.models import Change, Character, User

USERNAME = "deep_thought@numberly.com"


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


@pytest.fixture
def review():
    return {
        "kind": "AdmissionReview",
        "request": {
            "dryRun": False,
            "namespace": "magrathea",
            "object": {
                "kind": "Deployment",
                "metadata": {
                    "annotations": {
                        "foo": "bar",
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
                        "foo": "bar",
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
            "userInfo": {"username": USERNAME}
        }
    }


@pytest.fixture
def change(review):
    return Change(review=review, annotations_prefix="kubemen.numberly.com",
                  useless_paths=[])


@pytest.fixture
def character():
    return Character(name="Foo Bar")


@pytest.fixture
def user(review):
    formatted_name = USERNAME.split("@", 1)[0]
    return User(name=USERNAME, formatted_name=formatted_name)
