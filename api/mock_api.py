from fastapi import FastAPI, HTTPException
from typing import List, Dict
import uuid


creatives = []
creative_group = []
campaigns = []
champions_queue = []

def add_creative(name, orientation, file_name):
    creative = {
        "id": str(uuid.uuid4()), 
        "name": name, 
        "orientation": orientation, 
        "file_name": file_name}
    creatives.append(creative)
    return creative