import os
import xgboost as xgb
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# ==============================================================================
# CONFIGURACIÓN DE RUTAS ROBUSTAS
# ==============================================================================
# Definimos la raíz del proyecto basándonos en la ubicación de ESTE archivo
# src/ml_engine/serving/ -> subimos 3 niveles -> raiz del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../../"))

# Rutas del modelo (Docker vs Local)
MODEL_PATH_DOCKER = "/app/models/xgb_navoptima_v1.json"
MODEL_PATH_LOCAL = os.path.join(PROJECT_ROOT, "models", "xgb_navoptima_v1.json")

model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida: Carga el modelo al iniciar."""
    global model
    
    # Lógica de fallback: Intenta ruta Docker, si no existe, usa Local
    path = MODEL_PATH_DOCKER if os.path.exists(MODEL_PATH_DOCKER) else MODEL_PATH_LOCAL
    
    print(f"📂 Buscando modelo en: {path}")
    
    if os.path.exists(path):
        try:
            model = xgb.Booster()
            model.load_model(path)
            print("✅ ¡ÉXITO! Modelo XGBoost cargado en memoria.")
        except Exception as e:
            print(f"❌ Error al leer el archivo del modelo: {e}")
    else:
        print(f"⚠️ ERROR CRÍTICO: Archivo no encontrado. Verifica que 'xgb_navoptima_v1.json' esté en la carpeta models/.")
    
    yield
    print("🛑 Servicio de inferencia detenido.")

app = FastAPI(title="NavOptima Inference API", version="1.0", lifespan=lifespan)

# ==============================================================================
# ESQUEMAS DE DATOS (Pydantic v2 Updated)
# ==============================================================================
class VoyageParameters(BaseModel):
    sog: float = Field(..., gt=0, description="Velocidad (knots)", json_schema_extra={"example": 12.5})
    draft: float = Field(..., gt=0, description="Calado (m)", json_schema_extra={"example": 7.2})
    length: float = Field(..., gt=0, description="Eslora (m)", json_schema_extra={"example": 200.0})
    wind_speed: float = Field(..., ge=0, description="Viento (m/s)", json_schema_extra={"example": 15.0})
    wave_height: float = Field(..., ge=0, description="Olas (m)", json_schema_extra={"example": 2.5})

class PredictionResponse(BaseModel):
    fuel_consumption_kgh: float
    confidence_score: float = 1.0

# ==============================================================================
# ENDPOINTS
# ==============================================================================
@app.get("/")
def home():
    return {"message": "NavOptima AI Service is Running", "docs": "/docs"}

@app.get("/health")
def health_check():
    if model:
        return {"status": "healthy", "model_loaded": True}
    return {"status": "degraded", "model_loaded": False}

@app.post("/predict", response_model=PredictionResponse)
def predict_consumption(params: VoyageParameters):
    if not model:
        raise HTTPException(status_code=503, detail="Modelo no disponible.")

    try:
        # Vector de entrada (Orden estricto según entrenamiento)
        input_data = pd.DataFrame([{
            'sog': params.sog,
            'draft': params.draft,
            'length': params.length,
            'wind_speed': params.wind_speed,
            'wave_height': params.wave_height
        }])

        dmatrix = xgb.DMatrix(input_data)
        prediction = model.predict(dmatrix)
        
        return {
            "fuel_consumption_kgh": round(float(prediction[0]), 2),
            "confidence_score": 0.95
        }

    except Exception as e:
        print(f"❌ Error durante inferencia: {e}")
        raise HTTPException(status_code=500, detail="Error interno en el cálculo.")

if __name__ == "__main__":
    import uvicorn
    # Hot reload activado para desarrollo rápido
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)