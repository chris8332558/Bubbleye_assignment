# tests/test_models.py - Test Pydantic models and type safety
import pytest
from pydantic_core import ValidationError
from shared.models import CreativeTypeStrEnum, Creative, CreativeGroup, Campaign

def test_creative_model_validation():
    """Test Creative model validates types correctly"""
    # Valid creative
    creative = Creative(id='1', title="test_video", filename="test_video.mp4", type=CreativeTypeStrEnum.VIDEO)
    assert creative.title == "test_video"
    assert creative.filename == "test_video.mp4"
    assert creative.type == CreativeTypeStrEnum.VIDEO
    
    # Empty title should raise validation error
    with pytest.raises(ValidationError) as exc_info:
        Creative(id='1', title="", filename="test_video.mp4", type=CreativeTypeStrEnum.VIDEO)
    
    err_msg = str(exc_info.value)
    assert "title" in err_msg.lower()

    # Invalid type should raise validation error
    with pytest.raises(ValidationError) as exc_info:
        Creative(id='1', title="test_title", filename="test_video.mp4", type="INVALID_TYPE")
    
    err_msg = str(exc_info.value)
    assert "type" in err_msg.lower()


def test_creative_group_validation():
    """Test CreativeGroup model"""
    # Valid group
    group = CreativeGroup(id='1', title="test_group", description="test_description", creative_ids=['1', '2'])
    assert len(group.creative_ids) == 2
    
    # Empty creative_ids list should be allowed
    empty_group = CreativeGroup(id='1', title="empty_group", description="test_description", creative_ids=[])
    assert len(empty_group.creative_ids) == 0


def test_campaign_validation():
    """Test Campaign model"""
    # Valid Campaign
    campaign = Campaign(id='1', title='test_campaign', description='test description', groups=['1', '2', '3'])
    assert len(campaign.groups) == 3
    assert len(campaign.impressions) == 3 
    assert campaign.groups == list(campaign.impressions.keys())