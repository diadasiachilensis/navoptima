#  Análisis del Patrón de Diseño Strategy Aplicado a la Ingesta de Datos

## Introducción al Problema y la Solución Arquitectónica

La ingeniería de datos moderna opera en un ecosistema caracterizado por una creciente diversidad y complejidad de fuentes de datos. Las organizaciones deben procesar información proveniente de flujos de eventos en tiempo real (streaming), lotes de archivos (batch), y un sinnúmero de APIs externas. Esta heterogeneidad exige arquitecturas que no solo sean robustas y escalables, sino también flexibles y fáciles de mantener a lo largo del tiempo. Para afrontar estos desafíos, los ingenieros de datos pueden recurrir a los patrones de diseño de software, soluciones probadas y reutilizables que ofrecen un vocabulario común y un enfoque estructurado para resolver problemas recurrentes de diseño.

Uno de los patrones más fundamentales es el Patrón de Diseño Strategy. Este patrón "define una familia de algoritmos, encapsula cada uno de ellos y los hace intercambiables" [1]. Su propósito principal es permitir que el algoritmo varíe independientemente de los clientes que lo utilizan, desacoplando la lógica de negocio específica de su orquestación. Esta capacidad de intercambiar comportamientos en tiempo de ejecución es especialmente valiosa en la fase de ingesta de datos, donde los métodos para obtener información pueden cambiar o expandirse con frecuencia.

El caso de estudio central de este informe es el diagrama de clases UML "Patrón Strategy para Ingesta", que modela una solución para la ingesta de datos de múltiples fuentes. A través de este análisis, desglosaremos sus componentes, evaluaremos los beneficios arquitectónicos que proporciona y lo situaremos dentro del ciclo de vida de la ingeniería de datos, demostrando cómo un principio de diseño de software bien aplicado puede resolver un problema práctico y complejo de datos.

A continuación, se procederá a un análisis detallado de los componentes del diagrama y los principios de diseño que sustentan su eficacia y elegancia.

## Desglose del Diagrama UML: El Patrón Strategy en Acción

Un análisis arquitectónico del patrón Strategy exige deconstruir su estructura para revelar cómo la interacción de sus componentes materializa principios de diseño fundamentales. Este desglose no es meramente descriptivo; revela cómo el patrón implementa estos principios para construir un sistema desacoplado, mantenible y extensible. La estructura del diagrama es una implementación directa de uno de los pilares del diseño orientado a objetos.

El principio rector que da vida al patrón Strategy es "Programar para una Interfaz, no para una Implementación" [1]. Este concepto dicta que el código debe depender de abstracciones (interfaces o clases abstractas) en lugar de clases concretas. La aplicación de este principio tiene consecuencias directas y significativas en la calidad del diseño:

* Depender de Implementaciones Concretas (Acoplamiento Fuerte):
  * El código cliente está ligado a una lógica específica.
  * Cualquier cambio en la implementación (por ejemplo, cambiar la fuente de una API a un flujo de Kafka) requiere modificar el código cliente.
  * Añadir nuevos algoritmos obliga a alterar la lógica existente, a menudo introduciendo complejas estructuras condicionales (`if/else` o `switch`).
* Depender de Interfaces (Acoplamiento Débil):
  * El código cliente solo conoce el "contrato" (los métodos definidos en la interfaz), no los detalles de su cumplimiento.
  * Las implementaciones pueden ser intercambiadas o añadidas en tiempo de ejecución sin afectar al cliente.
  * El sistema se vuelve extensible, ya que se pueden introducir nuevos comportamientos simplemente creando nuevas clases que implementen la interfaz.

![uml](UML.png)

> **Figura 1:** Implementación del Patrón Strategy en el componente Ingestion Worker. Se ilustra el desacoplamiento entre el ejecutor (Contexto) y los algoritmos de extracción (Estrategias Concretas). Esta estructura permite la intercambiabilidad de fuentes de datos (AIS, Clima, Bunker) y garantiza el Principio de Abierto/Cerrado (OCP), permitiendo añadir nuevos proveedores sin modificar la lógica central del sistema

### El Contexto: `IngestionWorker`

El `IngestionWorker` actúa como el Contexto en el patrón Strategy. Su función es orquestar el proceso de ingesta de datos utilizando una estrategia específica que se le proporciona.

El aspecto más crucial de su diseño es su total ignorancia sobre la implementación concreta del algoritmo de ingesta. Como se anota en el diagrama, "El contexto no sabe CÓMO se obtienen los datos, solo invoca `fecth()`". Esta separación se logra mediante la delegación: el `IngestionWorker` no implementa la lógica de obtención de datos, sino que delega esa responsabilidad al objeto de estrategia que contiene. Este es un claro ejemplo del principio de diseño que aconseja "Favorecer la Composición sobre la Herencia" [1], ya que el `IngestionWorker` se compone con una estrategia en lugar de heredar su comportamiento.

### La Estrategia Abstracta: `IngestionStrategy`

