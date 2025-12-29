# Análisis de Vistas Arquitectónicas y Topología de Datos de NavOptima

## Introducción

El diseño de plataformas de datos complejas como NavOptima exige una deliberación arquitectónica rigurosa desde su concepción. La adopción de un enfoque "Architecture-First" es una decisión estratégica que prioriza la creación de un sistema robusto, modular y evolutivo antes de la implementación de funcionalidades específicas. Este principio es fundamental para mitigar riesgos de negocio tangibles, como la acumulación de deuda técnica, la incapacidad de escalar ante el crecimiento de la flota o el fracaso en el cumplimiento de requisitos regulatorios de auditoría. Así, se asegura que la estructura del sistema no solo soporte las necesidades actuales, sino que garantice la continuidad del negocio y su capacidad de adaptación sin incurrir en costosas reingenierías.

En este contexto, NavOptima se define como una plataforma de inteligencia operativa para la gestión de flotas marítimas. Su propósito es procesar flujos de datos heterogéneos—desde telemetría en tiempo real hasta información financiera—para transformarlos en valor de negocio tangible, permitiendo una toma de decisiones informada y optimizada.

El diseño de la plataforma se guía por el principio de Architecture Quantum, que se define como "un artefacto desplegable de forma independiente con una alta cohesión funcional" (Ford et al., 2021, p. 28). Este concepto es fundamental para NavOptima, ya que permite que sus componentes lógicos, como los sistemas de ingesta de datos y los módulos de procesamiento, se desarrollen, desplieguen y escalen de forma independiente. Esta modularidad es clave para la agilidad y la resiliencia del sistema, permitiendo que cada "quantum" evolucione a su propio ritmo sin afectar al resto de la plataforma.

Este informe procederá a analizar las vistas arquitectónicas clave del sistema NavOptima, comenzando con la vista de contexto de más alto nivel para establecer su alcance y sus interacciones fundamentales.

## Análisis de la Vista de Contexto (C4 Nivel 1)

El Diagrama de Contexto, correspondiente al Nivel 1 del modelo C4, es una herramienta esencial para establecer una comprensión compartida del sistema en su nivel más abstracto. Su propósito es delimitar claramente el alcance de la plataforma NavOptima, identificar a sus usuarios clave (actores) y visualizar las interacciones críticas con los sistemas externos de los que depende. Al tratar el sistema como una "caja negra", este diagrama establece el marco operativo y las fronteras de la plataforma sin entrar en detalles de su implementación interna.

![Diagrama de Contexto C4](c4_model/context-system-diagram.png)

> **Figura 1**: Diagrama de Contexto de la Plataforma NavOptima (Descripción: Un diagrama de contexto que muestra a los actores "Gerente de Flota" y "Auditor Financiero" interactuando con el sistema "Plataforma NavOptima". El sistema a su vez se comunica con dos sistemas externos: "Proveedor AIS" vía Streaming y "Bunker Price API".)

### Interacciones y Requisitos Clave

#### Actores Principales

El Gerente de Flota es el actor primario del sistema. Este rol representa al usuario operativo que consume los análisis, informes y predicciones generados por NavOptima para tomar decisiones estratégicas y tácticas, como la optimización de rutas, la gestión del consumo de combustible y la programación de mantenimientos. Su interacción define el propósito fundamental de la plataforma: transformar datos en inteligencia operativa.

La inclusión del Auditor Financiero como actor es una decisión de diseño estratégica que impone un requisito no funcional de máxima importancia: la auditabilidad y trazabilidad de los datos. Para que los análisis de costos operativos, especialmente los relacionados con el combustible (bunker), sean fiables y defendibles, cada dato de precios y cada transacción debe ser completamente verificable desde su origen hasta su presentación final. Esto subraya la necesidad de una gobernanza de datos robusta, ya que, como afirman Reis y Housley (2022), "La gobernanza de datos es una base para las prácticas de negocio basadas en datos", y sus categorías principales incluyen "la descubribilidad, la seguridad y la rendición de cuentas (accountability)" (p. 57). La presencia de este actor obliga a que la arquitectura garantice la integridad y el linaje de los datos en todo su ciclo de vida.

#### Dependencias Externas

El sistema depende de dos fuentes de datos externas críticas que presentan características de integración distintas:

