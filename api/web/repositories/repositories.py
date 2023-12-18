from ..dao import db_model
from ..dto import request_model
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from sqlalchemy.future import select
from typing import Optional
from sqlalchemy import join, text

async def create_query(
    session: AsyncSession,
    user_query: request_model.CreateQuery
):
    new_query = db_model.Query.from_orm(user_query)
    session.add(new_query)
    await session.commit()
    await session.refresh(new_query)
    return new_query

async def create_url(
    session: AsyncSession,
    url: request_model.CreateURL
):
    new_url = db_model.URL.from_orm(url)
    session.add(new_url)
    await session.commit()
    await session.refresh(new_url)
    return new_url

async def create_contact_info(
    session: AsyncSession,
    contact_info: request_model.CreateLeads
):
    new_contact_info = db_model.Leads.from_orm(contact_info)
    session.add(new_contact_info)
    await session.commit()
    await session.refresh(new_contact_info)
    return new_contact_info

async def get_query_data_by_column(
    session: AsyncSession,
    column: BaseModel,
    value: str
):
    query_statement = select(db_model.Query).where(
        column == value
    )
    execute_query = await session.execute(query_statement)
    response = execute_query.scalars().first()
    return response

async def get_URL_data_by_column(
    session: AsyncSession,
    column: BaseModel,
    value: str
):
    query_statement = select(db_model.URL).where(
        column == value
    )
    execute_query = await session.execute(query_statement)
    response = execute_query.scalars().first()
    return response

async def get_all_queries(
        session: AsyncSession
):
    query = select(db_model.Query, db_model.URL.url) \
        .join(db_model.URL, db_model.Query.id == db_model.URL.query_id)
    # query = select(db_model.Query)
    execute_query = await session.execute(query)
    response = execute_query.scalars().all()
    return response

async def delete_all_documents(
    session: AsyncSession
):
    await session.execute(text("DELETE FROM documents;")) # type: ignore
    await session.commit()

async def get_all_documents(
        session: AsyncSession
):
    execute_query = await session.execute("SELECT * FROM documents;") # type: ignore
    documents = execute_query.all()
    return documents

async def store_documents_url(
        session: AsyncSession,
        document_data: request_model.CreateDocumentURL
):  
    new_document = db_model.Documents_URL.from_orm(document_data)
    session.add(new_document)
    await session.commit()
    await session.refresh(new_document)
    return new_document