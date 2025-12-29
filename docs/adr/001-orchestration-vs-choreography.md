# ADR-001: Orquestación Centralizada para Integridad Financiera

##  Contexto

Este Registro de Decisión Arquitectónica (ADR) establece el patrón de coordinación de datos para el proyecto NavOptima. Esta decisión es fundamental para garantizar la integridad, consistencia y auditabilidad de los flujos de datos que soportan nuestras operaciones financieras y los modelos de Machine Learning. Una arquitectura robusta en este ámbito es un requisito indispensable para cumplir con los estándares de gobernanza y responsabilidad que el proyecto exige.

La arquitectura de datos del proyecto se basa en un modelo de tres capas, diseñado para transformar progresivamente los datos desde su estado inicial hasta un formato optimizado para el análisis y consumo (Kretz et al., 2023, p. 116). Las capas, con sus nombres internos de proyecto, son las siguientes:

* Bronze (Crudo): Representa la ingesta de datos sin procesar directamente desde las fuentes originales. En esta capa, los datos se almacenan en su formato nativo para preservar la fidelidad con el origen.
* Silver (Enriquecido): Contiene datos que han sido sometidos a procesos de validación, limpieza, estandarización y enriquecimiento. Esta capa proporciona una fuente de verdad confiable para toda la organización.
* Gold (Curado): Almacena datos agregados y optimizados para el consumo final. Estos conjuntos de datos están listos para ser utilizados por sistemas de negocio, herramientas de análisis y modelos de Machine Learning.

El problema central que este ADR busca resolver es la coordinación de procesos secuenciales y dependientes que se extienden a través de tres dominios funcionales distintos: Ingesta de Datos, Lógica Financiera y Entrenamiento de Modelos de ML. Estos procesos forman una cadena de valor donde cada paso depende del éxito y la integridad del anterior. Un fallo, un retraso o una inconsistencia en cualquiera de las etapas compromete la validez de los resultados finales, desde los informes financieros hasta las predicciones de los modelos. Esto representa un riesgo operativo y reputacional inaceptable, donde la corrupción de datos no detectada podría conducir a informes financieros erróneos y predicciones de ML defectuosas, socavando la propuesta de valor central de NavOptima.

Por lo tanto, es imperativo seleccionar un patrón arquitectónico que gestione explícitamente estas dependencias y garantice la correcta ejecución de toda la cadena de procesamiento.

## Decisión

La selección de un patrón de comunicación y flujo de trabajo adecuado es una decisión estratégica que debe mitigar los riesgos de integridad, manejo de errores y auditabilidad identificados en el contexto. Un enfoque inadecuado podría llevar a fallos silenciosos, inconsistencias de datos y una falta de visibilidad que es inaceptable en un entorno de misión crítica como NavOptima.

Se adopta un patrón de Orquestación Centralizada, que será implementado utilizando el framework Apache Airflow.

Este enfoque implica la utilización de un componente central (el orquestador) que gestiona y supervisa la ejecución de los flujos de trabajo (workflows). El orquestador es responsable de iniciar tareas, gestionar sus dependencias, manejar reintentos en caso de fallos y proporcionar una visibilidad explícita y centralizada del estado de cada proceso.

Fundamentamos esta decisión en un análisis detallado de los requisitos del proyecto y los trade-offs entre diferentes patrones de arquitectura, como se justifica a continuación.

## Justificación

La elección del patrón de Orquestación Centralizada es una decisión fundamentada en principios de arquitectura de software y alineada directamente con los requisitos de negocio de NavOptima. No se trata de una preferencia tecnológica, sino de una respuesta calculada a las necesidades de integridad financiera, manejo de errores robusto y eficiencia operativa que definen el éxito del proyecto.

## Garantía de Integridad Financiera y Auditabilidad

El requisito más crítico del proyecto NavOptima es la necesidad de una auditabilidad completa en todos los procesos de datos financieros. Para cumplir con esta exigencia, es esencial contar con un sistema que imponga gobernanza y responsabilidad (accountability) sobre el ciclo de vida completo de los datos, un principio clave en la ingeniería de datos moderna (Housley et al., 2024, p. 59).

Un orquestador central, actuando como un "mediador" (Richards & Ford, 2020, p. 183), gestiona y controla activamente el flujo de trabajo. Esta centralización permite registrar la ejecución de cada tarea, sus parámetros y su resultado, creando una traza de auditoría inmutable y fácil de seguir. En contraste, un sistema basado en coreografía, donde los servicios interactúan implícitamente a través de eventos, dificulta enormemente la reconstrucción de una secuencia de operaciones, ya que el flujo de control está descentralizado y no es explícito. En un escenario de auditoría regulatoria, reconstruir el linaje de un único resultado financiero en un sistema coreografiado sería una tarea forense compleja y propensa a errores. En cambio, nuestro orquestador central proporcionará un registro de ejecución lineal y explícito, sirviendo como la fuente de verdad definitiva para cada cálculo. La orquestación nos proporciona la capacidad de demostrar, en cualquier momento, cómo se generó un dato específico, cumpliendo así con nuestros requisitos de auditoría.

