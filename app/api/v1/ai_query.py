from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.sql_agent import get_sql_query_chain

router = APIRouter(prefix="/ai", tags=["Agente IA"])

class QueryRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_agent(request: QueryRequest):
    try:
        chain, db = get_sql_query_chain()
        
        # 1. Generar SQL
        sql = chain.invoke({"question": request.question})
        
        # 2. Limpiar el SQL (por si el modelo incluye ```sql ... ```)
        clean_sql = sql.replace("```sql", "").replace("```", "").strip()
        
        # 3. Ejecutar en la base de datos
        result = db.run(clean_sql)
        
        return {
            "question": request.question,
            "sql_generated": clean_sql,
            "answer": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))