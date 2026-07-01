from pydantic import BaseModel, Field
from typing import Optional

class SportBrief(BaseModel):
    id: int

class TeamCreate(BaseModel):
    """
    Modelo robusto para equipos. 
    Mapeamos los campos que vienen del JSON real de la API de la MLB.
    """
    id: int
    teamName: str
    locationName: str
    # Capturamos el objeto sport y luego extraemos su ID
    sport: SportBrief 
    league: Optional[dict] = None # Opcional por si no viene en algún endpoint

    class Config:
        # Esto permite que Pydantic maneje los nombres tal cual vienen del JSON
        populate_by_name = True

    # Propiedad para facilitar el acceso al ID del deporte
    @property
    def sport_id(self) -> int:
        return self.sport.id