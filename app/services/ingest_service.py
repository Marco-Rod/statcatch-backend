from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
import logging

from app.clients.mlb_client import MLBStatsClient
from app.models.team import Team
from app.models.player import Player
from app.schemas.team_schema import TeamCreate
from app.schemas.player_schema import MLBPlayerInput, PlayerCreate

# Configuramos un logger básico para ver el progreso en la terminal
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class IngestService:
    def __init__(self):
        self.mlb_client = MLBStatsClient()

    async def ingest_teams(self, session: AsyncSession, season: int) -> dict:
        """Extrae, transforma y carga (ETL) masivamente los equipos de una temporada."""
        logger.info(f"Iniciando descarga de equipos para la temporada {season}...")
        
        # 1. EXTRACT: Consumir API externa a través de nuestro cliente
        raw_teams = await self.mlb_client.fetch_teams(season=season)
        
        # 2. TRANSFORM: Filtrar y validar con Pydantic
        teams_to_insert = []
        for raw_data in raw_teams:
            try:
                # Validamos el JSON usando la estructura anidada del nuevo TeamCreate
                valid_team = TeamCreate(**raw_data)
                
                # Aplanamos el objeto para cumplir con las columnas de SQLAlchemy/PostgreSQL
                team_dict = {
                    "id": valid_team.id,
                    "name": valid_team.teamName,
                    "team_name": valid_team.teamName,
                    "location": valid_team.locationName,
                    "sport_id": valid_team.sport.id,  # Extraemos el ID del sub-objeto
                    "league_name": valid_team.league.get("name") if valid_team.league else None
                }
                teams_to_insert.append(team_dict)
            except Exception as e:
                logger.warning(f"Error transformando equipo individual: {e}")
                continue

        # 3. LOAD: Inserción masiva en PostgreSQL
        if not teams_to_insert:
            logger.warning("No se generaron diccionarios de equipos válidos para insertar.")
            return {"status": "warning", "message": "No se encontraron equipos válidos."}

        # Construimos la sentencia de inserción masiva
        stmt = insert(Team).values(teams_to_insert)
        
        # Evitamos errores si el ID del equipo ya existe (Upsert pasivo)
        stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
        
        await session.execute(stmt)
        await session.commit()
        
        logger.info(f"Se procesaron {len(teams_to_insert)} equipos con éxito en la base de datos.")
        return {"status": "success", "inserted_count": len(teams_to_insert)}

    async def ingest_players(self, session: AsyncSession, season: int) -> dict:
        """Extrae, transforma y carga masivamente los jugadores de una temporada."""
        logger.info(f"Iniciando descarga de jugadores para la temporada {season}...")
        
        # 1. EXTRACT
        raw_players = await self.mlb_client.fetch_players_by_season(season=season)
        
        # 2. TRANSFORM
        players_to_insert = []
        for raw_data in raw_players:
            try:
                # Primero, atrapamos la estructura anidada con el esquema Input actualizado
                player_input = MLBPlayerInput(**raw_data)
                t_id = None
                if player_input.currentTeam and hasattr(player_input.currentTeam, 'id'):
                    t_id = player_input.currentTeam.id

                # Luego, la aplanamos hacia el esquema que hace match con la BD
                clean_player = PlayerCreate(
                    id=player_input.id,
                    full_name=player_input.fullName,
                    birth_date=player_input.birthDate,
                    current_age=player_input.currentAge,
                    height=player_input.height,
                    weight=player_input.weight,
                    active=player_input.active,
                    bat_side=player_input.batSide.code if player_input.batSide else None,
                    throw_hand=player_input.pitchHand.code if player_input.pitchHand else None,
                    primary_position=player_input.primaryPosition.name if player_input.primaryPosition else None,
                    position_abbreviation=player_input.primaryPosition.abbreviation if player_input.primaryPosition else None,
                    # Ahora sí vinculamos el ID del equipo directamente
                    team_id=t_id
                )
                if clean_player.team_id is None:
                    print(f"DEBUG: Jugador {player_input.fullName} quedó con team_id None")
                players_to_insert.append(clean_player.model_dump())
            except Exception as e:
                # Ignoramos registros silenciosamente en el ETL si vienen muy rotos
                continue

        # 3. LOAD
        if not players_to_insert:
            logger.warning("No se generaron diccionarios de jugadores válidos para insertar.")
            return {"status": "warning", "message": "No se encontraron jugadores válidos."}

        # Dividimos en pedazos de 1000 por buena práctica de arquitectura de datos
        batch_size = 1000
        for i in range(0, len(players_to_insert), batch_size):
            batch = players_to_insert[i:i + batch_size]
            stmt = insert(Player).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
            await session.execute(stmt)
            
        await session.commit()
        
        logger.info(f"Se procesaron {len(players_to_insert)} jugadores con éxito en la base de datos.")
        return {"status": "success", "inserted_count": len(players_to_insert)}

    async def full_season_ingest(self, session: AsyncSession, season: int) -> dict:
        """
        Función maestra que coordina la ingesta en el orden correcto 
        para garantizar la integridad de las llaves foráneas.
        """
        logger.info(f"Iniciando flujo completo (Full Sync) para la temporada {season}...")
        
        # 1. Primero, cargar equipos obligatoriamente para poblar el catálogo de llaves
        teams_result = await self.ingest_teams(session, season)
        
        # 2. Luego, cargar jugadores que apuntarán a esos equipos
        players_result = await self.ingest_players(session, season)
        
        return {
            "status": "success",
            "message": "Datos de equipos y jugadores sincronizados correctamente.",
            "teams_summary": teams_result,
            "players_summary": players_result
        }