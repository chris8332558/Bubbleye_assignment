import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from typing import List, Dict
from datetime import datetime
from shared.models import CurrencyStrEnum, CreativeTypeStrEnum, CampaignStateStrEnum
from shared.models import Video, Image, HTML, AdAccount, Product, Creative, CreativeGroup, Campaign
import uuid
import uvicorn
import asyncio
import random


app = FastAPI()

ad_accounts: Dict[str, AdAccount] # {uuid4: AdAccount}
creatives: Dict[str, Creative] = {} # {uuid4: Creative}
creative_groups: Dict[str, CreativeGroup] = {} # {uuid4: CreativeGroup}
campaigns: Dict[str, Campaign] = {} # {uuid4: Campaign}

champions_queue = [] # For the champion groups for future use in the regular campaigns


### POSTS ###

@app.post("/ad-accounts", response_model=AdAccount)
def create_ad_account(title: str, description: str, timezone: str, currency: CurrencyStrEnum):
    """Create an Ad account. Raise error if its title already exist

    Args:
        title (str): title for the Ad account
        description (str): description for the Ad account
        timezone (str): timezone for the Ad account
        currency (CurrencyStrEnum): currency for the Ad account

    Returns:
        The newly created AdAccount
    """
    if any(adaccount.title == title for adaccount in ad_accounts.values()):
        raise HTTPException(400, f"Ad account \"{title}\" already exists")

    new_id=str(uuid.uuid4())
    new_ad_account = AdAccount(id=new_id, title=title, description=description, timezone=timezone, currency=currency)
    ad_accounts[new_id] = new_ad_account
    return new_ad_account

@app.post("/products", response_model=Product)
def create_product(ad_account_id: str, title:str, description: str):
    """Create a new product for an Ad account

    Args:
        ad_account_id (str): the target Ad account
        title (str): title for the product
        description (str): description for the product

    Returns:
        The newly created Product
    """
    new_id = str(uuid.uuid4())
    new_product = Product(id=new_id, title=title, description=description)
    ad_accounts[ad_account_id].add_product()
    return new_product
    
@app.post("/creatives", response_model=Creative)
def create_creative(title: str, type: CreativeTypeStrEnum):
    """Create a creative with type of image, video, or html

    Args:
        title (str): title for the creative
        type (CreativeTypeStrEnum): Image, Video, or HTML

    Raises:
        HTTPException: Raise 400 error if the creative title already exists

    Returns:
        The newly created Creative
    """
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
    elif type == CreativeTypeStrEnum.HTML:
        the_html = HTML(filename=f"{title}.html")
        new_creative = Creative(
            id=new_id, 
            title=title, 
            type=type,
            filename = the_html.filename,
            html=the_html
            )

    creatives[new_id] = new_creative
    return new_creative
    
@app.post("/creative-groups", response_model=CreativeGroup)
def create_group(title: str, description: str, creative_ids: List[str] = Query(...)):
    """Create a new CreativeGroup

    Args:
        title (str): title for the creative group
        description (str): description for the creative group
        creative_ids (List[str], optional): Creatives to add to this group . Defaults to Query(...).

    Raises:
        HTTPException: 400 error if the group title already exists
        HTTPException: 400 error if the creative(s) doesn't exit

    Returns:
        The newly created CreativeGroup
    """
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

@app.post("/campaigns", response_model=Campaign)
def create_campaign(title: str, description: str, group_ids: List[str] = Query(default=[])):
    """Create a new Campaign

    Args:
        title (str): title for the campaign 
        description (str): description for the campaign
        group_ids (List[str], optional): Groups to add to the campaign. Defaults to Query(...).

    Raises:
        HTTPException: 400 error if the campaign title already exists
        HTTPException: 400 error if the group(s) doesn't exit

    Returns:
        The newly created Campaign 
    """
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
        groups=group_ids,
    )
    campaigns[new_id] = new_campaign
    return new_campaign 

@app.post("/campaigns/{campaign_id}/attach", response_model=Campaign)
def attach_group_to_campaign(campaign_id: str, group_id: str):
    """Attach a CreativeGroup to the Campaign

    Args:
        campaign_id (str): The target campaign id
        group_id (str): The CreativeGroup id to be attached

    Raises:
        HTTPException: 400 error if the Campaign doesn't exist
        HTTPException: 400 error if the CreativeGroup doesn't exist
        HTTPException: 400 error if the CreativeGroup already in the Campaign

    Returns:
        The newly created Campaign
    """
    if campaign_id not in campaigns:
        raise HTTPException(400, "Campaign not found")
    if group_id not in creative_groups:
        raise HTTPException(400, "Group not found")
    the_campaign = campaigns[campaign_id]

    if group_id not in the_campaign.groups:
        the_campaign.groups.append(group_id)
        the_campaign.impressions[group_id] = 0
    else:
        raise HTTPException(400, "Group already in the campaign")
    return the_campaign

