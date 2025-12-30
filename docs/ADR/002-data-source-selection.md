# ADR-002: Selección de Estrategia de Datos (Training & Inference)

Una estrategia de datos robusta es el fundamento de la ventaja competitiva de NavOptima. Este Registro de Decisión de Arquitectura (ADR, por sus siglas en inglés) formaliza las decisiones estructurales críticas para nuestros pipelines de datos de entrenamiento e inferencia. Este documento es una práctica fundamental para registrar las justificaciones y consecuencias de dichas decisiones, asegurando la alineación y la claridad a lo largo del ciclo de vida del proyecto.


--------------------------------------------------------------------------------


## 1. Contexto

La selección de las fuentes de datos es una decisión de arquitectura con un impacto estratégico directo en el éxito del Producto Mínimo Viable (MVP). Esta elección debe equilibrar cuidadosamente la riqueza y el volumen de los datos con la agilidad de desarrollo y la optimización de costos, principios clave de una arquitectura moderna orientada al valor de negocio.

Para las dos fases críticas de nuestro sistema —el entrenamiento inicial de modelos de predicción de consumo ("Cold Start") y la operación en tiempo real (inferencia)— NavOptima requiere tres flujos de datos esenciales: Telemetría de buques (AIS), Condiciones Ambientales (Weather) y Costos Financieros (Bunker Fuel). La directriz principal para la fase de MVP es el uso exclusivo de datos abiertos (Open Data). Esta restricción es una decisión estratégica deliberada para eliminar por completo los costos de licencia, validar el modelo de negocio con una inversión mínima (bajo Costo Total de Propiedad o TCO) y acelerar drásticamente nuestra velocidad de salida al mercado (Speed to Market). Este mandato de datos abiertos proporciona inmensos beneficios de costo y agilidad, pero también introduce un riesgo calculado de sesgo geográfico en los datos, que será abordado a través de una estrategia robusta de MLOps.

En base a este contexto, la siguiente sección detalla las fuentes de datos aprobadas.

## 2. Decisión

Este ADR establece el stack de fuentes de datos definitivo para el MVP de NavOptima. La selección ha sido dividida en dos categorías lógicas que se corresponden directamente con las fases del ciclo de vida de Machine Learning: datos para el entrenamiento inicial de modelos (históricos) y datos para la operación en tiempo real del sistema (inferencia).

### 2.1. Datos de Entrenamiento (Históricos / Cold Start)

Esta sección define nuestra estrategia de datos fríos (cold data), optimizada para el procesamiento por lotes (batch processing) de alto rendimiento y el almacenamiento de bajo coste. Las siguientes fuentes han sido seleccionadas por su capacidad para proveer grandes volúmenes de datos históricos, un requisito indispensable para el entrenamiento inicial ("Cold Start") de modelos de aprendizaje profundo robustos.

* Tráfico Marítimo (AIS): Dataset de la Autoridad Marítima Danesa (DMA)
  * Justificación Técnica (Transfer Learning): Se selecciona este dataset no solo por su gratuidad, sino por su validez física universal. La relación hidrodinámica fundamental (Consumo = f(Velocidad, Resistencia, Calado)) aprendida de los buques en el Mar del Norte es transferible a cualquier océano, ya que las leyes de la física naval son invariantes. Esto permite entrenar un modelo robusto de "Línea Base" para el MVP sin incurrir en los costos prohibitivos de adquirir datos privados del Pacífico Sur en etapa temprana. Este volumen masivo es un activo estratégico que nos permite superar el problema de aprendizaje con pocos ejemplos (few-shot learning) asociado a eventos operacionales raros. Permite al modelo aprender de una distribución de cola larga (long-tail distribution) de escenarios operativos del mundo real, algo imposible de lograr con datasets más pequeños y comerciales.
* Clima (Weather): Reanálisis ERA5 de Copernicus
  * Justificación: El dataset ERA5 es considerado un estándar industrial para datos climatológicos históricos (oleaje y viento). Adoptar un estándar de facto des-mitiga el riesgo de la fase de ingeniería de características (feature engineering) al garantizar la consistencia de los datos y permitir al equipo aprovechar técnicas de investigación y validación establecidas, acelerando así el camino hacia un modelo fiable.
* Combustible (Fuel Costs): USDA Socrata - Daily Bunker Fuel Prices
  * Justificación: Al ser una fuente gubernamental abierta y estable, elimina la dependencia de técnicas de scraping, que son frágiles y costosas de mantener. Provee precios diarios para combustibles clave (VLSFO/IFO380) en los principales hubs globales, garantizando una alta trazabilidad financiera y una gobernanza sólida sobre los datos de costos, un pilar fundamental en la gestión de datos empresariales.
