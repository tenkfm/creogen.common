# common/services/firebase/claims.py

from typing import Dict, List, Any
from firebase_admin import auth
import requests

def _merge_claims(current: Dict[str, Any] | None, patch: Dict[str, Any]) -> Dict[str, Any]:
    current = current or {}
    merged = current.copy()
    for k, v in patch.items():
        if isinstance(v, list):
            merged[k] = sorted(set([*(merged.get(k, []) or []), *v]))
        elif isinstance(v, dict):
            merged[k] = {**(merged.get(k, {}) or {}), **v}
        else:
            merged[k] = v
    return merged

def ensure_baseline_roles(uid: str, baseline: List[str] = ["user"]) -> Dict[str, Any]:
    """
    Guarantees that the user has roles:["user"] (or other baseline roles).
    """
    user = auth.get_user(uid)
    current = user.custom_claims or {}
    roles = set(current.get("roles", []))
    need_update = False
    for r in baseline:
        if r not in roles:
            need_update = True
            roles.add(r)
    if need_update:
        new_claims = _merge_claims(current, {"roles": sorted(roles)})
        auth.set_custom_user_claims(uid, new_claims)
        return new_claims
    return current

def set_claims(uid: str, claims: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full set/overwrite of custom claims (use with caution).
    """
    auth.set_custom_user_claims(uid, claims)
    return claims

def refresh_id_token(api_key: str, refresh_token: str) -> Dict[str, Any]:
    """
    Refreshes the ID token using the Secure Token API.
    
    """
    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    # IMPORTANT: Content-Type x-www-form-urlencoded
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    r = requests.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    if r.status_code != 200:
        raise RuntimeError(f"SecureToken refresh failed: {r.status_code} {r.text}")
    return r.json()
