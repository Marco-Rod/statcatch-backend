from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_ollama import ChatOllama


# Configuracion del motor de base de datos
DB_URL = "postgresql+asyncpg://statcatch_admin:secure_mlb_password_2026@db:5432/statcatch_db"

def get_sql_agent():
    # Conectamos con la bd
    db = SQLDatabase.from_uri(DB_URL)

    # Definimos el cerebro (Ollama)
    llm = ChatOllama(
        model="qwen2.5-coder:7b",
        temperature=0  # Temperadura 0 para que no invente sql
    )

    # Creamos el agente
    agent_executor = create_sql_agent(
        llm,
        db=db,
        agent_type="openai-tools",
        verbose=True # para ver en consola como piensa la IA
    )
    return agent_executor



