from fastapi import FastAPI, HTTPException
from typing import List, Dict
from datetime import datetime
from shared.models import CurrencyStrEnum
from shared.models import AdAccount, Product, Creative, CreativeGroup, Campaign
import uuid

app = FastAPI()

ad_accounts: Dict[str, AdAccount] # {id: AdAccount}
creatives: Dict[str, Creative] = {} # {id: Creative}
creative_groups: Dict[str, CreativeGroup] = {} # {id: CreativeGroup} 
campaigns: Dict[str, Campaign] = {} # {id: Campaign}
champions_queue = []

@app.post("/ad-accounts")
def create_ad_account(title: str, description: str, timezone: str, currency: CurrencyStrEnum):
    new_id=str(uuid.uuid4())
    new_ad_account = AdAccount(id=new_id, title=title, description=description, timezone=timezone, currency=currency)
    ad_accounts[new_id] = new_ad_account
    return new_ad_account
    

@app.post("/products/")
def create_product(ad_account_id: str, id: str, title:str, description: str):
    new_id = str(uuid.uuid4())
    new_product = Product(id=new_id, title=title, description=description)
    ad_accounts[ad_account_id].add_product()
    return new_product
    
@app.post("/creatives")
def create_creative(name, orientation, file_name):
    creative = {
        "id": str(uuid.uuid4()), 
        "name": name, 
        "orientation": orientation, 
        "file_name": file_name}
    creatives.append(creative)
    return creative