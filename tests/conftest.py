import pytest
import requests

from kubemen.app import app

app.app_context().__enter__()


@pytest.fixture
def client():
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
