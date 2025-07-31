from typing import List, Dict, Optional
from pydantic import BaseModel, constr, ValidationError
from datetime import datetime
from enum import Enum, IntEnum


###### Enums ######
class CurrencyStrEnum(str, Enum):
    UNKNOWN_CURRENCY = 'UNKNOWN_CURRENCY'
    USD = 'USD'
    JPY = 'JPY'
    EUR = 'EUR'

class CountryStrEnum(str, Enum):
    USA = 'USA'
    JP = 'JP'
    ENG = 'ENG'
    
class EnablingStateEnum(str, Enum):
    UNSPECIFIED = 0 
    ENABLED = 1 
    DISABLED = 2 

class AssetKindEnum(Enum):
    UNKNOWN_ASSET_KIND = 0
    CREATIVE = 1
    CSV = 2
    ASSET_DYNAMIC_CREATIVE = 3
    FB_PLAYABLE_AD = 4

class CreativeTypeEnum(Enum):
    UNKNOWN = 0
    IMAGE = 1
    VIDEO = 2
    HTML = 3

class CreativeGroupStatusEnum(Enum):
    UNKNOWN_STATUS = 0
    DRAFT = 1
    SUBMITTED = 2
    REVIEW_NOT_NEEDED = 3
    UNDER_REVIEW = 4
    APPROVED = 5
    DISAPPROVED = 6

class CampaignTypeEnum(Enum):
    UNKNOWN_CAMPAIGN_TYPE = 0
    GENERIC = 1
    APP_USER_ACQUISITION = 2
    APP_REENGAGEMENT = 3
    WEBSITE_VISIT = 4
    CTV_GENERIC = 5
    CTV_APP_USER_ACQUISITION = 6
    WEB_USER_ACQUISITION = 7
    
class DeviceOSEnum(Enum):
    UNKNOWN_DEVICE_OS = 0
    ANDROID = 1
    IOS = 2
    VERSATILE = 3
    MOBILE_WEB = 4
    
class CampaignStateEnum(Enum):
    UNKNOWN_CAMPAIGN_STATE = 0
    SUBMITTED = 1
    READY = 2
    UPCOMING = 3
    ACTIVE = 4
    PAUSED = 5
    SUSPENDED = 6
    VIOLATED = 7
    COMPLETED = 8

###### Enums ######
    

    
###### Entities ######
class AdAccount(BaseModel):
    id: str
    title: str
    description: str
    timezone: str 
    currency: CurrencyStrEnum 
    updated_at: datetime
    

class AdGroup(BaseModel):
    id: str
    title: str
    enabling_state: EnablingStateEnum
    creative_group_id: List[str]
    updated_at: datetime
    # audiece
    # capper
    # user_buckets


class Creative(BaseModel):
    id: str
    title: str
    enabling_state: EnablingStateEnum
    # advertiser_info: AdvertiserInfo
    type: CreativeTypeEnum
    original_filename: str
    # image: Image Object
    # video: Video Obejct
    # html: Html Object
    updated_at: datetime
    

class CreativeGroup(BaseModel):
    id: str
    title: str
    description: str
    enabling_state: EnablingStateEnum
    creative_ids: List[str]
    status: CreativeGroupStatusEnum
    tracking_link_id: str
    updated_at: datetime


class Campaign(BaseModel):
    id: str
    title: str
    description: str
    enabling_state: EnablingStateEnum
    type: CampaignTypeEnum
    device_os: DeviceOSEnum
    state: CampaignStateEnum
    countries: CountryStrEnum
    currency: CurrencyStrEnum
    # schedual: Schedual Object (start time and end time) 
    tracking_link_id: str
    # goal: CampaignGoal Object
    updated_at: datetime

###### Entities ######