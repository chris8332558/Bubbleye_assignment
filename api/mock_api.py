import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict
from datetime import datetime
from shared.models import CurrencyStrEnum, CreativeTypeStrEnum, CampaignStateStrEnum
from shared.models import Video, Image, AdAccount, Product, Creative, CreativeGroup, Campaign
import uuid
import uvicorn


app = FastAPI()

ad_accounts: Dict[str, AdAccount] # {uuid4: AdAccount}
creatives: Dict[str, Creative] = {} # {uuid4: Creative}
creative_groups: Dict[str, CreativeGroup] = {} # {uuid4: CreativeGroup}
campaigns: Dict[str, Campaign] = {} # {uuid4: Campaign}

champions_queue = []

@app.post("/ad-accounts")
def create_ad_account(title: str, description: str, timezone: str, currency: CurrencyStrEnum):
    new_id=str(uuid.uuid4())
    new_ad_account = AdAccount(id=new_id, title=title, description=description, timezone=timezone, currency=currency)
    ad_accounts[new_id] = new_ad_account
    return new_ad_account

@app.post("/products")
def create_product(ad_account_id: str, id: str, title:str, description: str):
    new_id = str(uuid.uuid4())
    new_product = Product(id=new_id, title=title, description=description)
    ad_accounts[ad_account_id].add_product()
    return new_product
    

# TODO: Change to use pydantic BaseModel to use Request Body
@app.post("/creatives")
def create_creative(title: str, type: CreativeTypeStrEnum):
    # Check if a creative with this title already exists
    if any(creative.title == title for creative in creatives.values()):
        raise HTTPException(400, f"Creative \"{title}\" already exists") 

    new_id=str(uuid.uuid4())
    if type == CreativeTypeStrEnum.VIDEO:
        the_video = Video(filename=f"{title}.mp4", auto_endcard=True)
        new_creative = Creative(
            id=new_id, 
            title=title,
            type=type,
            filename = the_video.filename,
            video=the_video   
            )
    elif type == CreativeTypeStrEnum.IMAGE:
        the_image = Image(filename=f"{title}.jpg")
        new_creative = Creative(
            id=new_id, 
            title=title, 
            type=type,
            filename = the_image.filename,
            image=the_image
            )

    creatives[new_id] = new_creative
    return new_creative
    
@app.post("/creative-groups")
def create_group(title: str, description: str, creative_ids: List[str] = Query(...)):
    if any(group.title == title for group in creative_groups.values()):
        raise HTTPException(400, f"Group \"{title}\" already exists")

    for c_id in creative_ids:
        if c_id not in creatives:
            raise HTTPException(400, "Creative ID not found")

    new_id = str(uuid.uuid4())
    new_group = CreativeGroup(
        id=new_id,
        title=title,
        description=description,
        creative_ids=creative_ids
    )
    creative_groups[new_id] = new_group
    return new_group

@app.post("/campaigns")
def create_campaign(title: str, description: str, group_ids: List[str] = Query(...)):
    if any(campaign.title == title for campaign in campaigns.values()):
        raise HTTPException(400, f"Campaign \"{title}\" already exists")

    for g_id in group_ids:
        if g_id not in creative_groups:
            raise HTTPException(400, "Group ID not found")

    new_id = str(uuid.uuid4())
    new_campaign = Campaign(
        id=new_id,
        title=title,
        description=description,
        groups_ids=group_ids
    )
    campaigns[new_id] = new_campaign
    return new_campaign 

@app.post("/campaigns/{campaign_title}/attach", response_model=Campaign)
def attach_group_to_campaign(campaign_title: str, group_id: str):
    if campaign_title not in campaigns:
        raise HTTPException(404, "Campaign not found")
    if group_id not in creative_groups:
        raise HTTPException(404, "Group not found")
    the_campaign = campaigns[campaign_title]
    if group_id not in the_campaign.groups:
        the_campaign.groups.append(group_id)
    return the_campaign

@app.get("/creatives", response_model=List[Creative])
def get_creatives():
    return list(creatives.values())

@app.get("/creative-groups", response_model=List[CreativeGroup])
def get_groups():
    return list(creative_groups.values())

@app.get("/campaigns", response_model=List[Campaign])
def get_campaigns():
    return list(campaigns.values())


def get_creatives_as_dict():
    return creatives

def get_creative_id_by_title(title: str) -> str | None:
    """Get creative ID by exact title match"""
    for creative_id, creative in creatives.items():
        if creative.title == title:
            return creative_id
    return None

    
if __name__ == "__main__":
    # Add a good creative group
    create_creative(title='good_creative_1', type=CreativeTypeStrEnum.VIDEO)
    create_creative(title='good_creative_2', type=CreativeTypeStrEnum.VIDEO)
    good_creative_1_id = get_creative_id_by_title('good_creative_1')
    good_creative_2_id = get_creative_id_by_title('good_creative_2')
    create_group(title='good_creative_group', description='High performance group', creative_ids=[good_creative_1_id, good_creative_2_id])

    # Add one creative testing campaign and two regular campaigns
    create_campaign(title='creative_testing_campaign', description='', group_ids=[])
    create_campaign(title='regular_campaign_a', description='', group_ids=[])
    create_campaign(title='regular_campaign_b', description='', group_ids=[])

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)