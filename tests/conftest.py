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
