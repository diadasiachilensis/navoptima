```mermaid
C4Container
    title Diagrama de Contenedores (Nivel 2) - Plataforma NavOptima

    System_Ext(ais_api, "AIS API", "Provee telemetría marítima y posicionamiento global de buques.")
    System_Ext(weather_api, "Weather API", "Provee datos climáticos históricos y pronósticos de alta resolución.")

    Boundary(nav_platform, "NavOptima Platform") {
        
        Container(airflow, "Apache Airflow", "Python/Airflow", "Orquestador Central: Dirige el flujo de trabajo, gestiona reintentos (Sagas) y asegura el cumplimiento del linaje de datos entre Quanta.")

        Boundary(bronze_layer, "Capa Bronze (Raw Ingestion)") {
            Container(ingestion_worker, "Ingestion Worker", "Python", "Extrae datos de APIs externas. Implementa el patrón Strategy para garantizar ingestas idempotentes y aisladas.")
            ContainerDb(raw_s3, "Raw Data Storage", "Amazon S3", "Data Lake inmutable que almacena telemetría y clima en formato original (JSON/Avro).")
        }

        Boundary(silver_layer, "Capa Silver (Validated & Enriched)") {
            Container(financial_processor, "Financial Processor", "Spark/Pandas", "Limpia y enriquece datos. Utiliza tipos Decimal para garantizar precisión financiera y bitemporalidad auditable.")
            ContainerDb(silver_db, "Enriched Database", "PostgreSQL/Iceberg", "Almacén de datos validados, deduplicados y listos para el análisis de costos operativo.")
        }

        Boundary(gold_layer, "Capa Gold (Business & Prediction)") {
            Container(ml_engine, "ML Training Engine", "XGBoost", "Módulo de entrenamiento de modelos predictivos de consumo de combustible mediante técnicas de Slicing.")
            ContainerDb(model_registry, "Model Registry", "MLflow", "Almacenamiento de artefactos, versiones de modelos y métricas de desempeño (RMSE/MAE).")
        }
    }

    Rel(airflow, ingestion_worker, "Dispara y monitorea", "Cron/Event")
    Rel(airflow, financial_processor, "Dispara tras éxito de Bronze", "Orchestration")
    Rel(airflow, ml_engine, "Dispara tras éxito de Silver", "Orchestration")

    Rel(ingestion_worker, ais_api, "Consume datos", "HTTPS/JSON")
    Rel(ingestion_worker, weather_api, "Consume datos", "HTTPS/JSON")
    Rel(ingestion_worker, raw_s3, "Persiste datos crudos", "Boto3/S3")

    Rel(financial_processor, raw_s3, "Lee datos crudos", "Parquet/S3 Select")
    Rel(financial_processor, silver_db, "Escribe datos validados (Decimal)", "JDBC/SQL")

    Rel(ml_engine, silver_db, "Extrae features", "SQL/Pandas")
    Rel(ml_engine, model_registry, "Registra modelos y métricas", "MLflow API")
```

Como **Arquitecto Líder** de **NavOptima**, procederé a detallar el **Diagrama de Contexto (Nivel 1 del Modelo C4)**. Este nivel es fundamental para definir el "Sistema de Interés" y sus límites, permitiendo que tanto los interesados técnicos como los de negocio comprendan las dependencias externas y el valor generado (Richards & Ford, 2020, p. 318).

A diferencia del diagrama anterior (Contenedores), aquí tratamos a NavOptima como una "caja negra" única, enfocándonos en las interacciones con los **actores** y los **sistemas externos** que alimentan nuestra arquitectura de datos.

### 1. Diagrama de Contexto del Sistema (Mermaid.js)

