from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# --- Sub-modelos para la anidación del JSON de la MLB ---

class TeamBrief(BaseModel):
    id: int # Este es el team_id que buscamos

class BatSide(BaseModel):
    code: str

class PitchHand(BaseModel):
    code: str

class PrimaryPosition(BaseModel):
    name: str
    abbreviation: str

# --- Esquema de entrada (Raw Data de la MLB) ---

class MLBPlayerInput(BaseModel):
    """Atrapa el JSON crudo y fuertemente anidado de la MLB"""
    id: int
    fullName: str
    birthDate: Optional[date] = None
    currentAge: Optional[int] = None
    height: Optional[str] = None
    weight: Optional[int] = None
    active: bool
    batSide: Optional[BatSide] = None
    pitchHand: Optional[PitchHand] = None
    primaryPosition: Optional[PrimaryPosition] = None
    currentTeam: Optional[TeamBrief] = None # Capturamos el objeto del equipo

# --- Esquema de salida (Clean Data para PostgreSQL) ---

class PlayerCreate(BaseModel):
    """Datos aplanados y limpios, listos para SQLAlchemy"""
    id: int
    full_name: str
    birth_date: Optional[date] = None
    current_age: Optional[int] = None
    height: Optional[str] = None
    weight: Optional[int] = None
    active: bool
    bat_side: Optional[str] = None
    throw_hand: Optional[str] = None
    primary_position: Optional[str] = None
    position_abbreviation: Optional[str] = None
    team_id: Optional[int] = None