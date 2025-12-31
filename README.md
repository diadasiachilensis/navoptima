# **🧭 Navoptima: Plataforma de Ingeniería de Datos para Predicción de Churn**

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

Este documento proporciona una visión detallada del proyecto de ingeniería de datos **Navoptima**. Su objetivo es servir como una guía central para desarrolladores, ingenieros y stakeholders, detallando los objetivos, la arquitectura del sistema, la pila tecnológica y las instrucciones para su despliegue y ejecución.

## **📝 Resumen del Proyecto**

**Navoptima** es una plataforma de ingeniería de datos de alto rendimiento diseñada para procesar y analizar flujos de eventos en tiempo real y por lotes.

El proyecto resuelve el desafío crítico de transformar datos crudos y volátiles en insights accionables y predicciones de baja latencia, permitiendo a la organización optimizar sus operaciones de negocio, como la **\[predicción de abandono de clientes\]**, con agilidad y precisión.

## **📑 Tabla de Contenidos**

1. [Objetivos del Negocio y Técnicos](https://www.google.com/search?q=%23-1-objetivos-del-negocio-y-t%C3%A9cnicos)  
2. [Arquitectura del Sistema](https://www.google.com/search?q=%23-2-arquitectura-del-sistema)  
3. [Pila Tecnológica (Tech Stack)](https://www.google.com/search?q=%23-3-pila-tecnol%C3%B3gica-tech-stack)  
4. [Cómo Empezar (Getting Started)](https://www.google.com/search?q=%23-4-c%C3%B3mo-empezar-getting-started)  
5. [Estructura del Proyecto](https://www.google.com/search?q=%23-5-estructura-del-proyecto)  
6. [Licencia](https://www.google.com/search?q=%23-6-licencia)

## **🎯 1\. Objetivos del Negocio y Técnicos**

Un principio fundamental en el diseño de sistemas de Machine Learning es la alineación estricta entre los objetivos técnicos y las métricas de negocio. El éxito de un proyecto de datos no se mide por la precisión del modelo en un vacío, sino por su capacidad para generar un impacto tangible en los indicadores clave del negocio. **Navoptima** se ha diseñado con esta filosofía en su núcleo.

### **1.1. Problema de Negocio**

La organización necesita una capacidad proactiva para identificar a los clientes en riesgo de abandonar el servicio (*churn*). Las soluciones existentes procesan los datos de forma periódica (diaria o semanal), lo que genera una ventana de tiempo demasiado amplia durante la cual se pierden oportunidades de retención.

**Solución:** Navoptima aborda este problema proporcionando predicciones casi en tiempo real sobre la probabilidad de abandono, permitiendo intervenciones personalizadas y oportunas.

### **1.2. Objetivos Técnicos**

Para resolver el problema de negocio, la arquitectura debe equilibrar el inherente *trade-off* entre el rendimiento del procesamiento por lotes y la latencia de las predicciones en tiempo real. Se han definido los siguientes objetivos técnicos clave:

* **⚡ Alto Rendimiento (High Throughput):** Para garantizar que nuestros modelos de ML se entrenen con datos completos y precisos, el sistema debe procesar de manera eficiente grandes volúmenes de datos históricos. Este enfoque por lotes es fundamental para el análisis exploratorio y el reentrenamiento periódico de los modelos.  
* **⏱️ Baja Latencia (Low Latency):** Para el caso de uso de predicción de abandono, servir predicciones con un retardo mínimo es crítico para habilitar intervenciones proactivas y oportunas (ej. ofrecer un descuento personalizado) antes de que un cliente finalice su decisión de abandonar el servicio.  
* **🔄 Idempotencia:** Para lograr un procesamiento de datos fiable, nuestros pipelines deben ser resilientes a fallos y reejecuciones. Al implementar *Idempotency Design Patterns* como el **Merger pattern**, garantizamos que la reejecución de un trabajo no introduzca datos duplicados ni corrompa el estado del sistema, lo cual es fundacional para la integridad de nuestro *feature store*.  
* **💎 Calidad de Datos:** El poder predictivo de nuestros modelos depende directamente de la integridad de los datos de entrada. Para garantizarla, aplicamos el patrón **Constraints Enforcer**, que valida que solo los datos que cumplen con un esquema y reglas de negocio predefinidas sean procesados, previniendo que datos de mala calidad se propaguen por el sistema.

La siguiente arquitectura es una respuesta directa a estos requisitos técnicos, con cada componente y patrón de diseño elegido para satisfacer uno o más de estos objetivos.

## **🏗️ 2\. Arquitectura del Sistema**

La arquitectura de Navoptima está estructurada siguiendo las fases del **Ciclo de Vida de la Ingeniería de Datos (Data Engineering Lifecycle)**. Este enfoque sistémico no solo garantiza un flujo de datos coherente, sino que también nos permite aislar, optimizar y escalar cada fase de manera independiente, una decisión clave para la mantenibilidad y evolución del sistema a largo plazo.

### **2.1. Descripción General**

El flujo de datos de alto nivel sigue la secuencia de procesamiento definida por el ciclo de vida del dato:

1. **Fuentes de Datos (Generation):** Sistemas transaccionales y de eventos generan los datos crudos.  
2. **Almacenamiento (Storage):** Los datos crudos y procesados se almacenan en un sistema optimizado para escalabilidad y acceso eficiente.  
3. **Ingesta (Ingestion):** Los datos son capturados desde las fuentes y transportados a nuestra capa de transformación.  
4. **Transformación (Transformation):** Los datos crudos se limpian, enriquecen y modelan para su uso en análisis y Machine Learning.  
5. **Servicio de Datos (Serving):** Los datos procesados y las predicciones del modelo se exponen a los sistemas consumidores.

### **2.2. Fases del Ciclo de Vida del Dato**

#### **📡 Fuentes de Datos (Generation)**

Navoptima se alimenta de una variedad de sistemas de origen, incluyendo bases de datos de aplicaciones **OLTP** (con un *fixed schema*) que registran las transacciones de los usuarios y flujos de eventos de telemetría (considerados *schemaless*) que capturan las interacciones en tiempo real. Esta diversidad requiere una arquitectura de almacenamiento e ingesta flexible.

#### **💾 Almacenamiento (Storage)**

Nuestra arquitectura se basa en un enfoque **Data Lakehouse**, una decisión estratégica para combinar la flexibilidad de un Data Lake —ideal para almacenar los flujos de eventos *schemaless*— con las garantías transaccionales **ACID** y el rendimiento de un Data Warehouse, que es esencial para el consumo por parte de herramientas de BI y analistas.

La base de nuestro almacenamiento es un *object store* (ej. Amazon S3) con un formato de tabla abierta (ej. Delta Lake), lo que implementa el principio clave de **Separación de Cómputo y Almacenamiento**. Esto nos permite escalar los recursos de procesamiento y almacenamiento de forma independiente, optimizando costos y rendimiento.

#### **📥 Ingesta (Ingestion)**

Para satisfacer el *trade-off* entre alto rendimiento y baja latencia, la estrategia de ingesta es híbrida.

* **Batch:** Para el procesamiento por lotes que alimenta el reentrenamiento de modelos, empleamos patrones como el **Incremental Loader** para cargar eficientemente solo los cambios diferenciales, satisfaciendo el objetivo de Alto Rendimiento.  
* **Real-time:** Para las predicciones de abandono en tiempo real, se implementa una ingesta por streaming que captura cambios de la base de datos (**CDC**) a través de un **Passthrough Replicator**, garantizando la Baja Latencia necesaria para intervenciones oportunas.

#### **🔄 Transformación (Transformation)**

Adoptamos un modelo **ELT (Extract, Load, Transform)**, que es la elección natural para una arquitectura Lakehouse. Al cargar primero los datos crudos en el almacenamiento de bajo costo, podemos aprovechar el principio de 'Separación de Cómputo y Almacenamiento' para aplicar transformaciones complejas utilizando motores de procesamiento distribuido potentes como **Spark**. Este enfoque es más escalable y rentable que el ETL tradicional.

Durante esta fase, aplicamos patrones clave como el **Merger pattern** para la idempotencia en las operaciones de actualización y el **Data Enrichment** para añadir valor contextual a los datos.

#### **📤 Servicio de Datos (Serving Data)**

Los resultados finales se exponen de dos maneras, equilibrando el *trade-off* entre latencia y rendimiento:

1. **Tablas Agregadas:** Disponibles en el Data Lakehouse para que los analistas de negocio y científicos de datos las consuman a través de herramientas de BI o notebooks.  
2. **API de Predicción:** Un microservicio de baja latencia que expone las predicciones del modelo para el consumo síncrono por parte de las aplicaciones cliente.

La implementación de esta arquitectura se apoya en un conjunto de tecnologías cuidadosamente seleccionadas por su robustez, escalabilidad y madurez en el ecosistema de datos.

## **🛠️ 3\. Pila Tecnológica (Tech Stack)**

La siguiente tabla resume las tecnologías clave utilizadas en el proyecto Navoptima, agrupadas por su función dentro del ciclo de vida del dato.

| Categoría | Tecnologías |
| :---- | :---- |
| **Orquestación de Flujos** | Apache Airflow, Dagster |
| **Procesamiento de Datos** | Apache Spark, Apache Flink |
| **Streaming y Mensajería** | Apache Kafka, Amazon Kinesis |
| **Almacenamiento** | Delta Lake, PostgreSQL, Amazon S3 |
| **Servicio de Predicciones** | API REST con FastAPI, Seldon Core |
| **Contenerización** | Docker, Kubernetes (K8s) |

## **🚀 4\. Cómo Empezar (Getting Started)**

Sigue estos pasos para configurar y ejecutar una versión local del entorno de desarrollo del proyecto.

### **4.1. Prerrequisitos**

Asegúrate de tener instaladas las siguientes herramientas en tu máquina local:

* Python 3.9+  
* Docker y Docker Compose  
* make

### **4.2. Instalación**

Ejecuta los siguientes comandos en tu terminal para clonar el repositorio e instalar todas las dependencias necesarias.

\# Clona este repositorio  
git clone \[https://github.com/diadasiachilensis/navoptima.git\](https://github.com/diadasiachilensis/navoptima.git)  
cd navoptima

\# Instala las dependencias de Python  
pip install \-r requirements.txt

\# Construye las imágenes de Docker y levanta los servicios de infraestructura  
\# (ej. base de datos, Kafka) definidos en docker-compose.yml.  
make build  
make up

### **4.3. Ejecución**

Para iniciar un pipeline específico, utiliza el siguiente comando. Por ejemplo, para ejecutar el DAG que procesa las características diarias de abandono de clientes:

\# Ejemplo para ejecutar un pipeline específico  
make run-pipeline pipeline\_name=process\_daily\_churn\_features

## **📂 5\. Estructura del Proyecto**

La estructura del repositorio está organizada para separar claramente las distintas responsabilidades del proyecto.

navoptima/  
├── data/              \# Scripts y ficheros relacionados con datos (ej. seeds, schemas)  
├── notebooks/         \# Notebooks para análisis exploratorio y experimentación  
├── src/               \# Código fuente principal de la aplicación y los pipelines  
├── tests/             \# Pruebas unitarias y de integración  
├── .env.example       \# Plantilla para variables de entorno  
├── docker-compose.yml \# Definición de servicios para el entorno local  
├── Dockerfile         \# Fichero para construir la imagen de Docker de la aplicación  
├── LICENSE.txt        \# Licencia del proyecto  
└── README.md          \# Esta documentación

## **📄 6\. Licencia**

Distribuido bajo la **Licencia MIT**. Consulta LICENSE.txt para obtener más información.
