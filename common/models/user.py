from pydantic import BaseModel, Field

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

    class Config:
        extra = "allow"