1. Proveedor AIS (Streaming): Esta fuente proporciona datos de posicionamiento y telemetría de los buques en tiempo real. La naturaleza de esta integración es un flujo continuo de eventos (streaming), lo que impone requisitos de alta disponibilidad y procesamiento de baja latencia en la capa de ingesta de NavOptima.

2. Bunker Price API: Proporciona los precios del combustible, un dato crítico para los cálculos de costos que deben ser auditables. A diferencia del proveedor AIS, esta integración se realiza típicamente mediante un mecanismo de solicitud-respuesta. La heterogeneidad entre la ingesta de datos en tiempo real y la recuperación de datos bajo demanda es un desafío arquitectónico clave que la plataforma debe resolver eficientemente.

Este análisis de contexto demuestra cómo los requisitos de los actores y las características de los sistemas externos moldean fundamentalmente el diseño de la plataforma. La siguiente sección descompone la "caja negra" de NavOptima para examinar su arquitectura interna.

## Análisis de la Vista de Contenedores (C4 Nivel 2)

La Vista de Contenedores (Nivel 2 del modelo C4) descompone la plataforma NavOptima para revelar su estructura interna y la topología de sus principales componentes ejecutables. Esta arquitectura implementa el patrón Medallion Architecture, una estrategia de diseño por capas que se ha consolidado como un estándar en la ingeniería de datos moderna. Este patrón organiza el flujo de datos en etapas progresivas de refinamiento—Bronze, Silver y Gold—, transformando los datos desde su estado crudo hasta un formato agregado y listo para el análisis de negocio y la aplicación de modelos de machine learning.

![Diagrama de Containers C4](c4_model/container-diagram.png)

>**Figura 2:** Diagrama de Contenedores con Medallion Architecture (Descripción: Un diagrama de contenedores que ilustra un flujo de datos orquestado por "Apache Airflow". El flujo atraviesa tres capas delimitadas: "Capa Bronze" con un "Ingestion Worker", "Capa Silver" con un "Financial Processor" y "Capa Gold" con un "ML Engine".)

A continuación, se analiza cada uno de los componentes y capas que conforman esta arquitectura.

### Orquestación Centralizada (Apache Airflow)

El componente Apache Airflow actúa como el orquestador central del flujo de datos a través de la plataforma. Su función es crítica para gestionar las dependencias complejas y asegurar la ejecución secuencial y fiable de las tareas en las capas Bronze, Silver y Gold. Define los flujos de trabajo como grafos acíclicos dirigidos (DAGs), lo que permite modelar explícitamente las relaciones entre los distintos procesos.

Apache Airflow actúa como el director de una orquesta sinfónica. Cada componente (Ingestion Worker, Financial Processor, ML Engine) es un instrumentista experto en su dominio. Airflow no toca los instrumentos, pero posee la partitura completa (el DAG), asegurando que cada músico entre en el momento preciso y que la ejecución del conjunto sea armoniosa y predecible. Al centralizar la lógica del flujo de trabajo, se desacoplan eficazmente los componentes y se reduce la complejidad del sistema. En arquitecturas distribuidas, gestionar la "complejidad del acoplamiento semántico del problema" es un desafío fundamental (Ford et al., 2021, p. 342), y un orquestador como Airflow permite manejar esta complejidad de manera explícita y centralizada.

### Capa Bronze (Ingesta Cruda)

La Capa Bronze es el punto de entrada para todos los datos externos a la plataforma NavOptima. Su objetivo principal es persistir los datos de origen con la máxima fidelidad posible, en su formato original y sin aplicar transformaciones que alteren su contenido. Esta capa funciona como un registro histórico inmutable, una "fuente de verdad" fiable y auditable.

El componente Ingestion Worker es el responsable de conectarse a las diversas fuentes de datos. Su diseño se basa en el Strategy Pattern, una solución arquitectónica deliberada para gestionar la heterogeneidad de las fuentes externas identificada en la Vista de Contexto. Este patrón de diseño de software permite definir una familia de algoritmos (estrategias de ingesta), encapsular cada uno de ellos y hacerlos intercambiables para manejar tanto datos de alta velocidad en tiempo real como datos de baja velocidad por solicitud-respuesta. En la práctica, esto se traduce en implementar clases distintas como AISStreamIngestionStrategy y BunkerPriceApiStrategy, que encapsulan la lógica específica para cada fuente. El Ingestion Worker puede entonces seleccionar y ejecutar dinámicamente la estrategia apropiada sin que su lógica principal se vea afectada por los detalles de cada fuente de datos.

