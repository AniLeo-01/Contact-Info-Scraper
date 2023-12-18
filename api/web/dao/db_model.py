from sqlmodel import SQLModel, Field, DateTime, Column, ForeignKey, JSON
from typing import Optional, List
from datetime import datetime
from pgvector.sqlalchemy import Vector
from uuid import UUID

class Query(SQLModel, table=True):
    id: int = Field(default = None, primary_key=True)
    query: str = Field(default=None, nullable=False)

    created_on: datetime = Field(default_factory=datetime.utcnow)
    modified_on: Optional[datetime] = Field(
        sa_column=Column(
            "modified_on",
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
        )
    )

class URL(SQLModel, table=True):
    id: int = Field(default = None, primary_key=True)
    url: str
    query_id: int = Field(ForeignKey("query.id", onupdate="CASCADE"))

class Leads(SQLModel, table=True):
    id: int = Field(default = None, primary_key=True)
    email: Optional[str]
    phone: Optional[str]
    url: str

class Documents_URL(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    content: str
    embedding: List[float] = Field(sa_column=Column(Vector(1536)))
    document_metadata: Optional[dict] = Field(default=None, alias='metadata', sa_column=Column(JSON))
    url_id: Optional[int] = Field(ForeignKey("url.id", onupdate="CASCADE"))