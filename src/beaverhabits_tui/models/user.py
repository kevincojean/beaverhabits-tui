from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    is_active: bool = True
    is_verified: bool = False
