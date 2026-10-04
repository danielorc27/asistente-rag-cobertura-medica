# Informe de Revisión Arquitectónica — ESPECIFICACION.md

**Proyecto:** Asistente Inteligente para Validación de Cobertura de Planes de Salud mediante RAG
**Fecha:** 2026-07-17
**Estado:** APROBADO (2026-07-17) — decisiones registradas en ESPECIFICACION.md, capítulo 14 (Addendum). Respuestas del autor: /query con `affiliate_id` + `question`; una sola llamada LLM; `EvidenceStrength` (INSUFFICIENT/PARTIAL/STRONG) en lugar de confidence numérico; /reindex protegido por API Key configurable; implementación inicia con insumos disponibles; testing por fase con consolidación E2E al final.

---

## 1. Resumen Ejecutivo

El documento es sólido en intención: define capas, contratos, restricciones de dependencias, pipeline RAG con razonamiento explícito, guardrails y un roadmap secuencial. Es implementable.

Sin embargo, contiene **una contradicción estructural sobre la dirección de dependencias**, **tres orquestadores en conflicto**, **ambigüedad sobre dónde viven las interfaces y los factories**, y **varios vacíos de diseño en los componentes de razonamiento** (Intent Analyzer, Coverage Decision Engine, Response Validator, nivel de confianza) que, si no se resuelven antes de codificar, producirán retrabajos justo en el "corazón del sistema".

Además existe **un bloqueante operativo**: los insumos de la prueba (`documents/*.docx`, `data/BD_afiliados.xlsx`) **no existen en el directorio del proyecto**. Solo está `ESPECIFICACION.md`.

---

## 2. Hallazgos Críticos (resolver antes de implementar)

### C1. Contradicción en la dirección de dependencias (§2.1 vs §2.3/§10.13/§13.10)

- §2.1 declara: *"Toda dependencia deberá apuntar hacia el dominio. Nunca en dirección contraria"* — esto es Clean Architecture correcta.
- Pero §2.3, §10.13 y §13.10 dibujan: `Presentation → Application → Domain → Infrastructure`, es decir, **Domain dependiendo de Infrastructure**. Eso es arquitectura en capas tradicional y viola el propio Dependency Inversion Principle que el documento exige (§2.12, §10.3).

**Impacto:** si se implementa el diagrama literalmente, el dominio importaría infraestructura y toda la promesa de la "Regla de Oro" (§2.13) se rompe.

**Recomendación:** corregir el diagrama a la forma canónica:

```
Presentation → Application → Domain ← Infrastructure
```

Infrastructure **implementa** las interfaces (ports) declaradas en Domain; nunca es un destino de dependencia de Domain. La frase "Un Repository puede utilizar Pandas" es correcta solo si se entiende que `ExcelAffiliateRepository` (Infrastructure) implementa `AffiliateRepository` (Domain).

### C2. Tres orquestadores compitiendo por la misma responsabilidad

- §3.12: `CoverageAnalysisService` es *"el único componente autorizado para coordinar todo el proceso"*.
- §4.6/§7.3: `AnalyzeCoverageUseCase` *"coordina consultar afiliado, recuperar contexto, generar prompt, llamar al LLM, construir respuesta"*.
- §7.17: el `Reasoning Engine` *"actuará como punto central de orquestación"*.

Las tres definiciones se superponen casi al 100%. Un desarrollador no puede saber dónde poner la coordinación — violando la propia regla §4.14 ("ubicar un archivo en menos de un minuto").

**Recomendación:** definir jerarquía explícita de una sola vez:
1. `AnalyzeCoverageUseCase` (Application/use_cases): punto de entrada único, secuencia de alto nivel.
2. `ReasoningEngine` (Application/reasoning): sub-orquestador exclusivamente de la etapa de razonamiento (intent → evidence → decisión preliminar).
3. **Eliminar `CoverageAnalysisService`** o declararlo alias/renombre del Use Case. Mantener ambos es duplicación garantizada.

También unificar el nombre del use case: aparece como `ResponderConsultaUseCase` (§2.4) y `AnalyzeCoverageUseCase` (§4.6, §7.3). Adoptar **`AnalyzeCoverageUseCase`** (consistente con la convención inglesa del resto de clases).

### C3. Ubicación ambigua de interfaces y factories

- §4.6 define `application/interfaces/` y §4.7 define `domain/repositories/` y `domain/providers/` — **ambos contienen interfaces**. ¿Dónde vive `LLMProvider`? El documento lo pone en `domain/providers/` (§4.7) pero también habla de "interfaces utilizadas por Application" sin criterio de separación.
- §3.15 define factories (`LLMFactory`, `VectorStoreFactory`...) pero la Fase 2 del roadmap (§12.4, "Dominio") incluye *"crear Factories"*. Un factory que instancia `OpenAIProvider` **no puede vivir en Domain** sin violar §5.17 (prohibido importar OpenAI en Domain).

