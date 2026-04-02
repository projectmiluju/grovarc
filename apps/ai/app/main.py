from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import connect_all, disconnect_all
from app.kafka.consumer import start_consumer, stop_consumer
from app.routers import agent, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_all()
    await start_consumer()
    yield
    await stop_consumer()
    await disconnect_all()


app = FastAPI(
    title="Grovarc AI Server",
    description="LangGraph Agent 기반 AI 분석 서버",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(agent.router)
