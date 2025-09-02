import json
import threading
from typing import List, Type, Optional, Dict

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from common.services.firebase.firebase_service_exception import FirebaseServiceException
from common.services.firebase.firebase_service_interface import FirebaseServiceInterface
from common.services.firebase.firebase_object import FirebaseObject

# ==== Глобальные синглтоны (на ПРОЦЕСС) ======================================
# Один firebase_app и один(и) firestore client на database_id для текущего процесса воркера.
_init_lock = threading.Lock()
_firebase_app_inited = False
_db_by_id: Dict[str, firestore.Client] = {}

def _ensure_firebase_app(api_key: str) -> None:
    """
    Инициализировать firebase_admin один раз на процесс.
    Без повторной регистрации приложений (иначе плодятся внутренние ресурсы/gRPC).
    """
    global _firebase_app_inited
    if _firebase_app_inited:
        return
    with _init_lock:
        if _firebase_app_inited:
            return
        if not firebase_admin._apps:
            cred_dict = json.loads(api_key)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        _firebase_app_inited = True

def _get_db(database_id: str) -> firestore.Client:
    """
    Вернуть/создать один firestore client на процесс и database_id.
    """
    if database_id in _db_by_id:
        return _db_by_id[database_id]
    with _init_lock:
        cli = _db_by_id.get(database_id)
        if cli is not None:
            return cli
        cli = firestore.client(database_id=database_id)
        _db_by_id[database_id] = cli
        return cli
# =============================================================================


# Firebase service implementation
class FirebaseService(FirebaseServiceInterface):
    def __init__(self, api_key: str, database_id: str):
        # Инициализируем firebase_admin ОДИН раз и берём общий client для процесса
        _ensure_firebase_app(api_key=api_key)
        self.database_id = database_id
        self.db = _get_db(database_id=database_id)

    # ---- CRUD ---------------------------------------------------------------

    def add(self, obj: FirebaseObject) -> FirebaseObject:
        try:
            collection_ref = self.db.collection(obj.collection_name())
            _, doc_ref = collection_ref.add(obj.model_dump(exclude_unset=True))
            obj.id = doc_ref.id
            return obj
        except Exception as e:
            raise FirebaseServiceException(f"Failed to add document to {obj.collection_name()}: {str(e)}")

    def add_with_doc_id(self, doc_id: str, obj: FirebaseObject) -> FirebaseObject:
        try:
            collection_ref = self.db.collection(obj.collection_name()).document(doc_id)
            collection_ref.set(obj.model_dump(exclude_unset=True))
            return obj
        except Exception as e:
            raise FirebaseServiceException(f"Failed to add document to {obj.collection_name()}: {str(e)}")

    def delete(self, model_class: Type[FirebaseObject], doc_id: str):
        try:
            collection_ref = self.db.collection(model_class.collection_name())
            doc_ref = collection_ref.document(doc_id)
            doc_ref.delete()
        except Exception as e:
            raise FirebaseServiceException(f"Failed to delete document: {str(e)}")

    def fetch_all(self, model_class: Type[FirebaseObject], filters: Optional[List[FieldFilter]] = None) -> List[FirebaseObject]:
        try:
            collection_ref = self.db.collection(model_class.collection_name())
            if filters:
                q = collection_ref
                for f in filters:
                    q = q.where(filter=f)
                documents = q.stream()
            else:
                documents = collection_ref.stream()

            objects: List[FirebaseObject] = []
            for doc in documents:
                data = doc.to_dict()
                data["id"] = doc.id
                objects.append(model_class(**data))
            return objects
        except Exception as e:
            raise FirebaseServiceException(f"Error fetching documents from {model_class.collection_name()}: {str(e)}")

    def fetch_by_id(self, model_class: Type[FirebaseObject], doc_id: str) -> Optional[FirebaseObject]:
        try:
            doc_ref = self.db.collection(model_class.collection_name()).document(doc_id)
            doc = doc_ref.get()
            if not doc.exists:
                return None
            data = doc.to_dict()
            data["id"] = doc.id
            return model_class(**data)
        except Exception as e:
            raise FirebaseServiceException(f"Error fetching document from {model_class.collection_name()}: {e}")

    def fetch_one(self, model_class: Type[FirebaseObject], filters: Optional[List[FieldFilter]]) -> Optional[FirebaseObject]:
        objects = self.fetch_all(model_class=model_class, filters=filters)
        if not objects:
            return None
        if len(objects) != 1:
            raise FirebaseServiceException(f"Expected one document, but found {len(objects)} in {model_class.collection_name()}.")
        return objects[0]

    def update(self, id: str, obj: FirebaseObject) -> FirebaseObject:
        try:
            doc_ref = self.db.collection(obj.collection_name()).document(id)
            data = obj.model_dump(exclude_unset=True)
            doc_ref.set(data, merge=True)
            data["id"] = id
            return data
        except Exception as e:
            raise FirebaseServiceException(f"Error updating document with ID {id}: {str(e)}")

    def add_to_subcollection(self, parent_collection: Type[FirebaseObject], parent_id: str, obj: FirebaseObject) -> str:
        try:
            parent_ref = self.db.collection(parent_collection.collection_name()).document(parent_id)
            subcol_ref = parent_ref.collection(obj.collection_name())
            _, doc_ref = subcol_ref.add(obj.model_dump(exclude_unset=True))
            return doc_ref.id
        except Exception as e:
            raise FirebaseServiceException(
                f"Adding subcollection failure {obj.collection_name()} "
                f"document {parent_collection.collection_name()}/{parent_id}: {e}"
            )

    def batch_add(self, objs: List[FirebaseObject]) -> List[FirebaseObject]:
        try:
            batch = self.db.batch()
            updated_objs: List[FirebaseObject] = []
            for obj in objs:
                collection_ref = self.db.collection(obj.collection_name())
                doc_ref = collection_ref.document()
                batch.set(doc_ref, obj.model_dump(exclude_unset=True))
                obj.id = doc_ref.id
                updated_objs.append(obj)
            batch.commit()
            return updated_objs
        except Exception as e:
            raise FirebaseServiceException(f"Batch add failed: {str(e)}")

    def batch_update(self, objs: List[FirebaseObject]) -> List[FirebaseObject]:
        try:
            batch = self.db.batch()
            updated_objs: List[FirebaseObject] = []
            for obj in objs:
                if not obj.id:
                    raise FirebaseServiceException("Each object must have an ID for batch update.")
                doc_ref = self.db.collection(obj.collection_name()).document(obj.id)
                batch.set(doc_ref, obj.model_dump(exclude_unset=True), merge=True)
                updated_objs.append(obj)
            batch.commit()
            return updated_objs
        except Exception as e:
            raise FirebaseServiceException(f"Batch update failed: {str(e)}")

    def batch_delete(self, model_class: Type[FirebaseObject], doc_ids: List[str]) -> None:
        try:
            batch = self.db.batch()
            for doc_id in doc_ids:
                doc_ref = self.db.collection(model_class.collection_name()).document(doc_id)
                batch.delete(doc_ref)
            batch.commit()
        except Exception as e:
            raise FirebaseServiceException(f"Batch delete failed: {str(e)}")

    def close_db(self):
        """
        Ничего не делаем. Клиент общий для процесса и закрывается
        при остановке воркера (если добавишь хуки Celery).
        """
        pass
