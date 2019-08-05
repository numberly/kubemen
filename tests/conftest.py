import pytest

from kubemen.app import app

app.app_context().__enter__()


@pytest.fixture
def client():
    return app.test_client()
