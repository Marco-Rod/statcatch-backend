from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Team(Base):
    __tablename__ = "teams"

    # ID real de la MLB como llave primaria
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    team_name: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    sport_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    league_name: Mapped[str] = mapped_column(String(50), nullable=True)

    # Relación inversa: Un equipo tiene muchos jugadores

    players: Mapped[list["Player"]] = relationship("Player", back_populates="team", cascade="all, delete-orphan")