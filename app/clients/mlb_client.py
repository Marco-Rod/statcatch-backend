import httpx
from typing import List, Dict, Any

class MLBStatsClient:
    """
    Cliente HTTP asíncrono para consumir la API pública de la MLB.
    """
    def __init__(self):
        self.base_url = "https://statsapi.mlb.com/api/v1"
        # Un timeout de 30 segundos es prudente porque los JSONs de la MLB son gigantes
        self.timeout = 30.0

    async def fetch_teams(self, season: int, sport_id: int = 1) -> List[Dict[Any, Any]]:
        url = f"{self.base_url}/teams"
        params = {"season": season, "sportId": sport_id}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Si el JSON tiene la llave "teams", perfecto.
            # Si no, intentemos ver si es una lista directa o un objeto con otra llave.
            if "teams" in data:
                return data["teams"]
            # Si el endpoint devuelve un objeto individual o estructura distinta, 
            # adaptémoslo para que siempre retorne una lista
            return [data] if isinstance(data, dict) and "id" in data else []
            
    async def fetch_players_by_season(self, season: int, sport_id: int = 1) -> List[Dict[Any, Any]]:
        """
        Descarga todos los jugadores registrados en una temporada específica.
        """
        url = f"{self.base_url}/sports/{sport_id}/players"
        params = {
            "season": season
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # La API devuelve los jugadores dentro de una llave llamada "people"
            return data.get("people", [])