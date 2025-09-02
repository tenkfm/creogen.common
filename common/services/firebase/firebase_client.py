import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client as FirestoreClient

_client: FirestoreClient | None = None

def get_client(api_key: str | None = None, database_id: str | None = None) -> FirestoreClient:
    """
    Возвращает singleton Firestore клиента для текущего процесса.
    Если клиента ещё нет — инициализирует его.
    """
    global _client
    if _client is not None:
        return _client

    # Инициализация Firebase App (один раз на процесс)
    if not firebase_admin._apps:
        if not api_key:
            raise RuntimeError("Firebase API key JSON is required on first init")
        cred_dict = json.loads(api_key)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

    _client = firestore.client(database_id=database_id)
    return _client


def close_client():
    """
    Корректно закрывает Firestore клиента (гасим gRPC-пулы).
    """
    global _client
    if _client is not None:
        _client._transport.close()  # закрыть underlying gRPC channel
        _client = None
