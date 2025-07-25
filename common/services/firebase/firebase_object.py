from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional

# Abstract base class for Firebase object
class FirebaseObject(ABC, BaseModel):
    id: Optional[str] = None
    
    @staticmethod
    @abstractmethod
    def collection_name():
        pass