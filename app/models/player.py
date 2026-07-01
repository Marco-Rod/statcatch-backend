from sqlalchemy import Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from typing import Optional
from app.core.database import Base

class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    current_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    weight: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Datos técnicos

    bat_side: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    throw_hand: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    primary_position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    position_abbreviation: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)


    # Relación con el Equipo (Llave Foránea)
    team_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    # Relación SQLAlchemy
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="players")