La inmutabilidad de esta capa es una respuesta arquitectónica directa al requisito de auditabilidad impuesto por el "Auditor Financiero". Proporciona un registro de origen inalterable, garantizando que cada análisis financiero pueda ser rastreado hasta su dato crudo original sin ambigüedad. Si se detecta un error en una capa superior, siempre es posible reconstruir los resultados corrigiendo la lógica y reprocesando los datos desde esta fuente prístina. Este enfoque representa una evolución disciplinada sobre los data lakes tradicionales, donde a menudo "simplemente se vierte la información y nunca se actualiza o elimina" (Reis & Housley, 2022, p. 111), pero añadiendo un propósito claro: servir como una base auditable y reproducible para todo el sistema.

### Capa Silver (Procesamiento Financiero)

La Capa Silver es la zona intermedia de la arquitectura, donde los datos crudos de la capa Bronze se limpian, validan, conforman y enriquecen. El propósito de esta capa es transformar los datos en modelos de información fiables y orientados a las necesidades del negocio, como pueden ser los registros financieros consolidados.

El Financial Processor es el componente central de esta capa y tiene responsabilidades críticas que demandan una alta precisión de ingeniería. Una de sus tareas fundamentales es la gestión de la Precisión Decimal en todos los cálculos de costos. El uso de tipos de datos Decimal en lugar de tipos de punto flotante (float o double) es una práctica indispensable en el dominio financiero. El uso de tipos de punto flotante podría introducir errores de redondeo de céntimos en miles de transacciones diarias, que se acumularían en discrepancias de miles de dólares en los informes anuales, invalidando por completo su validez ante una auditoría.

Asimismo, la implementación de un almacenamiento Bitemporal no es una opción, sino una necesidad derivada de los requisitos del Auditor. En dominios regulados o financieros, no basta con saber cuándo ocurrió un evento en el mundo real (tiempo de evento); también es crucial registrar cuándo se registró dicho evento en el sistema (tiempo de procesamiento). Esta dualidad temporal es la base del almacenamiento bitemporal y permite reconstruir el estado exacto del conocimiento del sistema en cualquier punto del tiempo, una capacidad indispensable para auditorías forenses y el cumplimiento normativo.

### Capa Gold (Inteligencia de Negocio)

La Capa Gold representa la fase final del pipeline de datos. Contiene datos altamente curados, agregados y optimizados para el consumo directo. Esta capa expone la información en formatos que facilitan el análisis por parte de usuarios de negocio, la visualización en herramientas de inteligencia de negocio (BI) y, como en el caso de NavOptima, el entrenamiento y la ejecución de modelos de machine learning.

El ML Engine es un consumidor clave de los datos de la capa Gold, generando predicciones que aportan valor operativo. Sin embargo, su validación no puede basarse únicamente en métricas de rendimiento globales. Un modelo con una precisión global del 98% podría ser catastróficamente erróneo en un 100% para los buques de tipo GNL (Gas Natural Licuado) en rutas transpacíficas, un fallo de alto riesgo financiero y de seguridad que quedaría completamente enmascarado por la métrica agregada.

Para mitigar este riesgo, la estrategia de validación del ML Engine debe emplear la Validación por Slicing. Esta técnica se define como la práctica de "separar los datos en subconjuntos y observar el rendimiento del modelo en cada subconjunto por separado" (Huyen, 2022, p. 188). Este enfoque es cualitativamente superior porque permite detectar sesgos ocultos y fallos sistemáticos. Para NavOptima, esto significa poder verificar si el modelo funciona de manera fiable para diferentes tipos de buques, rutas comerciales o condiciones meteorológicas, lo cual es vital para garantizar la confianza y la seguridad en las operaciones que dependen de sus predicciones.

En conjunto, la arquitectura Medallion implementada en NavOptima proporciona un marco robusto y escalable que transforma sistemáticamente los datos brutos para soportar desde la auditoría financiera más estricta hasta la inteligencia artificial predictiva más avanzada.

## Referencias Bibliográficas

Ford, N., Richards, M., Sadalage, P., & Dehghani, Z. (2021). Software architecture: The hard parts: Modern trade-off analyses for distributed architectures. O'Reilly Media.

Huyen, C. (2022). Designing machine learning systems: An engineering approach. O'Reilly Media.

Reis, J., & Housley, M. (2022). Fundamentals of data engineering: Plan and build robust data systems. O'Reilly Media.