La interfaz `IngestionStrategy` es la Estrategia Abstracta y el corazón del patrón en este diseño. Define un contrato común que todas las estrategias de ingesta concretas deben cumplir. En este caso, el contrato consiste en un único método: `fecth()`.

Esta abstracción es el punto clave de desacoplamiento. Al programar el `IngestionWorker` para que utilice esta interfaz, garantizamos que pueda trabajar con cualquier clase que la implemente. Esto permite que los algoritmos de ingesta sean completamente intercambiables, proporcionando una enorme flexibilidad al sistema [1]. El `IngestionWorker` no depende de `AisStrategy` ni de `WeatherStrategy`, sino de la abstracción `IngestionStrategy`.

### Las Estrategias Concretas: `AisStrategy` y `WeatherStrategy`

Las clases `AisStrategy` y `WeatherStrategy` son las Estrategias Concretas. Cada una de ellas encapsula un algoritmo específico para obtener un tipo de dato particular, cumpliendo con el contrato establecido por la interfaz `IngestionStrategy`.

* `AisStrategy` contendría la lógica para conectarse a una fuente de datos de AIS (Sistema de Identificación Automática de buques) y obtener su información.
* `WeatherStrategy` encapsularía el código necesario para consultar una API meteorológica y extraer los datos relevantes.

Cada clase es una unidad cohesiva y autónoma de funcionalidad, responsable de una única tarea: la ingesta de un tipo de dato específico. El análisis de estos componentes demuestra cómo el patrón Strategy organiza el código de una manera lógica y desacoplada, lo que a su vez habilita una serie de beneficios arquitectónicos de alto nivel.

## Evaluación de Beneficios Arquitectónicos

Los beneficios arquitectónicos evaluados a continuación no surgen por accidente; son el resultado directo de aplicar rigurosamente principios de diseño como "Programar para una Interfaz" y "Favorecer la Composición", materializando sus promesas teóricas en características sistémicas medibles ("-ilidades") [2]. La aplicación del patrón Strategy en el contexto de la ingesta de datos ofrece beneficios tangibles que mejoran la robustez y la vida útil del sistema.

1. Flexibilidad y Extensibilidad. El diseño resultante es inherentemente flexible. El `IngestionWorker` puede cambiar su comportamiento dinámicamente simplemente cambiando el objeto de estrategia que utiliza. Más importante aún, el sistema es "abierto a extensiones". Como se indica en las notas del diagrama, si surge un nuevo requisito para ingerir datos de precios de combustible (BunkerPriceStrategy), se puede añadir una nueva clase de estrategia sin realizar ninguna modificación en el `IngestionWorker` existente. Esto es fundamental para construir una arquitectura evolutiva, capaz de adaptarse a nuevos requisitos de negocio con un impacto mínimo en el código base y un riesgo reducido de introducir errores.

2. Alto Desacoplamiento y Cohesión. El patrón promueve un diseño "débilmente acoplado" (loosely coupled), un principio fundamental para sistemas mantenibles [1]. El `IngestionWorker` (el cliente) y las estrategias concretas (los algoritmos) no están directamente ligados entre sí. Este desacoplamiento no es solo un principio de codificación, sino la implementación táctica necesaria para alcanzar características arquitectónicas clave como la Capacidad de Prueba (Testability), la Capacidad de Despliegue (Deployability) y la Mantenibilidad (Maintainability) [2]. Las estrategias pueden evolucionar y ser probadas de forma aislada sin afectar al `IngestionWorker`, lo que simplifica las pruebas unitarias y reduce la propagación de cambios. Al mismo tiempo, cada estrategia exhibe una alta cohesión, ya que toda la lógica relacionada con una fuente de datos específica está encapsulada en una sola clase.

3. Simplificación y Responsabilidad Única. El `IngestionWorker` se ve notablemente simplificado. En lugar de contener una lógica condicional compleja para manejar cada tipo de fuente de datos, su única responsabilidad es orquestar la ejecución de una estrategia. Esto se alinea directamente con el Principio de Responsabilidad Única, que postula que una clase debe tener una sola razón para cambiar. La responsabilidad del `IngestionWorker` es la orquestación del proceso de ingesta, no los detalles de cómo se realiza esa ingesta. Esta delegación de responsabilidad hace que el código sea más limpio, más fácil de entender y menos propenso a errores.

Estos beneficios teóricos se traducen en ventajas prácticas directas cuando se aplican al dominio de la ingeniería de datos, donde la agilidad para incorporar nuevas fuentes es un factor competitivo clave.

## Aplicación en el Ciclo de Vida de la Ingeniería de Datos

Para contextualizar plenamente el valor de este patrón, es útil situarlo dentro del Ciclo de Vida de la Ingeniería de Datos, un modelo que estructura el flujo de datos en etapas: Ingestion, Transformation y Serving [3, 4]. La fase de Ingestion es el punto de entrada para todos los datos y, a menudo, la más frágil y compleja debido a su dependencia de sistemas externos. Por esta razón, la aplicación de patrones de diseño robustos como el Strategy en esta etapa es de vital importancia para la fiabilidad de todo el pipeline de datos.

