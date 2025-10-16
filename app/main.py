# app/main.py

from fastapi import FastAPI, HTTPException
from typing import List

# Importamos los modelos de datos y la lógica principal
from .models import Payload
from .logic import calcular_plan_produccion

# Esta es la línea clave que probablemente faltaba o estaba comentada
app = FastAPI(
    title="ENGIE Production Plan API",
    description="Una API para calcular el plan de producción óptimo para un conjunto de centrales eléctricas.",
    version="1.0.0"
)

# Definimos el endpoint que recibirá las peticiones POST
@app.post("/productionplan", response_model=List[dict])
def create_production_plan(payload: Payload):
    """
    Calcula el plan de producción para una carga y un conjunto de centrales eléctricas.
    """
    try:
        # Llamamos a nuestra función orquestadora del 'logic.py'
        response_data = calcular_plan_produccion(payload)
        return response_data

    except Exception as e:
        # Capturamos cualquier error inesperado
        print(f"Error inesperado durante el cálculo: {e}")
        # Devolvemos un error HTTP 500
        raise HTTPException(
            status_code=500,
            detail=f"Ha ocurrido un error interno al procesar el plan de producción: {e}"
        )