@app.post("/campaigns/{campaign_id}/remove", response_model=Campaign)
def remove_group_from_campaign(campaign_id: str, group_id: str):
    """Remove the CreativeGroup from the Campaign

    Args:
        campaign_id (str): The target campaign id
        group_id (str): The CreativeGroup id to be attached

    Raises:
        HTTPException: 400 error if the Campaign doesn't exist
        HTTPException: 400 error if the CreativeGroup doesn't exist
        HTTPException: 400 error if the CreativeGroup is not in the Campaign

    Returns:
        The target Campaign
    """
    if campaign_id not in campaigns:
        raise HTTPException(400, "Campaign not found")
    if group_id not in creative_groups:
        raise HTTPException(400, "Group not found")
    the_campaign = campaigns[campaign_id]

    if group_id in the_campaign.groups:
        the_campaign.groups.remove(group_id)
        the_campaign.impressions.pop(group_id)
    else:
        raise HTTPException(400, "Group is not in the campaign")
    return the_campaign

@app.post("/campaigns/{campaign_id}/launch", response_model=Campaign)
def launch_campaign(campaign_id: str, bg_tasks: BackgroundTasks):
    """Launch the campaign, it'll accumulate impressions in the backgroud

    Raises:
        HTTPException: 400 error if the Campaign doesn't exist
        HTTPException: 400 error if the Campaign has no groups

    Returns:
        The target Campaign
    """
    if campaign_id not in campaigns:
        raise HTTPException(400, "Campaign not found")
    
    the_campaign = campaigns[campaign_id]
    if len(the_campaign.groups) == 0:
        raise HTTPException(400, "Campaign has no groups")

    the_campaign.state = CampaignStateStrEnum.ACTIVE
    bg_tasks.add_task(accumulate_campaign_impressions, campaign_id)

    return the_campaign 
    
    
@app.post("/campaigns/{campaign_id}/pause", response_model=Campaign)
def pause_campaign(campaign_id: str):
    """Pause the campaign

    Raises:
        HTTPException: 400 error if the Campaign doesn't exist

    Returns:
        The target Campaign
    """
    if campaign_id not in campaigns:
        raise HTTPException(400, "Campaign not found")
    
    the_campaign = campaigns[campaign_id]
    if len(the_campaign.groups) == 0:
        raise HTTPException(400, "Campaign has no groups")

    the_campaign.state = CampaignStateStrEnum.PAUSED

    return the_campaign 

@app.post("/campaigns/{campaign_id}/reset", response_model=Campaign)
def reset_campaign(campaign_id: str):
    """Reset the group impressions to 0

    Returns:
        The target Campaign
    """
    the_campaign = campaigns[campaign_id]
    for gid in the_campaign.impressions:
        the_campaign.impressions[gid] = 0

    return the_campaign

### POSTS ###



### Getters ###

@app.get("/creatives", response_model=List[Creative])
def get_creatives():
    return list(creatives.values())

@app.get("/creative-groups", response_model=List[CreativeGroup])
def get_groups():
    return list(creative_groups.values())

@app.get("/campaigns", response_model=List[Campaign])
def get_campaigns():
    return list(campaigns.values())

@app.get("/champions")
def get_champions():
    return champions_queue

### Getters ###


### Helpers ###

def get_creatives_as_dict():
    """Get creative with {key: value} = {id: Creative object}

    Returns:
        Dict[Creatives]: the current creatives
    """
    return creatives

def get_creative_id_by_title(title: str) -> str | None:
    """Get creative ID by exact title match

    Returns:
        str: the target creative id or None if it doesn't exist
    """
    for creative_id, creative in creatives.items():
        if creative.title == title:
            return creative_id
    return None

async def accumulate_campaign_impressions(campaign_id: str):
    """Simulate impression increment after launching the campaign. The campaign will paused when all its groups reach 10,000 impressions.

    Raises:
        HTTPException: 404 error if the campaign doesn't exist.
    """
    if campaign_id not in campaigns:
        raise HTTPException(404, "Campaign not found")

    the_campaign = campaigns[campaign_id]
    while the_campaign.state == CampaignStateStrEnum.ACTIVE:
        all_complete = True
        for gid in the_campaign.groups:
            increment = random.randint(600, 2000)
            the_campaign.impressions[gid] += increment
            if the_campaign.impressions[gid] < 10000:
                all_complete = False

        if all_complete:
            the_campaign.state = CampaignStateStrEnum.PAUSED
            await _select_champion_from_campaign(the_campaign.id)
            break
        
        await asyncio.sleep(1) 
        
async def _select_champion_from_campaign(campaign_id: str):
    """Automatically select the creative group with a highest impression after the campaign paused.

    Args:
        campaign_id (str): the target campaign id.
    """
    the_campaign = campaigns[campaign_id]
    the_champion_group = max(the_campaign.impressions, key=the_campaign.impressions.get)
    if the_champion_group not in champions_queue:
        champions_queue.append(the_champion_group)


### Helpers ###



if __name__ == "__main__":
    # Add the two good creatives and use them to create the good creative group
    create_creative(title='good_creative_1', type=CreativeTypeStrEnum.VIDEO)
    create_creative(title='good_creative_2', type=CreativeTypeStrEnum.VIDEO)
    good_creative_1_id = get_creative_id_by_title('good_creative_1')
    good_creative_2_id = get_creative_id_by_title('good_creative_2')
    create_group(title='good_creative_group', description='High performance group', creative_ids=[good_creative_1_id, good_creative_2_id])

    # Add the creative testing campaign and the two regular campaigns
    create_campaign(title='creative_testing_campaign', description='', group_ids=[])
    create_campaign(title='regular_campaign_a', description='', group_ids=[])
    create_campaign(title='regular_campaign_b', description='', group_ids=[])

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)