from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.sql_agent import get_sql_agent


router = APIRouter(prefix="/ai", tags=["Agente IA"])

class QueryRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_agent(request: QueryRequest):
    """
    Envia una pregunta en lenguaje natural al agente SQL
    """
    try:
        agent = get_sql_agent()
        # Invocamos al agente con la pregunta del usuario
        response = agent.involke({"input": request.question})
        return {"answer": response["output"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el agente: {str(e)}")

