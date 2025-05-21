from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "viewer"

class User(UserBase):
    id: int
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)

class DocumentBase(BaseModel):
    title: str

class DocumentCreate(DocumentBase):
    pass # Will handle file upload separately

class Document(DocumentBase):
    id: int
    filename: str
    upload_time: datetime
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserRoleUpdate(BaseModel):
    role: str

class QuestionRequest(BaseModel):
    question: str

class IngestionTask(BaseModel):
    document_id: int
    status: str = "pending" # pending, processing, completed, failed
    message: Optional[str] = None
# Roo temp change 7