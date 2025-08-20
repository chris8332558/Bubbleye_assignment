# tests/test_backend.py - Test FastAPI endpoints
import pytest
from fastapi.testclient import TestClient
from shared.models import CreativeTypeStrEnum, CampaignStateStrEnum

def test_create_creative(client):
    """Test creative creation"""
    response = client.post("/creatives?title=test_video&type=VIDEO")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "test_video"
    assert data["type"] == CreativeTypeStrEnum.VIDEO 
    assert "id" in data


def test_create_creative_invalid_type(client):
    """Test creative creation with invalid type"""
    response = client.post("/creatives?title=test_video&type=INVALID")
    assert response.status_code == 422 # Validation error

def test_get_creatives_empty(client):
    """Test getting creatives"""
    response = client.get("/creatives")
    assert response.status_code == 200
    # Should return list (might be empty or contain test data)
    assert isinstance(response.json(), list)

def test_create_group(client, sample_creatives):
    """Test creative group creation"""
    portrait, landscape = sample_creatives
    portrait_id = portrait['id']
    landscape_id = landscape['id']
    title = 'test_creative_group'
    response = client.post(f"/creative-groups?title={title}&description=&creative_ids={portrait_id}&creative_ids={landscape_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == title
    assert len(data["creative_ids"]) == 2

def test_create_group_invalid_creative_id(client):
    """Test group creation with non-existent creative IDs"""
    response = client.post("/creative-groups?title=invalid_group&description=&creative_ids=100")
    assert response.status_code == 400

def test_create_group_duplicate_title(client):
    """Test duplicate group title creation"""
    duplicate_title = "dulpicate_group"
    client.post(f"/creative-groups?title={duplicate_title}&description=&creative_ids=")
    response = client.post(f"/creative-groups?title={duplicate_title}&description=&creative_ids=")

    assert response.status_code == 400

def test_create_campaign(client, sample_group):
    """Test campaign creation"""
    gid = sample_group['id']
    response = client.post(f"/campaigns?title=test_create_campaign&description=&group_ids={gid}")
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == "test_create_campaign"
    assert len(data['groups']) == 1 

def test_attach_group_to_campaign(client, sample_campaign):
    """Test attaching creative group to campaign"""
    new_creative = client.post("/creatives?title=test_attach_group_to_campaign_video&type=VIDEO").json()
    new_cid = new_creative['id']
    new_group = client.post(f"/creative-groups?title=test_attach_group_to_campaign_group&description=&creative_ids={new_cid}").json()
    new_gid = new_group['id']
    camp_id = sample_campaign['id']

    response = client.post(f"/campaigns/{camp_id}/attach?group_id={new_gid}")
    campaign_data = response.json()
    assert response.status_code == 200
    assert new_gid in campaign_data["groups"]

def test_launch_empty_campaign(client):
    """Test launching campaign with no groups attached"""
    empty_campaign = client.post(f"/campaigns?title=launch_empty_campaign&description=").json()
    camp_id = empty_campaign['id']
    response = client.post(f"/campaigns/{camp_id}/launch")
    assert empty_campaign['state'] == CampaignStateStrEnum.PAUSED
    assert response.status_code == 400