from pydantic import BaseModel
from typing import Optional

class SignupRequest(BaseModel):
    username: str
    password: str = ""
    role: str = "patient" 