* Indicadores Económicos Locales: API del Banco Central de Chile (SIET).
  * Justificación de Negocio: Aunque los costos globales son en USD (USDA Socrata), la realidad operativa de la casa matriz requiere trazabilidad en moneda local y contexto macroeconómico. Se integrarán las series de Dólar Observado (para conversión contable) y Precio del Cobre (como proxy de demanda de flete regional) para "tropicalizar" los resultados del modelo, asegurando que los reportes de la Capa Gold sean financieramente conciliables con la contabilidad chilena.

### 2.2. Datos Operativos (Tiempo Real / Inference)

Esta sección define nuestra ruta de datos calientes (hot data), optimizada para la recuperación de baja latencia para servir peticiones de inferencia en tiempo real. Las siguientes fuentes, basadas en APIs, han sido seleccionadas para la fase operativa del sistema.

* Clima: API de Open-Meteo.
* Tráfico: API de MarineTraffic (utilizando el plan gratuito/demo para la fase de MVP).

Esta selección de fuentes de datos sienta las bases para una estrategia de implementación clara y eficiente.

## 3. Estrategia de Implementación

Para la ingesta y procesamiento de los datos de entrenamiento, se adoptará un paradigma ELT (Extract, Load, Transform). Este enfoque fue elegido para maximizar la velocidad de ingesta y la flexibilidad. Al cargar primero los datos crudos y sin alterar en la Capa Bronze, desacoplamos la ingesta de la transformación, asegurando que los datos del sistema de origen se capturen rápidamente sin ser un cuello de botella para la lógica de negocio compleja. La estrategia se ejecutará en dos pasos principales:

1. Ingesta (Capa Bronze): Se desarrollarán scripts en Python para ejecutar una carga masiva (full batch load) de los datasets históricos de la DMA (AIS) y USDA Socrata (Fuel Costs). Los archivos CSV resultantes se almacenarán sin ninguna modificación en el directorio data/raw, que constituye la Capa Bronze de nuestro data lake. Esta capa inmutable de "fuente de verdad" es crítica para la Gobernanza de Datos, ya que garantiza la auditabilidad y permite el reprocesamiento completo y determinista de todo el pipeline de datos si la lógica de transformación evoluciona.
2. Fusión (Bronze -> Silver): El paso principal de transformación se ejecutará un proceso de enriquecimiento en dos etapas:
  1. Fusión Física: Join Espacio-Temporal de AIS + Clima para reconstruir la resistencia al avance (Slip Negativo).
  2. Contextualización Comercial: Los costos derivados en USD se cruzarán con el tipo de cambio histórico del Banco Central de Chile y el precio del Bunker en el hub de referencia (Panamá/Socrata). Esto transforma una predicción puramente técnica en un KPI financiero ("Costo de Viaje Ajustado") relevante para la toma de decisiones en la gerencia local.

A continuación, se analiza el impacto y los riesgos asociados a esta estrategia.

## 4. Consecuencias

Este análisis de las ventajas y los riesgos inherentes a la decisión tomada es una práctica esencial en la arquitectura de software. Entender estas consecuencias nos permite planificar mitigaciones de manera proactiva y alinear las expectativas de todos los stakeholders involucrados en el proyecto.

### * Positivas:
  * Costo Cero en Adquisición de Datos: Esta estrategia anula por completo los costos de licencia de datos. Esto nos permite alinear el presupuesto del MVP directamente con el desarrollo de producto y la experimentación, maximizando la eficiencia del capital invertido.
  * Trazabilidad y Gobernanza Financiera: El uso de la fuente USDA proporciona un linaje de datos (data lineage) inequívoco para todas las entradas relacionadas con los costos. Esto crea un "rastro de papel" transparente, esencial para las auditorías financieras y la confianza de los stakeholders, abordando directamente el principio básico de la responsabilidad sobre los datos (data accountability).
### * Riesgos:
  * Deriva de Covariables Geográficas (Covariate Shift): El principal riesgo técnico es la deriva de covariables geográficas (geographic covariate shift), un fenómeno en el que la distribución estadística de las características de entrada (ej. clima, estado del mar) en el entorno de producción (rutas marítimas globales) difiere significativamente del entorno de entrenamiento (predominantemente aguas danesas).
  * Necesidad de Recalibración del Modelo: La mitigación no es una solución única, sino un proceso continuo gobernado por MLOps. NavOptima implementará un ciclo robusto que implica: 
      1) la implementación de detección automatizada de deriva de datos (data drift) en los datos de inferencia entrantes para señalar desviaciones significativas de la distribución de entrenamiento, y 
      
      2) el monitoreo continuo del rendimiento del modelo contra la verdad fundamental. Cuando el rendimiento se degrade por debajo de un umbral predefinido, estos sistemas activarán un pipeline automatizado de reentrenamiento y validación con los datos recién adquiridos para la nueva región geográfica.
