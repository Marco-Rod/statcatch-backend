from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.ingest_service import IngestService

router = APIRouter(prefix="/ingest", tags=["Ingesta de Datos"])
ingest_service = IngestService()

@router.post("/teams")
async def ingest_teams_data(
    season: int = Query(2026, description="Temporada a consultar"),
    db: AsyncSession = Depends(get_db)
):
    """Dispara la ingesta masiva de equipos."""
    try:
        result = await ingest_service.ingest_teams(session=db, season=season)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la ingesta: {str(e)}")

@router.post("/players")
async def ingest_players_data(
    season: int = Query(2026, description="Temporada a consultar"),
    db: AsyncSession = Depends(get_db)
):
    """Dispara la ingesta masiva de jugadores."""
    try:
        result = await ingest_service.ingest_players(session=db, season=season)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la ingesta: {str(e)}")

@router.post("/full-sync")
async def full_sync(
    season: int = Query(2026),
    db: AsyncSession = Depends(get_db)
):
    return await ingest_service.full_season_ingest(session=db, season=season)