**Recomendación:**
- Regla única: **todas las interfaces (ports) viven en Domain** (`domain/repositories/`, `domain/providers/`). Eliminar `application/interfaces/` o reservarlo solo para contratos internos de orquestación que Domain no necesita conocer (y documentar el criterio).
- **Factories viven en Infrastructure** (o en `config/dependencies.py` como composition root). Quitar "Factories" de las actividades de la Fase 2.
- Declarar explícitamente que `config/dependencies.py` es el **composition root**: es el único lugar autorizado a importar de todas las capas para cablear implementaciones. Sin esta excepción explícita, el propio DI viola las reglas de importación del documento.

### C4. Reglas de negocio en Application en lugar de Domain

§4.6 ubica `reasoning/` (con `CoverageDecisionEngine`, `RuleEngine`, `EvidenceEvaluator`) en Application, pero §2.4 dice que Domain contiene *"reglas de negocio puras"*. Las reglas de cobertura (carencia, vigencia, estado del afiliado, exclusiones) **son** reglas de negocio puras y determinísticas — exactamente lo que §13.12 exige implementar en código.

**Recomendación:** las reglas evaluables determinísticamente (vigencia, carencia, estado) van a **Domain** como servicios de dominio o métodos de entidades. El `ReasoningEngine` en Application solo orquesta: llama a las reglas de dominio, al retriever y al prompt builder.

### C5. Insumos de la prueba ausentes (bloqueante operativo)

El directorio contiene únicamente `ESPECIFICACION.md`. No existen `documents/DOC1..DOC3.docx` ni `data/BD_afiliados.xlsx`. Sin ellos:
- No puede diseñarse con certeza la entidad `Afiliado` (el esquema de columnas del Excel es desconocido).
- Las Fases 4–7 no son verificables.

**Recomendación:** obtener los archivos antes de la Fase 2 (el diseño de entidades depende del esquema real del Excel). Si no están disponibles, definir un esquema asumido y documentarlo como supuesto.

---

## 3. Vacíos de Diseño (decisiones que el documento no toma)

### V1. Identificación del afiliado — el vacío más importante del flujo

§7.5 espera extraer "Juan Pérez" del texto libre, pero:
- Nombres no son identificadores únicos (homónimos).
- Es dato sensible de salud: resolver afiliado por coincidencia difusa de nombre es un riesgo funcional y de privacidad.
- El contrato de `POST /query` no está definido: ¿la consulta llega solo como texto libre o con `affiliate_id` estructurado?

**Recomendación:** exigir identificador estructurado en el request DTO (`affiliate_id` / número de documento) y usar el Intent Analyzer solo para procedimiento e intención. Si la prueba técnica exige extraer el afiliado del texto, definir política explícita de desambiguación (0 matches → error controlado; >1 match → solicitar aclaración).

### V2. ¿El Intent Analyzer usa LLM o no?

Los diagramas (§7.4, §7.16) muestran una única llamada al LLM al final. Pero interpretar lenguaje natural sin frases exactas (§4.1) no es viable con regex/keywords de forma robusta. Si el Intent Analyzer usa el LLM, hay **dos llamadas al modelo** y los diagramas son incorrectos; si no lo usa, el requisito §4.1 queda comprometido.

**Recomendación:** aceptar explícitamente que el Intent Analyzer hace una llamada LLM ligera (extracción estructurada con salida JSON, modelo económico configurable) y actualizar los diagramas. Es coherente con §13.12: la extracción de entidades desde texto libre es precisamente donde el LLM aporta valor.

### V3. Coverage Decision Engine: decidir sobre texto no estructurado

§7.9 exige una decisión preliminar **antes** del LLM cruzando "reglas documentales" — pero las reglas documentales son chunks de texto libre. Un motor determinístico no puede evaluar texto no estructurado.

**Recomendación:** delimitar el alcance del engine: la decisión preliminar se construye **solo con datos estructurados del afiliado** (estado activo, vigencia, carencia calculable, plan) y produce estados como `BLOCKED_BY_AFFILIATE_STATUS`, `NEEDS_DOCUMENT_ANALYSIS`. La interpretación de reglas documentales queda a cargo del LLM con la evidencia recuperada. Documentar esto evita intentar construir un rule-engine imposible.

### V4. Nivel de confianza (`confidence: 0.94`) sin definición

§7.13 exige un número que ningún componente del diseño sabe producir. Los LLM no emiten confianza calibrada; los scores de similitud del retrieval no son probabilidad de corrección. Un número inventado es precisamente la "falsa precisión" que el documento prohíbe.

