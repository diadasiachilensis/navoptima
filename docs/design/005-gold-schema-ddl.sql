-- =============================================================================
-- PROYECTO NAVOPTIMA - CAPA GOLD (DATA WAREHOUSE)
-- Arquitectura: Esquema Estrella con SCD Tipo 2
-- Motor: PostgreSQL
-- =============================================================================

-- 1. CREACIÓN DEL ESQUEMA
-- -----------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS gold_navoptima;

-- 2. TABLA MAESTRA: TIPOS DE BUQUES (Nivel 1 - Diccionario)
-- Normalización 3FN para eliminar redundancia de texto.
-- -----------------------------------------------------------------------------
CREATE TABLE gold_navoptima.dim_vessel_types (
    vessel_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE
);

-- Semilla de datos iniciales (Estándar Naviera)
INSERT INTO gold_navoptima.dim_vessel_types (type_name) VALUES 
('Bulk Carrier'), 
('Container Ship'), 
('General Cargo'), 
('Oil Tanker'), 
('Chemical Tanker'),
('Passenger'), 
('Fishing'),
('Tug');

-- 3. TABLA MAESTRA: MÉTRICAS CLIMÁTICAS (Nivel 1 - Contexto Físico)
-- Normaliza las fuerzas ambientales para análisis de resistencia añadida.
-- -----------------------------------------------------------------------------
CREATE TABLE gold_navoptima.dim_weather_metrics (
    weather_metric_id SERIAL PRIMARY KEY,
    
    -- Variables Físicas (DECIMAL para precisión en cálculos de resistencia)
    wind_speed_ms DECIMAL(10,4) NOT NULL,
    wave_height_m DECIMAL(10,4) NOT NULL,
    
    -- Categoría descriptiva para filtros de BI (Ej: "Storm", "Calm")
    weather_category VARCHAR(50)
);

CREATE INDEX idx_weather_wind ON gold_navoptima.dim_weather_metrics(wind_speed_ms);

-- 4. DIMENSIÓN DE BUQUES (Nivel 2 - Historia / SCD Tipo 2)
-- EL CORAZÓN DE LA AUDITORÍA. Maneja versiones históricas del activo.
-- -----------------------------------------------------------------------------
CREATE TABLE gold_navoptima.dim_vessels (
    -- Clave Subrogada (Surrogate Key): Identifica la VERSIÓN única del barco
    vessel_sk SERIAL PRIMARY KEY,
    
    -- Clave Natural: Identifica al barco físico (MMSI)
    mmsi INTEGER NOT NULL,
    
    -- Relación con el Tipo (FK)
    vessel_type_id INTEGER REFERENCES gold_navoptima.dim_vessel_types(vessel_type_id),
    
    -- Variables Estructurales (Definen la física del modelo ML)
    -- Si estas cambian, se debe generar una nueva versión (vessel_sk)
    length_m DECIMAL(10,2), 
    width_m DECIMAL(10,2),
    
    -- Columnas de Auditoría SCD Tipo 2 ("Vigencia del Pasaporte")
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP DEFAULT '9999-12-31', -- Fecha futura = Vigente
    is_current BOOLEAN DEFAULT TRUE,
    
    -- Constraint: Integridad de Historia (No puede haber dos versiones vivas a la vez)
    CONSTRAINT uq_vessel_history UNIQUE (mmsi, valid_from)
);

-- Índices para optimizar el "Time Travel" y busquedas operativas
CREATE INDEX idx_dim_vessels_mmsi ON gold_navoptima.dim_vessels(mmsi);
CREATE INDEX idx_dim_vessels_current ON gold_navoptima.dim_vessels(is_current) WHERE is_current = TRUE;

-- 5. TABLA DE HECHOS: RENDIMIENTO Y COSTOS (Nivel 3 - Transaccional)
-- Registra eventos de consumo. Conecta la física con las finanzas.
-- -----------------------------------------------------------------------------
CREATE TABLE gold_navoptima.fact_vessel_performance (
    performance_id BIGSERIAL PRIMARY KEY,
    
    -- TIEMPO: Cuándo ocurrió el evento
    timestamp_utc TIMESTAMP NOT NULL,
    
    -- CONTEXTO (Foreign Keys)
    -- vessel_sk: Apunta a la versión histórica exacta del barco (Auditoría)
    vessel_sk INTEGER NOT NULL REFERENCES gold_navoptima.dim_vessels(vessel_sk),
    -- weather_metric_id: Apunta a las condiciones del mar
    weather_metric_id INTEGER NOT NULL REFERENCES gold_navoptima.dim_weather_metrics(weather_metric_id),
    
    -- VARIABLES OPERACIONALES (Medidas Degeneradas)
    -- Son numéricas y cambian rápido, por eso viven aquí.
    sog_knots DECIMAL(10,2) NOT NULL,    -- Velocidad (Input crítico ML)
    draft_m DECIMAL(10,2) NOT NULL,      -- Calado (Input crítico ML)
    
    -- TARGETS Y KPIs (Negocio)
    fuel_consumption_kgh DECIMAL(10,4) NOT NULL, -- Target para entrenamiento XGBoost
    fuel_cost_usd DECIMAL(12,4) NOT NULL         -- KPI Financiero Auditado
);

-- Índices de particionamiento lógico y velocidad de consulta
CREATE INDEX idx_fact_timestamp ON gold_navoptima.fact_vessel_performance(timestamp_utc);
CREATE INDEX idx_fact_vessel_sk ON gold_navoptima.fact_vessel_performance(vessel_sk);