from pydantic import BaseModel, Field
from typing import List, Optional

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


class UserToken(BaseModel):
    localId: str
    email: str
    idToken: str
    refreshToken: str
    expiresIn: int
    roles: Optional[List[str]] = Field(default_factory=list)

    class Config:
        extra = "allow"