**Recomendación:** definir la fórmula (p. ej., función de: score medio de similitud del top-k, suficiencia declarada por el Evidence Evaluator, y consistencia de la validación) **o** reemplazarlo por un enum cualitativo (`HIGH/MEDIUM/LOW`) derivado de reglas explícitas. Documentar la elección.

### V5. Response Validator: "detectar alucinaciones" sin mecanismo

§7.12 lista validaciones de dos naturalezas distintas: unas determinísticas (respuesta vacía, formato, existencia de citas, que las citas referencien chunk_ids realmente recuperados) y otras semánticas ("contradice la evidencia", "alucinaciones evidentes") que requerirían un segundo LLM-judge.

**Recomendación:** para la v1, implementar solo las validaciones determinísticas + verificación de que toda cita apunte a un chunk realmente entregado en el prompt. Dejar el juez semántico como evolución declarada. Definir también la política de fallo: ¿reintento (cuántos)? ¿respuesta degradada ("no fue posible generar respuesta verificable")? Hoy solo dice "error controlado".

### V6. Contrato del LLMProvider demasiado estrecho para el diseño

§3.8 define `LLMProvider` como "recibir prompt → devolver texto", pero §7.13 exige respuesta estructurada JSON. Sin soporte de salida estructurada en el contrato (JSON mode / tool use), el parsing será frágil.

**Recomendación:** el contrato debe ser `generate(prompt: PromptDTO) -> LLMResult` con soporte de salida estructurada (schema esperado) y metadatos (modelo, tokens, latencia — necesarios para §7.18 y §9.14). Incluir política de reintento ante JSON inválido y timeout/retry ante fallos del proveedor (hoy solo aparecen en pruebas §11.13, nunca en diseño).

### V7. Retrieval sin umbral de relevancia

`TOP_K_RESULTS` siempre devuelve K chunks, aun si ninguno es relevante. El Evidence Evaluator (§7.8) debe juzgar "suficiencia" pero no recibe señal para hacerlo.

**Recomendación:** el resultado del retrieval debe incluir el score de similitud, y agregar `MIN_SIMILARITY_SCORE` a la configuración. "Cero chunks sobre el umbral" es la señal natural de "evidencia insuficiente".

### V8. Invalidación del índice al cambiar parámetros

El hash por documento (§6.11) detecta cambios del documento, pero no detecta cambios de `EMBEDDING_MODEL`, `CHUNK_SIZE` o `CHUNK_OVERLAP`. Cambiar el modelo de embeddings deja un índice silenciosamente incompatible (vectores no comparables).

**Recomendación:** persistir junto al índice un manifiesto (`embedding_model`, `chunk_size`, `chunk_overlap`, versión del pipeline). Si el manifiesto no coincide con la configuración actual, el índice se considera inválido → reindexación FULL. Además, al reindexar un documento modificado, **eliminar primero sus chunks anteriores** por `document_id` (el diseño menciona `delete` en VectorStore pero nunca define esta secuencia).

### V9. Trazabilidad: exigida pero sin persistencia definida

§7.18/§13.3 exigen poder reconstruir cada decisión (consulta, afiliado, chunks, modelo, versión de prompt), pero ningún componente ni carpeta define **dónde se guarda** esa traza. Con "persistencia de usuarios" fuera de alcance (§9), hay ambigüedad.

**Recomendación:** para la v1, trazabilidad = (a) el propio `CoverageResponse` transporta la evidencia y metadatos, y (b) log estructurado (JSON) por consulta con un `trace_id`. Declararlo explícitamente. Cuidado con §9.18: la traza contiene datos del afiliado → definir qué campos se anonimizan en logs.

### V10. Ambigüedad en §6.12 sobre embeddings por lotes

*"Nunca generar embeddings de múltiples documentos simultáneamente"* leído literalmente prohíbe el batching de la API de OpenAI, que es la práctica correcta (menor costo/latencia) y que el propio `EmbeddingProvider` promete ("procesar listas", §3.6).

**Recomendación:** reformular: "un embedding por chunk; nunca un embedding de un documento completo". El batching de chunks en una sola llamada API está permitido y es deseable.

---

## 4. Riesgos y Decisiones Mejorables

### R1. Testing como Fase 7 contradice el propio documento

§12.14 exige que **cada fase** "pase todas las pruebas" para considerarse completa, pero las pruebas se construyen recién en la Fase 7. Además §13.14 afirma que "la calidad se construye desde el diseño". Dejar los tests al final es el anti-patrón que el documento condena.

