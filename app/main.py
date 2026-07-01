from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app.models.team import Team
from app.models.player import Player
from app.api.v1.data_ingest import router as ingest_router
from app.api.v1.data_query import router as query_router
from app.api.v1.ai_query import router as ai_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sistema asíncrono de procesamiento y ETL de estadísticas de la MLB y ligas menores."
)

app.include_router(ingest_router, prefix="/api/v1")
app.include_router(query_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # Crea las tablas si no existen en la BD
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health", tags=["Infrastructure"])
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
