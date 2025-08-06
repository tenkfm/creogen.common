from enum import Enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from common.services.firebase.firebase_object import FirebaseObject

class TTExport(FirebaseObject):
    user_id: Optional[str] = None
    publication_id: Optional[str] = None
    campaign_name: str
    ad_groups_count: int
    pixel_id: str
    pixel_event: str
    locations: List[str]
    languages: List[str]
    budget: float
    bid: float
    identity_id: str
    text: str
    url: str
    event_name: str
    
    @staticmethod
    def collection_name():
        return "tt_exports"