```mermaid
C4Context
    title Diagrama de Contexto (Nivel 1) - Sistema NavOptima

    Person(fleet_manager, "Gerente de Flota", "Toma decisiones operativas para optimizar rutas y consumo de combustible.")
    Person(auditor, "Auditor Financiero", "Verifica la integridad de los costos y el cumplimiento normativo (Compliance).")

    System(navoptima, "Plataforma NavOptima", "Calcula ineficiencias de consumo y predice costos operativos mediante la integración de telemetría y clima.")

    System_Ext(ais_system, "Proveedor de Datos AIS", "Sistema satelital que entrega posición, rumbo y velocidad de los buques en tiempo real.")
    System_Ext(weather_service, "Servicio Meteorológico", "API externa que provee condiciones de viento, mareas y oleaje.")
    System_Ext(bunker_api, "Bunker Price API", "Provee precios actualizados del combustible en diferentes puertos globales.")

    Rel(fleet_manager, navoptima, "Consulta KPIs de eficiencia y predicciones", "HTTPS")
    Rel(auditor, navoptima, "Audita registros de costos e inmutabilidad", "SQL/Reports")
    
    Rel(ais_system, navoptima, "Envía telemetría de la flota", "WebSockets/Streaming")
    Rel(weather_service, navoptima, "Provee datos climáticos", "JSON/REST")
    Rel(bunker_api, navoptima, "Suministra precios de combustible", "REST")
```

---

### 2. Justificación Técnica y Cruce de Fuentes

Para este diseño de Nivel 1, he aplicado los siguientes principios arquitectónicos extraídos de las fuentes:

*   **Definición de Límites y Quanta:** Aunque NavOptima está internamente distribuido, a nivel de contexto se visualiza como un único sistema. Esto se debe a que, desde la perspectiva del usuario, el sistema actúa como una unidad con **alta cohesión funcional** (Ford et al., 2021, p. 30). El límite separa nuestra lógica de negocio de los "Productores de Datos" externos (Konieczny, 2025, p. 147).
*   **Acoplamiento Externo (Efferent Coupling):** El sistema presenta una dependencia crítica hacia sistemas externos (AIS, Clima). Según el análisis de **Trade-offs**, hemos aceptado un acoplamiento con estos proveedores para evitar el costo prohibitivo de generar telemetría propia, priorizando la **viabilidad económica** del proyecto (Richards & Ford, 2020, p. 33).
*   **Integridad Financiera y Actores:** La inclusión del "Auditor Financiero" como actor principal responde a la necesidad de **Auditabilidad** y **Trazabilidad** detallada en el dominio de arquitecturas financieras (Khraisha, 2026, p. 2276). NavOptima debe garantizar que el dato que el auditor ve sea consistente con los eventos de consumo real capturados por el sistema AIS.
*   **Ciclo de Vida de los Datos:** La interacción con el servicio AIS y Meteorológico representa la fase de **Generación** dentro del ciclo de vida de la ingeniería de datos (Reis & Housley, 2022, p. 37). NavOptima transforma estos "hechos crudos" en "valor de negocio" para el Gerente de Flota mediante la capa de **Activación** (Tranquillin et al., 2024, p. 30).

---

### 3. Bibliografía

Ford, N., Richards, M., Sadalage, P., & Dehghani, Z. (2021). *Software Architecture: The Hard Parts*. O'Reilly Media, Inc.

Khraisha, T. (2026). *Designing Financial Data Architectures* (Early Release). O'Reilly Media, Inc.

Konieczny, B. (2025). *Data Engineering Design Patterns*. O'Reilly Media, Inc.

Reis, J., & Housley, M. (2022). *Fundamentals of Data Engineering*. O'Reilly Media, Inc.

Richards, M., & Ford, N. (2020). *Fundamentals of Software Architecture*. O'Reilly Media, Inc.

Tranquillin, M., Lakshmanan, V., & Tekiner, F. (2024). *Architecting Data and Machine Learning Platforms*. O'Reilly Media, Inc.

***

**Analogía Técnica:** *El Diagrama de Contexto es como el mapa de una capitanía de puerto; no nos muestra cómo funcionan los motores de los barcos (contenedores internos), sino qué barcos entran (datos externos), quiénes son los oficiales a cargo (usuarios) y cuáles son las fronteras marítimas del puerto (límites del sistema).*