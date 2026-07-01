from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.agent_toolkits import create_sql_agent
from langchain_ollama import ChatOllama
from sqlalchemy import create_engine


# Configuracion del motor de base de datos
SYNC_DB_URL = "postgresql+psycopg2://statcatch_admin:secure_mlb_password_2026@db:5432/statcatch_db"

def get_sql_query_chain():
    # Motor síncrono
    engine = create_engine(SYNC_DB_URL)
    db = SQLDatabase(engine, include_tables=['players', 'teams'])
    
    # Cerebro
    llm = ChatOllama(
        model="qwen2.5-coder:7b",
        base_url="http://host.docker.internal:11434",
        temperature=0
    )
    
    # Chain simple: Convierte pregunta -> SQL
    chain = create_sql_query_chain(llm, db)
    return chain, db
