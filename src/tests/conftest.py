import pytest
import cloudpassage

class MockResponse:
    """Mock Class to mock HaloSession"""
    @staticmethod
    def authenticate_client():
        return {"mock_key": "mock_response"}

@pytest.fixture(autouse=True)
def no_session(monkeypatch):
    """Patch HaloSession for all tests."""
    def fake_session(*args, **kwargs):
        return MockResponse()
    monkeypatch.setattr(cloudpassage, "HaloSession", fake_session)