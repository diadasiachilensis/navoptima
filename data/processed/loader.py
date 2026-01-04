import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
from datetime import datetime

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================
DB_USER = "nav_user"
DB_PASS = "nav_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "navoptima_warehouse"

# Cadena de conexión SQLAlchemy
DB_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '../../data/processed/df_final_enriched.csv')

# Constantes de Negocio
BUNKER_PRICE_PER_TON = 650.0 # USD (Estimación promedio 2024 para VLSFO)

def get_engine():
    return create_engine(DB_URI)

def load_gold_layer():
    print(f"🚀 Iniciando ETL a Capa Gold: {datetime.now()}")
    
    # 1. EXTRACT (Leer CSV)
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"❌ No se encuentra el archivo: {CSV_PATH}")
    
    print("   📂 Leyendo dataset procesado (esto puede tardar unos segundos)...")
    df = pd.read_csv(CSV_PATH)
    
    # Conversión de tipos críticos
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Limpieza de redondeo para reducir cardinalidad en dimensiones
    df['wind_speed_rounded'] = df['wind_speed'].round(1)
    df['wave_height_rounded'] = df['wave_height'].round(1)

    engine = get_engine()

    with engine.connect() as conn:
        print("   🔌 Conexión a Base de Datos establecida.")

        # ======================================================================
        # 2. DIMENSION: VESSEL TYPES (Look-up)
        # ======================================================================
        print("   🏗️ Gestionando Dimensión: Tipos de Buques...")
        # Como no tenemos el tipo en el CSV, aseguramos que exista 'Unknown'
        conn.execute(text("""
            INSERT INTO gold_navoptima.dim_vessel_types (type_name) 
            VALUES ('Unknown') 
            ON CONFLICT (type_name) DO NOTHING;
        """))
        conn.commit()
        
        # Recuperamos el ID para usarlo
        type_id_unknown = conn.execute(text(
            "SELECT vessel_type_id FROM gold_navoptima.dim_vessel_types WHERE type_name = 'Unknown'"
        )).scalar()

        # ======================================================================
        # 3. DIMENSION: WEATHER METRICS (Deduplicación)
        # ======================================================================
        print("   ☁️ Gestionando Dimensión: Métricas Climáticas...")
        
        # Extraemos combinaciones únicas de viento/olas para no inflar la tabla
        weather_df = df[['wind_speed_rounded', 'wave_height_rounded']].drop_duplicates()
        weather_df.columns = ['wind_speed_ms', 'wave_height_m']
        weather_df['weather_category'] = 'Measured' # Placeholder

        # Inserción masiva ignorando duplicados (requiere tabla temporal o lógica pandas)
        # Para eficiencia, leemos lo que ya existe y solo insertamos lo nuevo
        existing_weather = pd.read_sql("SELECT wind_speed_ms, wave_height_m, weather_metric_id FROM gold_navoptima.dim_weather_metrics", conn)
        
        # Merge para encontrar nuevos
        weather_merged = pd.merge(weather_df, existing_weather, on=['wind_speed_ms', 'wave_height_m'], how='left')
        new_weather = weather_merged[weather_merged['weather_metric_id'].isnull()].copy()
        
        if not new_weather.empty:
            print(f"      -> Insertando {len(new_weather)} nuevas condiciones climáticas.")
            new_weather_insert = new_weather[['wind_speed_ms', 'wave_height_m', 'weather_category']]
            new_weather_insert.to_sql('dim_weather_metrics', engine, schema='gold_navoptima', if_exists='append', index=False)
        
        # Recargamos el mapa completo de IDs climáticos
        weather_map = pd.read_sql("SELECT wind_speed_ms, wave_height_m, weather_metric_id FROM gold_navoptima.dim_weather_metrics", conn)

        # ======================================================================
        # 4. DIMENSION: VESSELS (SCD Tipo 2 - Inicialización)
        # ======================================================================
        print("   🚢 Gestionando Dimensión: Buques (SCD Tipo 2)...")
        
        # Agrupamos por MMSI para obtener los datos estáticos únicos
        vessels_df = df.groupby('mmsi').agg({
            'length': 'first',
            'timestamp': 'min' # Fecha de inicio de validez = primer registro visto
        }).reset_index()
        
        vessels_df.rename(columns={'length': 'length_m', 'timestamp': 'valid_from'}, inplace=True)
        vessels_df['vessel_type_id'] = type_id_unknown
        vessels_df['width_m'] = None # No tenemos este dato
        vessels_df['valid_to'] = datetime(9999, 12, 31)
        vessels_df['is_current'] = True

        # Verificamos qué barcos ya existen para no duplicar en re-runs
        existing_mmsi = pd.read_sql("SELECT mmsi FROM gold_navoptima.dim_vessels", conn)['mmsi'].unique()
        new_vessels = vessels_df[~vessels_df['mmsi'].isin(existing_mmsi)]

        if not new_vessels.empty:
            print(f"      -> Registrando {len(new_vessels)} nuevos buques.")
            new_vessels.to_sql('dim_vessels', engine, schema='gold_navoptima', if_exists='append', index=False)
        
        # Recuperamos el mapa de SKs (Surrogate Keys)
        # NOTA: En un escenario real SCD2, filtraríamos por is_current=True y fechas
        vessel_map = pd.read_sql("SELECT mmsi, vessel_sk FROM gold_navoptima.dim_vessels WHERE is_current = TRUE", conn)

        # ======================================================================
        # 5. FACT TABLE: PERFORMANCE (Ensamble Final)
        # ======================================================================
        print("   📊 Construyendo Tabla de Hechos (Fact Table)...")
        
        # A. Mapear Vessel SK
        fact_df = pd.merge(df, vessel_map, on='mmsi', how='inner')
        
        # B. Mapear Weather ID (Usando los valores redondeados como clave de unión)
        fact_df = pd.merge(fact_df, weather_map, 
                           left_on=['wind_speed_rounded', 'wave_height_rounded'], 
                           right_on=['wind_speed_ms', 'wave_height_m'], 
                           how='inner')
        
        # C. Transformaciones Finales y KPIs Financieros
        fact_df['timestamp_utc'] = fact_df['timestamp']
        fact_df['sog_knots'] = fact_df['sog']
        fact_df['draft_m'] = fact_df['draft']
        fact_df['fuel_consumption_kgh'] = fact_df['fuel_consumption']
        
        # Cálculo de Costo: (kg / 1000) * Precio Tonelada
        fact_df['fuel_cost_usd'] = (fact_df['fuel_consumption'] / 1000.0) * BUNKER_PRICE_PER_TON

        # Selección de columnas finales según esquema
        final_cols = [
            'timestamp_utc', 'vessel_sk', 'weather_metric_id', 
            'sog_knots', 'draft_m', 'fuel_consumption_kgh', 'fuel_cost_usd'
        ]
        
        final_load = fact_df[final_cols]
        
        print(f"      -> Insertando {len(final_load)} registros transaccionales...")
        
        # Carga por lotes (Chunking) para no saturar memoria
        chunk_size = 100000
        total_rows = len(final_load)
        
        for i in range(0, total_rows, chunk_size):
            chunk = final_load.iloc[i:i+chunk_size]
            chunk.to_sql('fact_vessel_performance', engine, schema='gold_navoptima', if_exists='append', index=False)
            print(f"         ... Lote {i//chunk_size + 1} cargado ({len(chunk)} filas)")

    print(f"✅ ¡Carga Completa! Data Warehouse operativo.")

if __name__ == "__main__":
    load_gold_layer()