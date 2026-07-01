from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.player import Player
from app.models.team import Team
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/query", tags=["Consulta de Datos"])

@router.get("/players")
async def get_players(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Consulta paginada de jugadores. 
    Por defecto trae los primeros 50 registros.
    """
    # Construimos la query
    stmt = select(Player).offset(skip).limit(limit)
    result = await db.execute(stmt)
    players = result.scalars().all()
    
    return {
        "total_requested": len(players),
        "data": players
    }

@router.get("/debug-teams")
async def debug_teams(db: AsyncSession = Depends(get_db)):
    # Traemos todos los jugadores y vemos si tienen team_id
    stmt = select(Player)
    result = await db.execute(stmt)
    players = result.scalars().all()
    
    return [{"name": p.full_name, "team_id_in_db": p.team_id} for p in players]

@router.get("/debug-raw-json")
async def debug_raw(db: AsyncSession = Depends(get_db)):
    # Traeremos UN jugador de la BD para ver su estructura (si la guardamos)
    # O mejor aún, hagamos una llamada rápida desde el servicio
    from app.clients.mlb_client import MLBStatsClient
    client = MLBStatsClient()
    data = await client.fetch_players_by_season(season=2026)
    return data[0] # Nos devuelve el JSON del primer jugador para inspeccionarlo


@router.get("/debug-teams-json")
async def debug_teams_json():
    from app.clients.mlb_client import MLBStatsClient
    client = MLBStatsClient()
    # Probemos con parámetros más abiertos
    return await client.fetch_teams(season=2026)


@router.get("/verify-raw-data")
async def verify_raw_data(db: AsyncSession = Depends(get_db)):
    """
    Esto ignora las relaciones de SQLAlchemy y mira si la columna team_id 
    realmente tiene números dentro de la tabla de jugadores.
    """
    stmt = select(Player.id, Player.full_name, Player.team_id).limit(20)
    result = await db.execute(stmt)
    return [{"id": row[0], "name": row[1], "team_id": row[2]} for row in result.all()]


@router.get("/players-with-team")
async def get_players_with_teams(db: AsyncSession = Depends(get_db)):
    # Usamos selectinload para decirle a SQLAlchemy: 
    # "Trae los jugadores Y ADEMÁS carga la información de sus equipos relacionados"
    stmt = select(Player).options(selectinload(Player.team))
    result = await db.execute(stmt)
    players = result.scalars().all()
    
    # Ahora 'p.team' no será None
    return [{"name": p.full_name, "team": p.team.name if p.team else "Sin equipo"} for p in players]



@router.get("/verify-teams")
async def verify_teams(db: AsyncSession = Depends(get_db)):
    """Verifica cuántos equipos hay realmente en la base de datos."""
    stmt = select(Team)
    result = await db.execute(stmt)
    teams = result.scalars().all()
    return {"total_teams": len(teams), "teams": [{"id": t.id, "name": t.name} for t in teams]}


@router.get("/compare-ids")
async def compare_ids(db: AsyncSession = Depends(get_db)): # <- Aquí estaba el error
    # Trae 5 jugadores y mira su team_id, luego trae los equipos disponibles
    players_stmt = select(Player.full_name, Player.team_id).limit(5)
    teams_stmt = select(Team.id, Team.name).limit(5)
    
    p_result = await db.execute(players_stmt)
    t_result = await db.execute(teams_stmt)
    
    return {
        "players": [{"name": r[0], "team_id": r[1]} for r in p_result.all()],
        "teams_in_db": [{"id": r[0], "name": r[1]} for r in t_result.all()]
    }