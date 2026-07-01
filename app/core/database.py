from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# 1. Crear el motor asincrono

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True, # Util para ver el SQL en la terminal durante desarrollo
    future=True
)

# 2. Crear la fabrica de sesiones asincronas

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Clase base para que nuestros modelos hereden de ella

class Base(DeclarativeBase):
    pass

# 4. Dependencia que usaremos en los endpoints de FastAPI

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()