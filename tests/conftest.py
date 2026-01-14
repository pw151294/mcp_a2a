import pytest
from starlette.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session", autouse=True)
def client() -> TestClient:
    """创建一个可供所有测试使用的TestClient实例"""
    with TestClient(app) as client:
        yield client