Un enfoque monolítico, basado en estructuras condicionales complejas para gestionar múltiples fuentes, a menudo degenera en un anti-patrón arquitectónico conocido como "la gran bola de lodo" (big ball of mud) [2]. El siguiente cuadro compara el enfoque modular del patrón Strategy con esta alternativa de alto acoplamiento.

Arquitectura Modular (Patrón Strategy)	Arquitectura Monolítica (Acoplamiento Fuerte)
Modular: Cada fuente de datos es una estrategia encapsulada.	Rígido: Un único bloque de código gestiona todas las fuentes.
Extensible: Añadir una nueva fuente implica crear una nueva clase, sin modificar el código existente.	Propenso a errores: Añadir o modificar una fuente requiere alterar una lógica condicional compleja, aumentando el riesgo de regresiones.
Mantenible: El código es fácil de entender, depurar y modificar debido a la separación de responsabilidades.	Difícil de mantener: A medida que crecen las fuentes, el bloque condicional se vuelve inmanejable y difícil de razonar.
Fácil de probar: Cada estrategia puede ser probada de forma aislada (pruebas unitarias).	Difícil de probar: Probar una fuente de datos requiere probar todo el bloque condicional, lo que complica el aislamiento de fallos.

### Casos de Uso en Plataformas de Datos Modernas

El patrón Strategy no se limita a las fuentes de datos del ejemplo. Su flexibilidad lo convierte en una solución ideal para una variedad de escenarios de ingesta en plataformas de datos modernas, donde coexisten múltiples tecnologías de procesamiento y almacenamiento [5, 6]. Algunos ejemplos de estrategias adicionales podrían ser:

* `KafkaStreamStrategy`: Para consumir datos de un topic de Kafka, manejando la lógica de conexión y deserialización de mensajes en tiempo real.
* `S3BatchStrategy`: Para procesar archivos por lotes (CSV, Parquet, JSON) desde un bucket de almacenamiento de objetos como Amazon S3, encapsulando la lógica de listado y lectura de archivos.
* `CDCStrategy`: Para implementar la Captura de Cambios en los Datos (Change Data Capture) desde una base de datos transaccional, procesando el flujo de eventos de inserción, actualización y eliminación.
* `RestApiStrategy`: Para obtener datos de una API REST de terceros, gestionando la autenticación, paginación y manejo de límites de peticiones (rate limiting).

La implementación del patrón Strategy es, por tanto, una herramienta táctica clave que permite a los ingenieros de datos construir sistemas de ingesta que no solo son funcionalmente correctos hoy, sino que están arquitectónicamente preparados para evolucionar mañana.

## Conclusión

Este informe ha demostrado que el Patrón de Diseño Strategy, cuando se aplica al desafío de la ingesta de datos, es mucho más que una simple técnica de programación. Es una manifestación práctica de principios fundamentales de la arquitectura de software, como el desacoplamiento, la programación orientada a interfaces y la extensibilidad. Al encapsular algoritmos de ingesta intercambiables, este patrón transforma un componente potencialmente rígido y complejo en un sistema modular, flexible y resiliente al cambio.

La adopción proactiva de patrones como este es una decisión estratégica que alinea la ingeniería de datos con los objetivos de negocio. Mitiga riesgos como la dependencia de un proveedor de datos específico (vendor lock-in) o el alto coste de adaptación a nuevos formatos, al tiempo que habilita capacidades clave como la incorporación rápida de nuevas fuentes de datos. Esta elección se alinea con la Segunda Ley de la Arquitectura de Software, que establece: "El porqué es más importante que el cómo" [2]. En este caso, el "porqué" es la búsqueda de agilidad y escalabilidad empresarial.

Además, construir sistemas modulares y extensibles desde el principio evita la necesidad de justificar costosas refactorizaciones en el futuro, un proceso que a menudo encuentra fricción política y empresarial cuando un diseño monolítico y frágil inevitablemente deja de satisfacer las nuevas demandas del negocio [7].

En definitiva, el diseño analizado no es solo una solución táctica para la ingesta, sino un modelo ejemplar para construir componentes robustos y preparados para el futuro dentro de cualquier plataforma de datos moderna.


--------------------------------------------------------------------------------


## Bibliografía

[1] Freeman, E., Robson, E., Bates, B., & Sierra, K. (2004). Head First Design Patterns. O'Reilly Media.

[2] Richards, M., & Ford, N. (2020). Fundamentals of Software Architecture. O'Reilly Media.

[3] Housley, M., & Reis, J. (2022). Fundamentals of Data Engineering. O'Reilly Media.

[4] Documentación Interna del Proyecto NavOptima. (2023).

[5] Chollet, F., et al. (2023). Architecting Data and Machine Learning Platforms. O'Reilly Media.

[6] Housley, M. (2024). Data Engineering Design Patterns. O'Reilly Media.

[7] Ford, N., Klein, M., & Richards, M. (2021). Software Architecture: The Hard Parts. O'Reilly Media.
