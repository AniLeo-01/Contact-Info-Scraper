from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..dto.request_model import CreateQuery
from ..services import services
import asyncio

scraper_router = APIRouter()

@scraper_router.post('/query', tags = ['Scraper'])
async def create_search_query(data: CreateQuery, session: AsyncSession = Depends(get_session)):
    try:
        
        return await asyncio.gather(services.scrape_data_to_json(data, session))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@scraper_router.get('/query', tags = ['Scraper'])
async def get_all_queries(session: AsyncSession = Depends(get_session)):
    try:
        return await services.get_all_user_queries(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail="No query found")