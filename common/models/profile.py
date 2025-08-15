from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from common.services.firebase.firebase_object import FirebaseObject

class Profile(FirebaseObject):
    id: Optional[str] = None
    email: str
    created_at: str
    heygen_api_key: Optional[str] = None

    @staticmethod
    def collection_name():
        return "profiles"