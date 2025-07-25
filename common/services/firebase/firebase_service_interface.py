from abc import ABC, abstractmethod
from typing import List, Type, Optional
from google.cloud.firestore_v1.base_query import FieldFilter
from common.services.firebase.firebase_object import FirebaseObject

# Abstract base class for Firebase service
class FirebaseServiceInterface(ABC):

    @abstractmethod
    def add(self, obj: FirebaseObject) -> str:
        pass

    @abstractmethod
    def delete(self, collection_name: str, document_id: str):
        pass

    @abstractmethod
    def fetch_all(self, model_class: Type[FirebaseObject], filters: Optional[List[FieldFilter]] = None) -> List[FirebaseObject]:
        pass

    @abstractmethod
    def fetch_by_id(self, model_class: Type[FirebaseObject], doc_id: str) -> FirebaseObject:
        pass

    @abstractmethod
    def update(self, id: str, obj: FirebaseObject) -> FirebaseObject:
        pass

    @abstractmethod
    def close_db(self):
        pass
