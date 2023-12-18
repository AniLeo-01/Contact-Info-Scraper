from fastapi import FastAPI
from api.web.controllers.controllers import scraper_router
from api.web.db import disconnect_db, init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Scraper API started.....")
    await init_db()
    yield
    print("Scraper API shutdown....")
    await disconnect_db()

app = FastAPI(title = "Contact Info Scraper", version = "1.0.0", lifespan=lifespan)

# @app.on_event("startup")
# async def on_startup():
#     print("Scraper API started.....")
#     await init_db()

# @app.on_event("shutdown")
# async def shutdown():
#     print("Scraper API shutdown....")
#     await disconnect_db()

app.include_router(scraper_router, tags=[''])