**Recomendación:** cada fase (2–6) entrega sus pruebas unitarias/integración junto con el código. La Fase 7 queda para E2E, cobertura consolidada y casos límite. Esto no altera el orden de fases, solo redistribuye la actividad de testing.

### R2. `POST /reindex` sin protección

Con autenticación fuera de alcance, un endpoint público que reconstruye el índice es destructivo y costoso (llamadas de embeddings). **Recomendación mínima:** token estático por header (`X-Admin-Token` desde `.env`) o dejarlo solo como script CLI (`scripts/rebuild_index.py`) en la v1, y documentar la decisión.

### R3. Datos sensibles de salud

El sistema procesa datos de salud de afiliados (dato sensible bajo la Ley 1581/2012 en Colombia). §9.18 menciona anonimizar logs pero no define qué campos. **Recomendación:** lista explícita de campos nunca-logueables (nombre, documento, diagnósticos) y un filtro de logging centralizado que lo garantice, en lugar de confiar en disciplina por llamada.

### R4. Triple definición de los mismos datos (Entity / DTO / Schema)

Domain puro (dataclasses) + DTOs Pydantic en Application + Schemas Pydantic en Presentation implica escribir tres veces `Afiliado` y sus mapeos. Es el costo aceptado de la arquitectura elegida — **aceptable**, pero debe presupuestarse y crear mappers explícitos por capa para que la duplicación sea controlada y no accidental.

### R5. Redundancia de herramientas: Black + Ruff

`ruff format` reemplaza a Black (misma filosofía, una herramienta menos). Menor, pero coherente con §5.19 ("¿puede reemplazarse fácilmente?"). **Recomendación:** usar solo Ruff (lint + format). Si se mantiene Black, no es un error.

### R6. Inconsistencias menores del documento

- La numeración de capítulos reinicia y colisiona (el cap. 1 termina en "§11 Regla Principal" y sigue "§2. Arquitectura").
- Logging aparece asignado a tres lugares: `config/logging.py` (§4.10), `infrastructure/logging/` (§4.8) y capa "Shared" en la tabla §5.16. Definir: configuración en `config/`, ningún wrapper en Infrastructure salvo necesidad real.
- El metadato `page` (§6.10) no existe en `.docx`; usar sección/heading si se quiere granularidad.
- "Historial" aparece una sola vez (§3.9) sin diseño de sesiones: declarar explícitamente fuera de alcance v1.
- No existe un golden set de preguntas/respuestas esperadas pese a que §8.19 exige evaluar cambios de prompts. Crear un mini conjunto de evaluación (10–20 casos con respuesta esperada) como fixture — es además la mejor evidencia para la prueba técnica (§11.19).

---

## 5. Decisiones que se validan como correctas

Para balance del informe, estos puntos están bien resueltos y no requieren cambio:

- Separación ingesta/consulta con indexación idempotente por hash (§6).
- Ports & Adapters para LLM, embeddings, vector store, loaders y repositorio de afiliados — correcto para los requisitos de sustitución (§3).
- Prompt modular versionado con guardrails como componente de primera clase (§8).
- Manejo explícito de incertidumbre como resultado válido del dominio (§7.15, §13.5).
- Configuración centralizada tipada con pydantic-settings y `.env.example` (§9).
- Stack pragmático y proporcional al problema (FastAPI, Chroma local, python-docx, sin Kubernetes ni microservicios).

---

## 6. Preguntas que requieren decisión del autor antes de implementar

1. **Contrato de `POST /query`**: ¿`affiliate_id` estructurado en el request (recomendado) o extracción desde texto libre?
2. **Doble llamada LLM**: ¿se aprueba que el Intent Analyzer use una llamada LLM de extracción (recomendado) o debe ser 100% determinístico?
3. **Confianza**: ¿fórmula numérica definida o enum cualitativo `HIGH/MEDIUM/LOW` (recomendado)?
4. **`/reindex`**: ¿endpoint con token estático o solo script CLI en v1?
5. **Insumos**: ¿cuándo estarán disponibles `documents/` y `BD_afiliados.xlsx`? Sin el Excel real, el esquema de `Afiliado` será un supuesto documentado.
6. **Testing por fase** (R1): ¿se aprueba redistribuir las pruebas dentro de cada fase?

---

## 7. Veredicto

**Arquitectura APROBABLE CON CORRECCIONES.** Ninguna corrección invalida el enfoque general (Clean Architecture + RAG + razonamiento explícito); todas son resolubles editando el ESPECIFICACION.md antes de la Fase 1. Los puntos C1–C4 y V1–V6 deben quedar decididos antes de escribir código, porque afectan interfaces del dominio y el contrato de la API — exactamente las piezas que el documento declara inmutables una vez definidas (§13.7).