## Manejo de Errores y Procesos Críticos de Negocio

Los flujos de datos financieros en NavOptima son procesos de negocio de misión crítica. En este contexto, los fallos no son una posibilidad, sino una eventualidad que debe ser gestionada de forma controlada y predecible. La comparación directa entre el patrón de orquestación (mediador) y el de coreografía (broker) revela deficiencias significativas en este último para nuestro caso de uso. La topología de broker se caracteriza por un pobre "Manejo de errores", una baja "Recuperabilidad" y un deficiente "Control de flujo de trabajo" (Richards & Ford, 2020, p. 183, Table 14-1).

La orquestación es el patrón preferido para procesos complejos y transaccionales que requieren una coordinación precisa, como en las sagas distribuidas. Al centralizar la lógica de compensación y reintentos, un orquestador puede garantizar la consistencia del sistema incluso ante fallos parciales, revirtiendo operaciones previas si un paso posterior fracasa (Richards & Ford, 2020, pp. 256-260). Esta capacidad de recuperación controlada es indispensable para mantener la integridad de nuestros datos financieros.

## Alineación con KPIs de Costo y Eficiencia Operativa

Desde una perspectiva de costo y eficiencia, NavOptima no puede permitirse un enfoque "Fire and Forget" (disparar y olvidar), que a menudo caracteriza a los sistemas puramente basados en eventos sin un control central. Los fallos silenciosos en un sistema coreografiado pueden pasar desapercibidos hasta que se manifiestan como costosas inconsistencias de datos. Esto se traduce directamente en un aumento del costo operativo (OpEx), ya que requiere la asignación de horas de ingeniería de alto valor para la reconciliación manual de datos, un esfuerzo que este patrón arquitectónico busca minimizar proactivamente.

La elección de Apache Airflow como implementación del orquestador se sustenta en su capacidad para definir dependencias explícitas entre tareas (Macey, 2024, Example 3-20). Esto garantiza que los procesos se ejecuten en la secuencia correcta y, fundamentalmente, que un fallo en una tarea detenga la cadena de ejecución de manera predecible. Esta característica evita la propagación de datos corruptos o incorrectos, minimizando el impacto de los errores y reduciendo significativamente el costo operativo asociado a la depuración y la recuperación manual.

Esta decisión arquitectónica, por lo tanto, se alinea con los principios de diseño para la robustez y la eficiencia, como se analizará en sus consecuencias.

## Consecuencias

Como dicta la "Primera Ley de la Arquitectura de Software", todo implica un trade-off (Richards & Ford, 2020, p. 20). La decisión de adoptar un patrón de Orquestación Centralizada, aunque sólidamente justificada, introduce un conjunto específico de ventajas y desventajas que el equipo de NavOptima debe gestionar activamente.

## Análisis de Trade-offs

Ventajas (Pros)	Desventajas (Contras)
Control Centralizado del Flujo de Trabajo: Proporciona una visibilidad completa y explícita de los procesos de negocio complejos, facilitando su comprensión y mantenimiento.<br><br>Manejo de Errores Simplificado: La lógica de reintentos, compensación y alertas se centraliza en el orquestador, en lugar de distribuirse entre múltiples servicios.<br><br>Alta Recuperabilidad y Auditabilidad: Facilita el reinicio de flujos desde un punto de fallo específico y simplifica enormemente el seguimiento de la traza de ejecución para fines de auditoría.<br><br>Desacoplamiento de la Lógica de Flujo: Los servicios individuales se centran únicamente en su tarea específica y no necesitan conocer el contexto del flujo de trabajo completo, lo que promueve su reutilización.	Punto Único de Fallo (SPOF): El orquestador se convierte en un componente crítico; su indisponibilidad detiene todos los flujos de trabajo. (Mitigación: se implementará una configuración de alta disponibilidad para Apache Airflow).<br><br>Acoplamiento al Orquestador: Los servicios, aunque se desacoplan entre sí, desarrollan un acoplamiento con la API del orquestador. (Este riesgo se mitigará mediante la definición de interfaces agnósticas y el uso de patrones de adaptador para aislar los servicios de la implementación específica de Airflow).<br><br>Potencial Cuello de Botella: Un alto volumen de flujos de trabajo concurrentes podría sobrecargar el orquestador. (Este riesgo se gestionará mediante el escalado proactivo de la arquitectura de Airflow y el monitoreo continuo del rendimiento para ajustar los recursos según la demanda).

El equipo de NavOptima ha evaluado y aceptado estos trade-offs. Las estrategias de mitigación mencionadas para las desventajas se incorporarán como parte del diseño detallado y el plan de implementación de la plataforma.

## Bibliografía

Housley, M., & Engineering, F. o. D. (2024). Fundamentals of Data Engineering. O'Reilly Media.

Kretz, A., Mazumdar, D., Balse, T., & Khong, A. (2023). Architecting Data and Machine Learning Platforms. O'Reilly Media.

Macey, T. (2024). Data Engineering Design Patterns. O'Reilly Media.

Richards, M., & Ford, N. (2020). Fundamentals of Software Architecture: An Engineering Approach. O'Reilly Media.
