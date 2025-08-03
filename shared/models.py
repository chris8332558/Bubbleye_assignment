from typing import List, Dict, Optional
from pydantic import BaseModel, constr, ValidationError, Field
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
    UNSPECIFIED = 'UNSPECIFIED'
    ENABLED = 'ENABLED' 
    DISABLED = 'DISABLED' 

class AssetKindStrEnum(str, Enum):
    UNKNOWN_ASSET_KIND = 'UNKOWN_ASSET_KIND'
    CREATIVE = 'CREATIVE'
    CSV = 'CSV'
    ASSET_DYNAMIC_CREATIVE = 'ASSET_DYNAMIC_CREATIVE'
    FB_PLAYABLE_AD = 'FB_PLAYABLE_AD'

class CreativeTypeStrEnum(str, Enum):
    UNKNOWN = "UNKNOWN" 
    IMAGE = "IMAGE" 
    VIDEO = "VIDEO"
    HTML = "HTML" 

class CreativeGroupStatusStrEnum(str, Enum):
    UNKNOWN_STATUS = 'UNKNOWN_STATUS'
    DRAFT = 'DRAFT' 
    SUBMITTED = 'SUBMITTED' 
    REVIEW_NOT_NEEDED = 'REVIEW_NOT_NEEDED'
    UNDER_REVIEW = 'UNDER_REVIEW'
    APPROVED = 'APPROVED'
    DISAPPROVED = 'DISAPPROVED'

class CampaignTypeStrEnum(str, Enum):
    UNKNOWN_CAMPAIGN_TYPE = 'UNKNOWN_CAMPAIGN_TYPE'
    GENERIC = 'GENERIC'
    APP_USER_ACQUISITION = 'APP_USER_ACQUISITION'
    APP_REENGAGEMENT = 'APP_REENGAGEMENT'
    WEBSITE_VISIT = 'WEBSITE_VISIT'
    CTV_GENERIC = 'CTV_GENERIC' 
    CTV_APP_USER_ACQUISITION = 'CTV_APP_USER_ACQUISITION'
    WEB_USER_ACQUISITION = 'WEB_USER_ACQUISITION'
    
class DeviceOSStrEnum(str, Enum):
    UNKNOWN_DEVICE_OS = 'UNKNOWN_DEVICE_OS'
    ANDROID = 'ANDROID'
    IOS = 'IOS' 
    VERSATILE = 'VERSATILE'
    MOBILE_WEB = 'MOBILE_WEB'
    
class CampaignStateStrEnum(str, Enum):
    UNKNOWN_CAMPAIGN_STATE = 'UNKNOWN_CAMPAIGN_STATE'
    SUBMITTED = 'SUBMITTED'
    READY = 'READY'
    UPCOMING = 'UPCOMING'
    ACTIVE = 'ACTIVE'
    PAUSED = 'PAUSED'
    SUSPENDED = 'SUSPENDED'
    VIOLATED = 'VIOLATED'
    COMPLETED = 'COMPLETED'

###### Enums ######
    

    
###### Moloco Entities ######

class Image(BaseModel):
    filename: str

class Video(BaseModel):
    filename: str
    auto_endcard: bool

class TrackingLink(BaseModel):
    id: str
    title: str
    description: str
    device_os: DeviceOSStrEnum
    url: str # placeholder for click_through_link / view_through_link
    # click_through_link: ClickThroughLink Object
    # view_through_link: ViewThroughLink Object

class Product(BaseModel):
    id: str
    title: str
    description: str
    
class AdAccount(BaseModel):
    id: str
    title: str
    description: str
    timezone: str = 'America/Los_Angeles'
    currency: CurrencyStrEnum = CurrencyStrEnum.UNKNOWN_CURRENCY
    created_at: datetime = Field(default_factory=datetime.now) 
    updated_at: datetime = Field(default_factory=datetime.now)
    products: List[Product]

    def update_time(self):
        self.updated_at = datetime.now()

    def add_product(self, product: Product):
        self.products.append(product)

    
class AdGroup(BaseModel):
    id: str
    title: str
    enabling_state: EnablingStateEnum
    creative_group_id: List[str]
    updated_at: datetime = Field(default_factory=datetime.now) 
    # audiece
    # capper
    # user_buckets
    def update_time(self):
        self.updated_at = datetime.now()



class Creative(BaseModel):
    id: str
    title: str
    enabling_state: EnablingStateEnum = EnablingStateEnum.ENABLED
    # advertiser_info: AdvertiserInfo
    type: CreativeTypeStrEnum 
    filename: str # the filename of the image or video
    image: Optional[Image] = None
    video: Optional[Video] = None
    # html: Html Object
    updated_at: datetime = Field(default_factory=datetime.now) 
    def update_time(self):
        self.updated_at = datetime.now()
    

class CreativeGroup(BaseModel):
    id: str
    title: str
    description: str
    enabling_state: EnablingStateEnum = EnablingStateEnum.ENABLED
    creative_ids: List[str]
    status: CreativeGroupStatusStrEnum = CreativeGroupStatusStrEnum.SUBMITTED
    # tracking_link_id: str
    updated_at: datetime = Field(default_factory=datetime.now) 
    impressions: int = 0 # self-defined variable for campaign to pause when hits 10,000
    def update_time(self):
        self.updated_at = datetime.now()

class Campaign(BaseModel):
    id: str
    title: str
    description: str = ''
    enabling_state: EnablingStateEnum = EnablingStateEnum.ENABLED
    # type: CampaignTypeEnum = CampaignTypeEnum.UNKNOWN_CAMPAIGN_TYPE
    # device_os: DeviceOSEnum
    state: CampaignStateStrEnum = CampaignStateStrEnum.PAUSED
    # countries: CountryStrEnum
    # currency: CurrencyStrEnum
    # schedual: Schedual Object (start time and end time) 
    tracking_link_id: str = ''
    # goal: CampaignGoal Object
    updated_at: datetime = Field(default_factory=datetime.now)
    
    groups: List[CreativeGroup] = []
    impressions: Dict[str, int] = {} # {group id: num of impression}
    
    def update_time(self):
        self.updated_at = datetime.now()

    def change_state(self, new_state: CampaignStateStrEnum):
        return self.model_copy(update={"state": new_state})

    def activate(self):
        return self.change_state(CampaignStateStrEnum.ACTIVE)
    
    def pause(self):
        return self.change_state(CampaignStateStrEnum.PAUSED)

###### Moloco Entities ######
