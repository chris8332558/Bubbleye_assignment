import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict
from datetime import datetime
from shared.models import CurrencyStrEnum, CreativeTypeStrEnum, CampaignStateStrEnum
from shared.models import AdAccount, Product, Creative, CreativeGroup, Campaign
import uuid
import uvicorn


app = FastAPI()

ad_accounts: Dict[str, AdAccount] # {id: AdAccount}
creatives: Dict[str, Creative] = {} # {id: Creative}
creative_groups: Dict[str, CreativeGroup] = {} # {id: CreativeGroup} 
campaigns: Dict[str, Campaign] = { # {id: Campaign}
    'creative_testing_campaign': Campaign(id=str(uuid.uuid4()), title='creative_testing_campaign', groups=[], state=CampaignStateStrEnum.PAUSED),
    'regular_campaign_a': Campaign(id=str(uuid.uuid4()), title='regular_campaign_a', groups=[], state=CampaignStateStrEnum.PAUSED),
    'regular_campaign_b': Campaign(id=str(uuid.uuid4()), title='regular_campaign_b', groups=[], state=CampaignStateStrEnum.PAUSED)
    }

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
    new_id=str(uuid.uuid4())
    new_creative = Creative(
        id=new_id, 
        title=title, 
        type=type 
        )
    creatives[new_id] = new_creative
    return new_creative
    
@app.post("/creative-groups")
def create_group(title: str, description: str, creative_ids: List[str] = Query(...)):
    for c_id in creatives:
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

    
# Run server (call this in a main.py or via command)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)