# tests/conftest.py - Pytest configuration and fixtures
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

from api.mock_api import app
from shared.models import CreativeTypeStrEnum

@pytest.fixture(scope="session")
def client():
    """FastAPI test client fixture"""
    return TestClient(app)

@pytest.fixture(scope="session")
def sample_creatives(client):
    """Create sample creatives for testing"""
    # portrait_video = client.post("/creatives", json={"title": "test_portrait_video", "type": CreativeTypeStrEnum.VIDEO})
    # landscape_video = client.post("/creatives", json={"title": "test_landscape_video", "type": CreativeTypeStrEnum.VIDEO})
    portrait_video = client.post("/creatives?title=test_portrait_video&type=VIDEO")
    landscape_video = client.post("/creatives?title=test_landscape_video&type=VIDEO")
    print(portrait_video)
    return portrait_video.json(), landscape_video.json()

@pytest.fixture(scope="session")
def sample_group(client, sample_creatives):
    """Create sample creative group"""
    portrait, landscape = sample_creatives
    id_1=portrait['id']
    id_2=landscape['id']
    response = client.post(f"/creative-groups?title=test_group&description=&creative_ids={id_1}&creative_ids={id_2}")
    return response.json()

@pytest.fixture(scope="session")
def sample_campaign(client, sample_group):
    """Create sample campaign"""
    group_id = sample_group['id']
    response = client.post(f"/campaigns?title=creative_testing_campaign&description=&group_ids={group_id}")
    return response.json()