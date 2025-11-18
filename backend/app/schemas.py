from pydantic import BaseModel
from typing import Dict

class UserCreate(BaseModel):
    username: str

class ChatRequest(BaseModel):
    user_id: int
    message: str

class ChatResponse(BaseModel):
    reply: str

class MasteryUpdate(BaseModel):
    user_id: int
    topic: str
    status: str

class MasteryResponse(BaseModel):
    mastery: Dict[str, str]
