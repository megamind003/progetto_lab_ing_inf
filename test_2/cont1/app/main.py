from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
import os
import asyncio
from sqlalchemy.sql import select 

DATABASE_URL = os.getenv("DB_URL", "postgresql+asyncpg://user:password@db:5432/mydb")
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String)

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await asyncio.sleep(2)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/items")
async def get_items():
    async with async_session() as session:
        result = await session.execute(select(Item))
        items = result.scalars().all()
        return {"items": [item.name for item in items]}
    
    
@app.post("/items/{name}")
async def create_item(name: str):
    async with async_session() as session:
        new_item = Item(name=name)
        session.add(new_item)
        await session.commit()
        return {"status": "item created"}