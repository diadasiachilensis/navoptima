### 🏛️ COLUMNA: DESIGN (Bloqueante \- El "Thinking")

*Estas tarjetas deben tener adjunto un archivo (PDF, PNG, MD) antes de moverse.*

**Tarjeta 1: Redactar ADR-001: Orquestación Centralizada**

* **Columna Sugerida:** Design (Prioridad Alta)  
* **Acción:** Documentar la decisión arquitectónica de usar un Orquestador (Airflow) vs. Coreografía.  
* **Criterios de Aceptación Técnicos:**  
- [x] Documento ADR creado siguiendo formato estándar (Status, Context, Decision, Consequences).  
- [x] Justificación explícita de "Auditability \> Latency" citando *Richards & Ford*.  
- [x] Definición de que un fallo en un paso detiene el proceso para preservar la integridad financiera.

**Tarjeta 2: Diseñar Diagrama C4 (Nivel Contenedores) \+ Medallion**

* **Columna Sugerida:** Design  
* **Acción:** Dibujar la topología de contenedores y flujo de datos.  
* **Criterios de Aceptación Técnicos:**  
- [x] Diagrama C4 Nivel 2 exportado.  
- [x] Segmentación visual clara de Capas: Bronze (Raw), Silver (Enriched), Gold (Business) según *Gorelli*.  
- [x] Protocolos definidos en las flechas (ej. `HTTPS` para API Clima, `TCP` para PostgreSQL).

**Tarjeta 3: Modelar Patrón Strategy para Ingesta (UML)**

* **Columna Sugerida:** Design  
* **Acción:** Crear diagrama de clases para el módulo de extracción.  
* **Criterios de Aceptación Técnicos:**  
- [x] Diagrama UML de Clases adjunto.  
- [x] Interfaz `IngestionStrategy` definida con método abstracto `fetch()`.  
- [x] Clases concretas `AisStrategy` y `WeatherStrategy` implementando la interfaz.  
- [x] Cumplimiento de Open/Closed Principle verificado visualmente.

**Tarjeta 4: Diseñar Esquema Relacional SCD Tipo 2**

* **Columna Sugerida:** Design  
* **Acción:** Diseñar el DER para la base de datos analítica.  
* **Criterios de Aceptación Técnicos:**  
- [x] Diagrama Entidad-Relación (DER) adjunto.  
- [x] Tabla `dim_vessel` incluye columnas: `valid_from` (timestamp), `valid_to` (timestamp), `is_current` (boolean).  
- [x] Relación definida entre `fact_fuel_consumption` y `dim_vessel` usando claves subrogadas, no IDs naturales.

---

### 🔨 COLUMNA: BACKLOG (Implementation \- El "Doing")

*Solo tomas estas tarjetas cuando las de arriba están en "Done".*

**Tarjeta 5: Implementar Ingesta Idempotente & Pydantic**

* **Columna Sugerida:** Backlog  
* **Acción:** Codificar los workers de extracción en Python.  
* **Criterios de Aceptación Técnicos:**  
- [ ] Modelos Pydantic (`VesselSchema`, `WeatherSchema`) implementados con tipos estrictos.  
- [ ] Mecanismo de **Idempotencia**: Si corro el script 2 veces con el mismo input, no duplica registros (*Reis & Housley*).  
- [ ] Manejo de Errores: Los datos inválidos se envían a una tabla/archivo `dead_letter_queue` sin romper el proceso.

**Tarjeta 6: Codificar Lógica Bitemporal con Decimal**

* **Columna Sugerida:** Backlog  
* **Acción:** Desarrollar el cálculo de costos en la Capa Silver.  
* **Criterios de Aceptación Técnicos:**  
- [ ] Uso exclusivo de `from decimal import Decimal` para montos monetarios (Prohibido `float`).  
- [ ] Tabla de destino registra dos tiempos: `event_time` (del sensor) y `processing_time` (del sistema) (*Khraisha*).

**Tarjeta 7: Implementar Patrón Write-Audit-Publish (WAP)**

* **Columna Sugerida:** Backlog  
* **Acción:** Orquestar la promoción de datos a la Capa Gold.  
* **Criterios de Aceptación Técnicos:**  
- [ ] Pipeline escribe primero en tabla `staging_gold`.  
- [ ] Script de Auditoría verifica reglas (ej. `consumo > 0`, `costo < 1M`).  
- [ ] Si Auditoría \== OK, transacción mueve datos a `prod_gold`. Si falla, alerta.

**Tarjeta 8: Configurar MLflow y Entrenamiento Comparativo**

* **Columna Sugerida:** Backlog  
* **Acción:** Crear script de entrenamiento de modelos.  
* **Criterios de Aceptación Técnicos:**  
- [ ] Script entrena 3 modelos: Regresión Lineal, XGBoost, Random Forest.  
- [ ] MLflow UI muestra métricas (RMSE, MAE) comparadas para cada corrida.  
- [ ] El mejor modelo se serializa automáticamente (`.pkl` o formato MLflow).

---

### 🧪 COLUMNA: TESTING (QA \- La "Proof")

*El DoD (Definition of Done) requiere que esto pase en verde.*

**Tarjeta 9: Implementar Tests de Slicing (Drift)**

* **Columna Sugerida:** Testing  
* **Acción:** Crear suite de tests para escenarios críticos.  
* **Criterios de Aceptación Técnicos:**  
- [ ] Test específico para Slice "Condiciones Extremas" (Viento \> 40 nudos).  
- [ ] El test falla si el error del modelo en ese slice supera el umbral definido (aunque el promedio global sea bueno) (*Chip Huyen*).

**Tarjeta 10: Configurar Fitness Functions (ArchUnit)**

* **Columna Sugerida:** Testing  
* **Acción:** Automatizar la validación de reglas de arquitectura.  
* **Criterios de Aceptación Técnicos:**  
- [ ] Script en CI/CD que analiza las importaciones del código.  
- [ ] **Regla:** El código en carpeta `/bronze` NO puede importar de `/gold`.  
- [ ] **Regla:** No existen ciclos de dependencia entre módulos.

---
