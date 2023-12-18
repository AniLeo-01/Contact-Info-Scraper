import uuid
from pydantic import BaseModel, Field, json
from typing import Optional, List

class CreateQuery(BaseModel):
    id: Optional[int]
    query: str = Field(default=None, nullable=False, example="Villas in Santa Teresa Costa Rica")
    query_num: Optional[int] = Field(default=10, nullable=False, example=10)
    exceptionFilters: Optional[List[str]] = Field(default=None, nullable=False, example=["airbnb.com", "booking.com"])

    class Config:
        orm_mode = True

class CreateDocument(BaseModel):
    id: Optional[int]
    url_id: Optional[int] = Field(default=None, nullable=False)
    text: str
    embedding: Optional[List[float]] = Field(default=None, nullable=False)
    metadata: Optional[str] = Field(default=None, nullable=True)

    class Config:
        orm_mode = True

class CreateDocumentURL(BaseModel):
    id: Optional[int]
    url_id: Optional[int] = Field(default=None, nullable=False)
    content: str
    document_metadata: Optional[dict] = Field(default=None, nullable=True)
    embedding: Optional[List[float]] = Field(default=None, nullable=False)
    
    class Config:
        orm_mode = True

class CreateURL(BaseModel):
    id: Optional[int]
    url: str
    query_id: int

    class Config:
        orm_mode = True

class CreateLeads(BaseModel):
    id: Optional[int]
    email: Optional[str]
    phone: Optional[str]
    url: Optional[str]

    class Config:
        orm_mode = True

