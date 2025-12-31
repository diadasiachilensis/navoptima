# **🧭 NavOptima: Plataforma de Ingeniería de Datos para Eficiencia de Combustible**

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container-blue?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Postgres](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626.svg?style=for-the-badge&logo=Jupyter&logoColor=white)
![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)
![Power Bi](https://img.shields.io/badge/power_bi-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-black?style=for-the-badge&logo=deltalake&logoColor=white)
![Amazon S3](https://img.shields.io/badge/Amazon%20S3-569A31?style=for-the-badge&logo=amazons3&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Kubernetes](https://img.shields.io/badge/kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)

Este documento proporciona una visión detallada del proyecto de ingeniería de datos **NavOptima**. Su objetivo es servir como una guía central para desarrolladores, ingenieros y stakeholders, detallando los objetivos, la arquitectura del sistema, la pila tecnológica y las instrucciones para su despliegue y ejecución.

## **📝 Resumen del Proyecto**

**NavOptima** es una plataforma de inteligencia operativa diseñada para procesar telemetría marítima y variables climáticas con el fin de optimizar el mayor costo operativo de la flota: el combustible.

El proyecto resuelve el desafío crítico de transformar datos crudos de posicionamiento (AIS) y meteorología en insights financieros y predicciones de consumo auditables, permitiendo a la organización **Ultranav** monitorear la eficiencia de la flota y reducir su huella de carbono con precisión decimal.

## **📑 Tabla de Contenidos**

1. [Objetivos del Negocio y Técnicos](https://www.google.com/search?q=%23-1-objetivos-del-negocio-y-t%C3%A9cnicos)  
2. [Arquitectura del Sistema](https://www.google.com/search?q=%23-2-arquitectura-del-sistema)  
3. [Pila Tecnológica (Tech Stack)](https://www.google.com/search?q=%23-3-pila-tecnol%C3%B3gica-tech-stack)  
4. [Cómo Empezar (Getting Started)](https://www.google.com/search?q=%23-4-c%C3%B3mo-empezar-getting-started)  
5. [Estructura del Proyecto](https://www.google.com/search?q=%23-5-estructura-del-proyecto)  
6. [Licencia](https://www.google.com/search?q=%23-6-licencia)

## **🎯 1. Objetivos del Negocio y Técnicos**

Un principio fundamental en el diseño de **NavOptima** es la alineación estricta entre la ingeniería de datos y el impacto financiero (OPEX). No buscamos solo predecir, sino auditar y optimizar.

### **1.1. Problema de Negocio**

La organización carece de una trazabilidad integrada entre la operación física de los buques y su impacto financiero real. Las estimaciones de consumo actuales se basan en reportes manuales o promedios estáticos, lo que impide detectar ineficiencias causadas por clima adverso o degradación del casco en tiempo útil.

**Solución:** NavOptima integra datos de **Telemetría AIS**, **Clima (ERA5)** y **Precios de Mercado (USDA)** para generar una "Verdad Única" sobre el costo del viaje.

### **1.2. Objetivos Técnicos**

La arquitectura debe equilibrar la precisión financiera con la capacidad predictiva. Se han definido los siguientes pilares:

* **📊 Auditabilidad Financiera:** A diferencia de sistemas puramente predictivos, NavOptima prioriza la integridad del dato. Utilizamos tipos Decimal y patrones de **SCD Tipo 2** para garantizar que los costos históricos sean reproducibles ante una auditoría.  
* **🛡️ Idempotencia:** Nuestros pipelines de ingesta (Capa Bronze) son resilientes. Implementamos el patrón **Strategy** para asegurar que re-procesar un archivo de AIS no duplique costos ni altere la historia.  
* **🌐 Transferencia de Aprendizaje (Transfer Learning):** Ante la falta de datos locales etiquetados, el sistema está diseñado para entrenar modelos con datasets globales (Dinamarca) y aplicar la inferencia en rutas locales, validando la física naval subyacente.  
* **💎 Calidad de Datos (Contracts):** El poder predictivo depende de la integridad de la entrada. Utilizamos **Pydantic** para validar esquemas estrictos en la ingesta, rechazando datos corruptos antes de que contaminen la Capa Silver.

## **🏗️ 2. Arquitectura del Sistema**

La arquitectura sigue el patrón **Medallion (Bronze-Silver-Gold)** orquestado centralmente para garantizar trazabilidad.

### **2.1. Descripción General**

El flujo de datos transforma la "Señal Física" en "Valor Financiero":

1. **Fuentes (Generation):** APIs externas de AIS, Clima y Mercado.  
2. **Ingesta (Bronze):** Aterrizaje de datos crudos inmutables.  
3. **Procesamiento (Silver):** Limpieza, cruce espacio-temporal y cálculo de costos.  
4. **Inteligencia (Gold):** Agregaciones para BI y Features para ML.  
5. **Servicio (Serving):** Dashboards en Power BI y APIs de inferencia.

### **2.2. Fases del Ciclo de Vida del Dato**

#### **📡 Fuentes de Datos**

NavOptima ingesta datos heterogéneos: **Telemetría de Alta Frecuencia** (AIS), **Grillas Meteorológicas** (GRIB/NetCDF) y **Series Temporales Financieras** (Precios Bunker/Dólar).

#### **💾 Almacenamiento (Data Lakehouse)**

Utilizamos una arquitectura híbrida. **MinIO/S3** actúa como Data Lake para los archivos crudos (Bronze), mientras que **PostgreSQL** sirve como Data Warehouse para las capas Silver y Gold, permitiendo consultas SQL complejas y garantías ACID para los datos financieros.

#### **📥 Ingesta (Ingestion)**

La estrategia es **Batch Micro-particionado**. Un IngestionWorker en Python, orquestado por Airflow, descarga diariamente los deltas de datos. Se aplica el **Patrón Strategy** para desacoplar la lógica de conexión (API vs FTP) de la lógica de negocio.

#### **🔄 Transformación (Transformation)**

El núcleo del sistema. Aquí ocurre la **"Magia Física"**:

* **Data Fusion:** Cruzamos la posición GPS del barco con la celda climática correspondiente (Viento/Olas).  
* **Physics Proxy:** Aplicamos la "Ley del Cubo" para estimar el consumo teórico.  
* **Financial Context:** Convertimos el consumo a USD y CLP usando las tasas del día.

#### **📤 Servicio de Datos (Serving)**

* **Gold Layer:** Tablas dimensionales (Star Schema) optimizadas para Power BI.  
* **MLFlow:** Registro de modelos entrenados (XGBoost) listos para predecir consumo futuro.

## **🛠️ 3. Pila Tecnológica (Tech Stack)**

Tecnologías seleccionadas por su madurez y capacidad de auditoría.

| Categoría | Tecnologías |
| :---- | :---- |
| **Orquestación** | **Apache Airflow** (Gestión de dependencias y backfills) |
| **Lenguaje Core** | **Python 3.10+** (Pandas, Pydantic, Scikit-Learn) |
| **Almacenamiento** | **PostgreSQL** (DW), **MinIO** (Object Storage) |
| **Machine Learning** | **XGBoost** (Modelo), **MLflow** (Experiment Tracking) |
| **Visualización** | **Power BI** (Business Dashboard), **Seaborn** (EDA) |
| **Infraestructura** | **Docker**, **Docker Compose** |

## **🚀 4. Cómo Empezar (Getting Started)**

### **4.1. Prerrequisitos**

* Python 3.9+  
* Docker y Docker Compose  
* Git

### **4.2. Instalación**

```bash
# 1. Clonar el repositorio  
git clone https://github.com/diadasiachilensis/navoptima.git
cd navoptima

# 2. Configurar entorno virtual  
python -m venv .venv  
source .venv/bin/activate  # o .venv\\Scripts\\activate en Windows

# 3. Instalar dependencias  
pip install -r requirements.txt

# 4. Levantar infraestructura (Airflow \+ DB)  
cd orchestration  
docker-compose up -d  
```

### **4.3. Ejecución de Pipelines**

Para correr la ingesta inicial de datos históricos (Dinamarca \+ USDA):
```bash
# Ejecutar el script de ingesta manual (Bypass de Airflow para dev)  
python src/ingestion\_worker/main.py \--mode=historical \--source=dma
```

## **📂 5. Estructura del Proyecto**

Organización basada en *Domain-Driven Design* y *Data Engineering Lifecycle*.

```bash

navoptima/  
├── data/                     # Almacenamiento local (Raw/Staging/Curated) \- Ignorado por Git  
├── docs/                     # Artefactos de Ingeniería (ADRs, Diagramas, Whitepapers)  
├── notebooks/                # Laboratorio de Data Science (EDA y Prototipos ML)  
├── orchestration/            # Definición de infraestructura (Docker, DAGs)  
├── src/                      # Código Fuente de Producción  
│   ├── ingestion\_worker/    # Capa Bronze (Extract)  
│   ├── data\_processor/      # Capa Silver (Transform & Enrich)  
│   ├── ml\_engine/           # Capa Gold (Train & Predict)  
│   └── shared/               # Contratos de Datos (Schemas Pydantic)  
├── tests/                    # Tests Unitarios y de Arquitectura  
└── README.md                 # Esta documentación  
```

## **📄 6. Licencia**

Distribuido bajo la **Licencia MIT**. Consulta LICENSE.txt para obtener más información.
