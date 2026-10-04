# ESPECIFICACION.md

# Proyecto
## Asistente Inteligente para Validación de Cobertura de Planes de Salud mediante RAG

---

# 1. Visión General

## Propósito

Este documento define la arquitectura, estándares de desarrollo, decisiones técnicas, restricciones, convenciones y lineamientos que deberán seguirse durante el desarrollo del proyecto.

Este documento tiene prioridad sobre cualquier decisión automática del modelo.

Ante cualquier duda de implementación siempre deberá prevalecer la arquitectura y principios definidos aquí.

---

# 2. Contexto

La solución corresponde a una prueba técnica para un cargo de Ingeniero de IA / Desarrollador de Sistemas Agénticos y RAG.

El problema consiste en automatizar el proceso mediante el cual un analista determina si un procedimiento médico solicitado por un afiliado está cubierto por su plan de salud.

Actualmente dicho proceso requiere consultar múltiples documentos y cruzar dicha información con el registro del afiliado.

El objetivo del sistema será realizar este proceso de forma automática utilizando Inteligencia Artificial Generativa apoyada mediante Retrieval-Augmented Generation (RAG).

---

# 3. Objetivo General

Construir un asistente inteligente capaz de:

- Interpretar consultas redactadas en lenguaje natural.
- Identificar correctamente la intención del usuario.
- Consultar información relevante dentro de múltiples documentos.
- Consultar información específica del afiliado.
- Cruzar ambas fuentes de información.
- Aplicar razonamiento sobre reglas de negocio.
- Determinar si la solicitud procede.
- Generar una respuesta clara, formal y completamente fundamentada.
- Citar siempre la fuente utilizada.
- Evitar completamente la invención de información.

La solución debe demostrar criterio de arquitectura de software, mantenibilidad y buenas prácticas de ingeniería.

---

# 4. Objetivos Funcionales

La aplicación deberá ser capaz de:

## 4.1 Interpretar consultas

Comprender preguntas redactadas en lenguaje natural sin depender de frases exactas.

Ejemplo:

"Quisiera saber si la resonancia lumbar ordenada por mi médico está cubierta por mi plan."

Debe identificar automáticamente:

- afiliado
- procedimiento
- condiciones mencionadas
- intención

---

## 4.2 Consultar información documental

La aplicación deberá recuperar únicamente la información relevante contenida dentro de los documentos entregados.

Nunca deberá enviar documentos completos al modelo.

---

## 4.3 Consultar información del afiliado

La aplicación deberá consultar información del afiliado desde el archivo BD_afiliados.xlsx.

Inicialmente el origen será un archivo Excel.

La arquitectura deberá permitir reemplazar posteriormente dicho origen por:

- PostgreSQL
- SQL Server
- API REST
- otro repositorio

sin modificar la lógica del negocio.

---

## 4.4 Razonamiento

El sistema deberá razonar utilizando simultáneamente:

- reglas documentales
- condiciones del plan
- estado del afiliado
- antigüedad
- autorizaciones
- periodos de carencia
- demás información disponible

No basta con recuperar texto.

Debe existir un proceso explícito de razonamiento.

---

## 4.5 Generación de respuesta

La respuesta deberá ser:

Formal.

Precisa.

Fundamentada.

Trazable.

Nunca deberá contener afirmaciones no respaldadas por los documentos recuperados.

---

# 5. Objetivos No Funcionales

El proyecto deberá priorizar:

- mantenibilidad
- escalabilidad
- desacoplamiento
- legibilidad
- facilidad para realizar pruebas
- modularidad
- separación de responsabilidades
- reutilización

La calidad del código tiene prioridad sobre la cantidad de funcionalidades implementadas.

---

# 6. Filosofía del Proyecto

Este proyecto NO busca demostrar únicamente conocimientos sobre LLMs.

Busca demostrar capacidad para diseñar software profesional.

Toda decisión deberá justificarse desde el punto de vista de ingeniería.

Se priorizará:

Arquitectura > Funcionalidades

Código limpio > Código rápido

Mantenibilidad > Complejidad

Desacoplamiento > Dependencias innecesarias

---

# 7. Restricciones

Durante el desarrollo deberán respetarse las siguientes restricciones.

## No hardcodear

Nunca escribir directamente en el código:

- nombres de documentos
- rutas
- modelos
- API Keys
- configuraciones

Todo deberá provenir desde configuración externa.

---

## No acoplar componentes

El dominio nunca deberá conocer:

FastAPI

OpenAI

ChromaDB

Pandas

python-docx

Toda dependencia externa deberá permanecer dentro de Infrastructure.

---

## No mezclar responsabilidades

Controllers:

únicamente reciben peticiones.

Services:

orquestan procesos.

Use Cases:

implementan lógica de aplicación.

Repositories:

obtienen datos.

Providers:

interactúan con servicios externos.

---

# 8. Alcance

La primera versión del proyecto trabajará con los siguientes archivos:

documents/

DOC1_Manual_de_Beneficios.docx

DOC2_Terminos_y_Condiciones.docx

DOC3_Criterios_de_Necesidad_Medica.docx

data/

BD_afiliados.xlsx

Estos archivos serán suficientes para completar la prueba.

Sin embargo, la arquitectura deberá permitir agregar nuevos documentos sin modificar la lógica del sistema.

---

# 9. Fuera del Alcance

No hace parte de esta prueba:

Autenticación.

Autorización.

Persistencia de usuarios.

Panel administrativo.

Frontend complejo.

Escalamiento distribuido.

Microservicios.

Kubernetes.

Procesamiento paralelo.

Entrenamiento de modelos.

Fine Tuning.

Modelos propios.

La solución deberá concentrarse exclusivamente en resolver correctamente el problema planteado.

---

# 10. Criterios de Calidad

Antes de considerar una funcionalidad terminada deberá cumplir:

✓ Código tipado.

✓ Logging.

✓ Manejo de errores.

✓ Documentación.

✓ Responsabilidad única.

✓ Desacoplamiento.

✓ Pruebas.

✓ Configuración externa.

✓ Cumplimiento de SOLID.

✓ Arquitectura consistente.

---

# 11. Regla Principal

Ante cualquier decisión de implementación deberá preguntarse:

"¿Esta decisión facilita que el sistema pueda evolucionar dentro de uno o dos años?"

Si la respuesta es negativa, deberá buscarse una alternativa más desacoplada.

La arquitectura siempre tendrá prioridad sobre la rapidez de implementación.

# 2. Arquitectura del Sistema

---

# 2.1 Principio Arquitectónico

La arquitectura deberá diseñarse bajo una variante simplificada de Clean Architecture orientada al desarrollo de aplicaciones basadas en Inteligencia Artificial Generativa.

El objetivo principal es garantizar:

- Bajo acoplamiento.
- Alta cohesión.
- Facilidad de mantenimiento.
- Facilidad para realizar pruebas.
- Escalabilidad.
- Sustitución sencilla de proveedores externos.
- Evolución del proyecto sin afectar el dominio.

Toda dependencia deberá apuntar hacia el dominio.

Nunca en dirección contraria.

---

# 2.2 Arquitectura General

```

```
                           +----------------------+
                           |      Cliente         |
                           +----------+-----------+
                                      |
                                      |
                           HTTP / REST API
                                      |
                                      |
                         +------------v-------------+
                         |        FastAPI           |
                         |      Controllers         |
                         +------------+-------------+
                                      |
                                      |
                         +------------v-------------+
                         |       Application        |
                         |      Use Cases           |
                         +------------+-------------+
                                      |
               +----------------------+----------------------+
               |                      |                      |
               |                      |                      |
       +-------v------+      +--------v--------+     +-------v-------+
       | Affiliate    |      | Retrieval       |     | Response      |
       | Service      |      | Service         |     | Service       |
       +-------+------+      +--------+--------+     +-------+-------+
               |                      |                      |
               |                      |                      |
       +-------v------+      +--------v--------+     +-------v-------+
       | Repository   |      | Vector Store    |     | LLM Provider  |
       +-------+------+      +--------+--------+     +-------+-------+
               |                      |                      |
               |                      |                      |
         Excel Reader            ChromaDB              OpenAI GPT-4.1
```

---

# 2.3 Principio de Dependencias

Toda dependencia deberá seguir la siguiente dirección.

```
Presentation

↓

Application

↓

Domain

↓

Infrastructure
```

Nunca en sentido contrario.

Ejemplo:

✔ Un Controller puede utilizar un Use Case.

✔ Un Use Case puede utilizar un Repository.

✔ Un Repository puede utilizar Pandas.

✘ Un Controller nunca debe utilizar Pandas.

✘ Un Controller nunca debe utilizar OpenAI.

✘ El Dominio nunca debe conocer ChromaDB.

✘ El Dominio nunca debe importar FastAPI.

---

# 2.4 Capas del Proyecto

## Presentation

Responsabilidad:

Exponer la API REST.

Debe contener únicamente:

- Endpoints
- DTOs
- Validaciones HTTP
- Conversión Request/Response

No contiene lógica de negocio.

---

## Application

Representa los casos de uso.

Aquí vive la orquestación del sistema.

Ejemplo:

ResponderConsultaUseCase

Este caso de uso coordina:

- consultar afiliado
- recuperar contexto
- generar prompt
- llamar al LLM
- construir respuesta

No conoce FastAPI.

No conoce OpenAI.

---

## Domain

Es el corazón del proyecto.

Debe contener:

Entidades.

Interfaces.

Contratos.

Objetos de valor.

Reglas de negocio puras.

No depende de ninguna librería externa.

---

## Infrastructure

Implementaciones concretas.

Ejemplo:

OpenAIProvider

ChromaVectorStore

ExcelAffiliateRepository

WordDocumentLoader

EmbeddingGenerator

Toda integración externa ocurre aquí.

---

# 2.5 Flujo General

Una consulta seguirá exactamente el siguiente flujo.

```
Usuario

↓

FastAPI

↓

Controller

↓

ResponderConsultaUseCase

↓

Buscar Afiliado

↓

Recuperar Contexto

↓

Construir Prompt

↓

LLM

↓

Interpretar Respuesta

↓

Construir DTO

↓

Cliente
```

---

# 2.6 Pipeline RAG

El sistema utilizará Retrieval-Augmented Generation.

El pipeline será:

```
Consulta

↓

Embedding

↓

Búsqueda Vectorial

↓

Top K Chunks

↓

Construcción del Prompt

↓

GPT-4.1

↓

Respuesta
```

Nunca deberá enviarse el documento completo.

Siempre únicamente los fragmentos relevantes.

---

# 2.7 Pipeline de Indexación

Los documentos deberán procesarse únicamente durante la indexación.

Nunca durante cada consulta.

El flujo será:

```
Leer documentos

↓

Extraer texto

↓

Normalizar

↓

Dividir en Chunks

↓

Generar Embeddings

↓

Guardar en ChromaDB
```

Consultas posteriores reutilizarán el índice.

---

# 2.8 Responsabilidades

## Controller

Debe:

✔ recibir request

✔ validar request

✔ invocar Use Case

✔ devolver response

Nunca:

✘ consultar Excel

✘ llamar OpenAI

✘ acceder Chroma

---

## Use Case

Debe:

coordinar todo el proceso.

Nunca implementar detalles técnicos.

---

## Repository

Debe obtener información.

Nunca contener reglas del negocio.

---

## Provider

Debe encapsular servicios externos.

Ejemplo:

OpenAI.

Nunca exponer el SDK al resto del proyecto.

---

## Vector Store

Debe conocer únicamente:

indexación

embeddings

búsqueda vectorial

Nada más.

---

# 2.9 Arquitectura Preparada para Evolución

El sistema deberá permitir reemplazar sin afectar el resto del código:

Excel

↓

PostgreSQL

o

API REST

---

OpenAI

↓

Gemini

↓

Azure OpenAI

---

ChromaDB

↓

Pinecone

↓

Qdrant

↓

Weaviate

---

Word

↓

PDF

↓

HTML

↓

Markdown

---

# 2.10 Regla Fundamental

Toda dependencia externa deberá poder reemplazarse modificando únicamente Infrastructure.

Nunca deberá modificarse:

Domain.

Application.

Presentation.

---

# 2.11 Decisiones Arquitectónicas

Se adopta Clean Architecture porque:

- separa responsabilidades.
- facilita pruebas.
- desacopla proveedores.
- simplifica mantenimiento.
- favorece escalabilidad.

Se adopta Repository Pattern porque desacopla el origen de datos.

Se adopta Strategy Pattern para permitir múltiples proveedores LLM.

Se adopta Dependency Injection para facilitar pruebas y reemplazo de implementaciones.

Se adopta Service Layer para centralizar la orquestación del negocio.

La arquitectura prioriza mantenibilidad sobre velocidad de desarrollo.

---

# 2.12 Principios SOLID

Todo el proyecto deberá cumplir:

- Single Responsibility Principle
- Open Closed Principle
- Liskov Substitution Principle
- Interface Segregation Principle
- Dependency Inversion Principle

Cualquier implementación que viole estos principios deberá considerarse incorrecta.

---

# 2.13 Regla de Oro

Antes de escribir cualquier componente deberá responderse la siguiente pregunta:

"Si mañana cambio OpenAI por Gemini, Chroma por Pinecone y Excel por PostgreSQL...

¿Debo modificar más de Infrastructure?"

Si la respuesta es sí, la arquitectura deberá rediseñarse.

# 3. Patrones de Diseño, Interfaces y Contratos

---

# 3.1 Filosofía de Diseño

Toda la arquitectura deberá construirse siguiendo el principio:

> "Programar contra abstracciones y no contra implementaciones."

Ningún componente de la aplicación deberá depender directamente de una implementación concreta.

Todos los componentes deberán depender de interfaces.

La implementación concreta será responsabilidad exclusiva de la capa Infrastructure.

---

# 3.2 Patrones de Diseño Utilizados

El proyecto utilizará únicamente patrones que aporten valor al problema.

No deberán agregarse patrones innecesarios.

Los patrones seleccionados son:

- Repository Pattern
- Strategy Pattern
- Factory Pattern
- Dependency Injection
- Service Layer
- Adapter Pattern
- Builder Pattern (para prompts)

Cada uno deberá utilizarse únicamente donde corresponda.

---

# 3.3 Repository Pattern

## Objetivo

Desacoplar completamente el origen de los datos.

El resto del sistema nunca deberá saber si los datos provienen de:

- Excel
- PostgreSQL
- SQL Server
- API REST
- MongoDB

Toda esa responsabilidad pertenece al Repository.

---

## Interface

AffiliateRepository

Responsabilidades:

- Buscar afiliado por identificación.
- Obtener información del plan.
- Obtener cobertura.
- Obtener datos necesarios para el razonamiento.

Nunca deberá conocer:

- OpenAI
- FastAPI
- ChromaDB

---

## Implementación inicial

ExcelAffiliateRepository

Internamente utilizará:

Pandas

openpyxl

Pero esta decisión deberá permanecer completamente encapsulada.

---

# 3.4 Document Loader

El sistema deberá abstraer completamente el origen de los documentos.

No deberá asumir que siempre serán archivos Word.

---

Interface

DocumentLoader

Responsabilidades

- Leer documentos.
- Extraer texto.
- Extraer metadatos.
- Entregar un modelo uniforme.

---

Implementación inicial

WordDocumentLoader

Utilizará:

python-docx

---

Implementaciones futuras

PdfDocumentLoader

MarkdownDocumentLoader

HtmlDocumentLoader

---

# 3.5 Chunking Strategy

La estrategia de fragmentación deberá abstraerse.

Nunca escribir directamente lógica de chunking dentro del pipeline.

---

Interface

ChunkStrategy

Responsabilidades

- recibir texto
- generar chunks
- preservar contexto

---

Implementación inicial

RecursiveCharacterChunkStrategy

---

Implementaciones futuras

SemanticChunkStrategy

SentenceChunkStrategy

MarkdownChunkStrategy

---

# 3.6 Embedding Provider

La generación de embeddings deberá abstraerse.

---

Interface

EmbeddingProvider

Responsabilidades

- generar embeddings
- procesar listas
- ocultar SDK utilizado

---

Implementación inicial

OpenAIEmbeddingProvider

Modelo:

text-embedding-3-small

---

Implementaciones futuras

VoyageAI

Cohere

Azure OpenAI

Sentence Transformers

---

# 3.7 Vector Store

Toda búsqueda vectorial deberá encapsularse.

---

Interface

VectorStore

Responsabilidades

- indexar
- buscar
- actualizar
- eliminar

---

Implementación inicial

ChromaVectorStore

---

Implementaciones futuras

Pinecone

Qdrant

Weaviate

FAISS

Milvus

---

# 3.8 LLM Provider

El modelo de lenguaje nunca deberá conocerse fuera de Infrastructure.

---

Interface

LLMProvider

Responsabilidades

- recibir prompt
- generar respuesta
- devolver texto

---

Implementación inicial

OpenAIProvider

Modelo por defecto

GPT-4.1

Configurable mediante

OPENAI_MODEL

---

Implementaciones futuras

Gemini

Azure OpenAI

Llama

Mistral

---

# 3.9 Prompt Builder

Los prompts no deberán construirse concatenando strings.

Se implementará un Builder.

---

Interface

PromptBuilder

Responsabilidades

- construir prompt
- agregar contexto
- agregar instrucciones
- agregar información del afiliado
- agregar historial (si existe)

---

Implementación inicial

CoveragePromptBuilder

---

Beneficios

Mayor mantenibilidad.

Prompts reutilizables.

Más fáciles de probar.

---

# 3.10 Retrieval Service

Responsabilidad

Recuperar contexto documental.

No genera respuestas.

No llama al LLM.

Únicamente recupera información.

---

Interface

RetrievalService

Funciones

retrieve()

search()

similarity_search()

---

# 3.11 Response Generator

Responsabilidad

Convertir el resultado del modelo en una respuesta de negocio.

No deberá devolver texto plano.

Deberá devolver un DTO estructurado.

---

Ejemplo

CoverageResponse

estado

justificación

fragmentos utilizados

nivel de confianza

advertencias

---

# 3.12 Orquestador Principal

El corazón del sistema será:

CoverageAnalysisService

Será el único componente autorizado para coordinar todo el proceso.

Responsabilidades

- consultar afiliado
- recuperar contexto
- construir prompt
- llamar LLM
- interpretar respuesta
- construir DTO

Nunca deberá contener código HTTP.

Nunca deberá contener SQL.

Nunca deberá contener lógica de lectura de archivos.

---

# 3.13 Flujo Interno

CoverageAnalysisService

↓

AffiliateRepository

↓

RetrievalService

↓

PromptBuilder

↓

LLMProvider

↓

CoverageResponse

---

# 3.14 Dependency Injection

Toda dependencia deberá inyectarse.

Nunca crear instancias mediante:

new

o

Class()

dentro de los servicios.

Ejemplo incorrecto

CoverageService

↓

OpenAIProvider()

Ejemplo correcto

CoverageService

↓

LLMProvider

---

# 3.15 Factory Pattern

La creación de proveedores deberá centralizarse.

Ejemplo

LLMFactory

EmbeddingFactory

VectorStoreFactory

DocumentLoaderFactory

ChunkStrategyFactory

Esto facilitará cambiar implementaciones mediante configuración.

---

# 3.16 Adapter Pattern

Toda librería externa deberá permanecer detrás de un Adapter.

Ejemplo

OpenAI SDK

↓

OpenAIProvider

↓

LLMProvider

De esta manera el resto del sistema nunca dependerá del SDK.

---

# 3.17 Builder Pattern

El Prompt Builder utilizará Builder Pattern.

No deberá existir código como:

prompt = texto + texto + texto

Toda construcción deberá ser incremental.

Ejemplo

builder

.add_system_rules()

.add_affiliate()

.add_documents()

.add_question()

.build()

---

# 3.18 Principios de Acoplamiento

Permitido

Controller

↓

UseCase

↓

Service

↓

Repository

No permitido

Controller

↓

OpenAI

Controller

↓

Excel

Controller

↓

Chroma

Domain

↓

Pandas

Application

↓

python-docx

---

# 3.19 Regla Fundamental

Si para reemplazar OpenAI por Gemini es necesario modificar más de un archivo fuera de Infrastructure, la arquitectura se considera incorrecta.

Lo mismo aplica para:

Excel

ChromaDB

Word

Embeddings

Cualquier dependencia externa.


# 4. Organización del Proyecto

---

# 4.1 Objetivo

La estructura del proyecto deberá facilitar:

- Escalabilidad.
- Mantenibilidad.
- Separación de responsabilidades.
- Facilidad para realizar pruebas.
- Reemplazo de implementaciones.
- Evolución hacia sistemas agénticos.

La organización del proyecto forma parte de la arquitectura y no deberá modificarse sin una justificación técnica.

---

# 4.2 Estructura General

```

project/

│

├── app/

│ ├── presentation/

│ ├── application/

│ ├── domain/

│ ├── infrastructure/

│ ├── shared/

│ └── config/

│

├── documents/

│

├── data/

│

├── storage/

│

├── tests/

│

├── scripts/

│

├── logs/

│

├── docker/

│

├── README.md

├── ESPECIFICACION.md

├── requirements.txt

├── pyproject.toml

├── .env.example

└── .gitignore

```

---

# 4.3 Responsabilidad de cada carpeta

## app/

Contiene todo el código fuente.

No deberá existir lógica del negocio fuera de esta carpeta.

---

## documents/

Contendrá los documentos entregados para la prueba.

Inicialmente:

DOC1_Manual_de_Beneficios.docx

DOC2_Terminos_y_Condiciones.docx

DOC3_Criterios_de_Necesidad_Medica.docx

No deberán codificarse estos nombres.

El sistema deberá leer automáticamente todos los documentos compatibles.

---

## data/

Contendrá fuentes estructuradas.

Inicialmente:

BD_afiliados.xlsx

En el futuro podrá contener:

CSV

JSON

SQLite

---

## storage/

Persistencia del índice vectorial.

Ejemplo

storage/

chroma/

cache/

embeddings/

Nunca almacenar documentos originales aquí.

---

## tests/

Todas las pruebas.

Nunca mezclar pruebas con código productivo.

---

## logs/

Archivos de log.

Nunca versionarlos.

---

## scripts/

Scripts auxiliares.

Ejemplo:

reindex.py

load_documents.py

clean_storage.py

---

## docker/

Dockerfile

docker-compose.yml

---

# 4.4 Organización interna de app

```

app/

│

├── presentation/

├── application/

├── domain/

├── infrastructure/

├── shared/

└── config/

```

---

# 4.5 Presentation

```

presentation/

│

├── api/

├── controllers/

├── schemas/

├── routers/

└── middleware/

```

Responsabilidades

Controllers

Recibir requests.

Routers

Registrar endpoints.

Schemas

DTOs de entrada y salida.

Middleware

Aspectos transversales.

Nunca lógica del negocio.

---

# 4.6 Application

```

application/

│

├── use_cases/

├── services/

├── reasoning/

├── prompts/

├── dto/

└── interfaces/

```

---

## use_cases/

Representan los casos de uso.

Ejemplo

AnalyzeCoverageUseCase

---

## services/

Orquestadores.

No contienen detalles técnicos.

---

## reasoning/

Motor de razonamiento.

Aquí vive la inteligencia del flujo.

Ejemplo

CoverageDecisionEngine

EvidenceEvaluator

RuleEngine

AgentCoordinator

Este último inicialmente será simple pero preparado para evolucionar hacia un sistema agéntico.

---

## prompts/

Builders de prompts.

Nunca concatenar strings manualmente.

---

## dto/

Objetos de transferencia.

---

## interfaces/

Interfaces utilizadas por Application.

---

# 4.7 Domain

```

domain/

│

├── entities/

├── value_objects/

├── repositories/

├── providers/

├── exceptions/

└── models/

```

---

## entities/

Afiliado.

Cobertura.

Procedimiento.

Respuesta.

---

## repositories/

Interfaces.

Nunca implementaciones.

---

## providers/

Interfaces para IA.

LLMProvider

EmbeddingProvider

VectorStore

---

## exceptions/

Errores del dominio.

---

# 4.8 Infrastructure

```

infrastructure/

│

├── llm/

├── vectorstore/

├── repositories/

├── document_loader/

├── embeddings/

├── chunking/

├── parser/

├── persistence/

└── logging/

```

---

## llm/

OpenAIProvider

---

## vectorstore/

Chroma.

---

## repositories/

ExcelAffiliateRepository

---

## document_loader/

WordDocumentLoader

---

## embeddings/

OpenAIEmbeddingProvider

---

## chunking/

RecursiveChunkStrategy

---

## parser/

Normalización.

Limpieza.

---

## persistence/

Persistencia.

---

## logging/

Configuración del logger.

---

# 4.9 Shared

```

shared/

│

├── constants/

├── utils/

├── types/

└── validators/

```

Solo componentes reutilizables.

Nunca lógica del negocio.

---

# 4.10 Config

```

config/

│

├── settings.py

├── logging.py

└── dependencies.py

```

---

settings.py

Carga .env.

---

logging.py

Configuración global.

---

dependencies.py

Dependency Injection.

---

# 4.11 Organización de Tests

```

tests/

│

├── unit/

├── integration/

├── e2e/

├── fixtures/

└── mocks/

```

---

Unit

Pruebas unitarias.

---

Integration

Pruebas entre componentes.

---

E2E

Flujo completo.

---

Fixtures

Datos de prueba.

---

Mocks

Repositorios simulados.

---

# 4.12 Convenciones de Nombres

Clases

PascalCase

CoverageAnalysisService

Funciones

snake_case

generate_prompt()

Archivos

snake_case

coverage_service.py

Interfaces

Sufijo

Repository

Provider

Strategy

Factory

Builder

UseCase

DTO

Engine

---

# 4.13 Archivos Prohibidos

Nunca crear carpetas como

helpers/

misc/

others/

temp/

utils_generales/

codigo_final/

services2/

test_final/

Cualquier carpeta deberá tener una responsabilidad claramente definida.

---

# 4.14 Regla de Organización

Si un desarrollador nuevo abre el proyecto deberá poder identificar dónde crear un nuevo componente en menos de un minuto.

Si existen dudas sobre dónde ubicar un archivo, significa que la estructura debe rediseñarse.

---

# 4.15 Principio Final

La estructura del proyecto deberá permitir crecer durante varios años sin necesidad de reorganizar carpetas ni romper dependencias.

Toda nueva funcionalidad deberá encontrar un lugar natural dentro de la arquitectura existente.

# 5. Stack Tecnológico y Decisiones Técnicas

---

# 5.1 Filosofía Tecnológica

La selección de tecnologías no deberá responder únicamente a popularidad.

Cada herramienta deberá cumplir al menos uno de los siguientes objetivos:

- Reducir complejidad.
- Mejorar mantenibilidad.
- Facilitar pruebas.
- Desacoplar componentes.
- Simplificar evolución futura.
- Mejorar legibilidad.
- Disminuir tiempo de implementación.
- Mantener una arquitectura limpia.

Toda nueva dependencia deberá justificar su existencia.

---

# 5.2 Lenguaje de Programación

## Python 3.11+

### Uso

Lenguaje principal del proyecto.

### Justificación

Python es actualmente el estándar de facto para el desarrollo de aplicaciones basadas en Inteligencia Artificial.

Su ecosistema ofrece librerías maduras para:

- LLMs
- NLP
- Embeddings
- Vector Databases
- APIs
- Procesamiento documental

Además permite construir rápidamente aplicaciones altamente mantenibles.

### Beneficios

- Excelente tipado.
- Gran ecosistema.
- Comunidad enorme.
- Compatibilidad con IA.
- Desarrollo rápido.

### Alternativas

- Java
- C#
- NodeJS
- Go

### Capa autorizada

Todo el proyecto.

---

# 5.3 Framework Web

## FastAPI

### Uso

Exponer la API REST.

### Justificación

FastAPI ofrece:

- Alto rendimiento.
- Validación automática.
- OpenAPI.
- Tipado completo.
- Dependency Injection.
- Excelente integración con Pydantic.

Es especialmente adecuado para servicios de IA.

### Beneficios

- Muy rápido.
- Código limpio.
- Documentación automática.
- Fácil testing.

### Alternativas

Flask

Django

Litestar

### Restricción

FastAPI únicamente podrá utilizarse en:

presentation/

Nunca dentro de:

Domain

Application

Infrastructure

---

# 5.4 Validación de Datos

## Pydantic v2

### Uso

Validación.

DTOs.

Configuración.

### Justificación

Permite:

- Tipado fuerte.
- Validaciones declarativas.
- Serialización.
- Configuración mediante BaseSettings.

### Restricción

No utilizar diccionarios sin tipado para transportar información.

Toda comunicación entre capas deberá realizarse mediante DTOs.

---

# 5.5 Configuración

## pydantic-settings

### Uso

Carga del archivo .env

### Justificación

Centraliza toda la configuración.

Evita acceder directamente a variables de entorno desde cualquier parte del proyecto.

### Variables esperadas

OPENAI_API_KEY

OPENAI_MODEL

EMBEDDING_MODEL

DOCUMENTS_PATH

AFFILIATES_FILE

VECTOR_DB_PATH

LOG_LEVEL

TOP_K_RESULTS

CHUNK_SIZE

CHUNK_OVERLAP

---

# 5.6 Modelo de Lenguaje

## OpenAI GPT-4.1

### Uso

Generación de respuestas.

Razonamiento.

Interpretación.

### Justificación

GPT-4.1 ofrece:

- Excelente razonamiento.
- Buen seguimiento de instrucciones.
- Contexto amplio.
- Alta estabilidad.

### Restricción

Nunca escribir:

gpt-4.1

directamente en el código.

Siempre utilizar:

OPENAI_MODEL

### Alternativas futuras

GPT-4.1-mini

Gemini

Azure OpenAI

Llama

Mistral

---

# 5.7 Embeddings

## text-embedding-3-small

### Uso

Generación de embeddings.

### Justificación

Excelente relación:

Costo

Precisión

Velocidad

Es suficiente para una prueba técnica.

### Restricción

Siempre configurable.

Nunca hardcodeado.

---

# 5.8 Base Vectorial

## ChromaDB

### Uso

Persistencia de embeddings.

Búsqueda semántica.

### Justificación

Para esta prueba ofrece:

- Instalación sencilla.
- Persistencia local.
- Sin dependencias externas.
- Excelente integración.

No requiere infraestructura adicional.

### Alternativas

Pinecone

Qdrant

Weaviate

FAISS

Milvus

### Restricción

El SDK únicamente podrá utilizarse en:

infrastructure/vectorstore

---

# 5.9 Lectura de Word

## python-docx

### Uso

Extracción de texto.

### Justificación

Los documentos entregados son:

.docx

No existe necesidad de OCR.

### Restricción

Nunca acceder directamente desde Application.

---

# 5.10 Lectura del Excel

## Pandas

## OpenPyXL

### Uso

Lectura de:

BD_afiliados.xlsx

### Justificación

Facilidad de consulta.

Código simple.

Excelente soporte.

### Restricción

Solo:

ExcelAffiliateRepository

puede utilizar Pandas.

---

# 5.11 Gestión del Proyecto

## uv

### Uso

Gestión de dependencias.

Entorno virtual.

### Justificación

Más rápido que pip.

Mayor reproducibilidad.

---

# 5.12 Calidad del Código

## Ruff

### Uso

Linting.

### Justificación

Muy rápido.

Reemplaza múltiples herramientas.

---

## Black

### Uso

Formateo.

### Justificación

Consistencia.

---

## MyPy

### Uso

Validación de tipos.

### Justificación

Detecta errores antes de ejecución.

---

# 5.13 Testing

## Pytest

### Uso

Pruebas unitarias.

Integración.

E2E.

### Justificación

Estándar en Python.

Excelente soporte para fixtures y mocks.

---

# 5.14 Logging

## logging

### Uso

Registro de eventos.

### Justificación

No introducir dependencias innecesarias.

La librería estándar es suficiente.

### Nivel esperado

INFO

WARNING

ERROR

DEBUG

Nunca utilizar print() para depuración.

---

# 5.15 Variables de Entorno

Toda configuración deberá obtenerse desde:

.env

Nunca desde constantes.

Ejemplo

OPENAI_API_KEY

OPENAI_MODEL

DOCUMENTS_PATH

AFFILIATES_FILE

VECTOR_DB_PATH

TOP_K_RESULTS

CHUNK_SIZE

CHUNK_OVERLAP

LOG_LEVEL

---

# 5.16 Dependencias Permitidas

Cada dependencia deberá limitarse a una capa.

| Tecnología | Capa autorizada |
|------------|-----------------|
| FastAPI | Presentation |
| Pydantic | Presentation / Application |
| OpenAI SDK | Infrastructure |
| ChromaDB | Infrastructure |
| Pandas | Infrastructure |
| python-docx | Infrastructure |
| logging | Shared |
| pytest | Tests |
| Ruff | Desarrollo |
| Black | Desarrollo |
| MyPy | Desarrollo |

---

# 5.17 Dependencias Prohibidas

Nunca importar:

OpenAI

Pandas

python-docx

ChromaDB

Dentro de:

Domain

Application

Presentation (excepto FastAPI)

---

# 5.18 Seguridad

Nunca incluir:

API Keys.

Contraseñas.

Secrets.

Archivos .env.

Credenciales.

El repositorio únicamente deberá contener:

.env.example

---

# 5.19 Criterios para Incorporar Nuevas Librerías

Antes de agregar una nueva dependencia deberá responderse:

¿Existe una solución utilizando la librería estándar?

¿Aporta valor real?

¿Reduce complejidad?

¿Es mantenida activamente?

¿Tiene buena documentación?

¿Puede reemplazarse fácilmente?

Si la respuesta es negativa, la dependencia no deberá incorporarse.

---

# 5.20 Principio Final

La tecnología es un medio y no un fin.

La arquitectura del sistema no deberá depender de una herramienta específica.

Si una tecnología cambia, únicamente deberá modificarse Infrastructure.

El resto del proyecto deberá permanecer inalterado.

# 6. Pipeline de Ingesta e Indexación (RAG)

---

# 6.1 Objetivo

El sistema utilizará una arquitectura Retrieval-Augmented Generation (RAG).

El objetivo de este pipeline será transformar documentos estructurados y no estructurados en una base de conocimiento semántica optimizada para consultas mediante LLM.

La indexación deberá ejecutarse una única vez.

Las consultas posteriores nunca deberán reprocesar los documentos.

---

# 6.2 Principios

El pipeline deberá cumplir los siguientes principios:

- Repetible
- Determinístico
- Idempotente
- Escalable
- Modular
- Extensible

Cada etapa deberá tener una única responsabilidad.

---

# 6.3 Flujo General

```

```
Documentos

↓

Document Loader

↓

Normalizador

↓

Validador

↓

Chunker

↓

Metadata Builder

↓

Embedding Generator

↓

Vector Store

↓

Persistencia
```

---

# 6.4 Descubrimiento Automático de Documentos

El sistema nunca deberá depender de nombres específicos.

No deberá existir código como:

DOC1.docx

DOC2.docx

DOC3.docx

La aplicación deberá descubrir automáticamente todos los documentos compatibles encontrados dentro del directorio configurado.

Ejemplo

documents/

Manual.docx

Beneficios.docx

Condiciones.docx

Politicas.docx

Procedimientos.docx

El sistema deberá procesarlos automáticamente.

---

# 6.5 Document Loader

Responsabilidad

Leer archivos físicos.

Nunca interpretar contenido.

Nunca generar embeddings.

Nunca realizar chunking.

Únicamente:

- abrir documento
- extraer texto
- obtener metadatos básicos

---

Metadatos mínimos

nombre

ruta

fecha modificación

tipo documento

tamaño

---

# 6.6 Normalización

Todo documento deberá pasar por una etapa de limpieza.

Objetivos

Eliminar:

espacios múltiples

saltos innecesarios

tabulaciones

caracteres invisibles

espacios duplicados

codificaciones inconsistentes

Nunca modificar el significado del texto.

---

# 6.7 Validación

Antes del chunking deberá verificarse:

✔ Documento vacío

✔ Documento corrupto

✔ Texto demasiado pequeño

✔ Texto ilegible

Los documentos inválidos deberán registrarse en logs.

Nunca deberán detener toda la indexación.

---

# 6.8 Estrategia de Chunking

El proyecto utilizará inicialmente:

Recursive Character Chunking

Justificación

Mantiene contexto.

Divide inteligentemente.

Excelente rendimiento.

Muy utilizado en aplicaciones RAG.

---

Parámetros iniciales

Chunk Size

1000 caracteres

Chunk Overlap

200 caracteres

Estos valores deberán configurarse mediante:

CHUNK_SIZE

CHUNK_OVERLAP

Nunca hardcodearse.

---

# 6.9 Reglas de Chunking

Nunca dividir:

una palabra

una oración importante

un título de su contenido

Siempre intentar mantener coherencia semántica.

---

# 6.10 Metadata Builder

Cada chunk deberá almacenar información suficiente para garantizar trazabilidad.

Metadatos mínimos

document_id

document_name

chunk_id

chunk_index

total_chunks

page (si aplica)

source

created_at

hash

---

Ejemplo

```

{
"id":"chunk_00125",
"document":"DOC2_Terminos.docx",
"chunk":15,
"total":83,
"source":"documents/DOC2.docx"
}

```

---

# 6.11 Hash del Documento

Cada documento deberá generar un hash.

Objetivo

Detectar cambios.

Si el hash no cambia:

No volver a indexar.

Esto reducirá considerablemente tiempos futuros.

---

# 6.12 Embeddings

Cada chunk generará exactamente un embedding.

Nunca generar embeddings del documento completo.

Nunca generar embeddings de múltiples documentos simultáneamente.

---

Proveedor

OpenAI

Modelo

text-embedding-3-small

Configurable mediante

EMBEDDING_MODEL

---

# 6.13 Persistencia

Los embeddings deberán almacenarse en:

ChromaDB

Persistencia local.

Nunca únicamente en memoria.

---

Directorio

storage/chroma

Configurable mediante

VECTOR_DB_PATH

---

# 6.14 Estrategia de Reindexación

El sistema deberá soportar tres modos.

FULL

Reconstruye todo.

---

INCREMENTAL

Solo documentos modificados.

---

NEW ONLY

Solo documentos nuevos.

---

Esto facilitará crecimiento futuro.

---

# 6.15 Cache

Si un documento:

no cambió

ya fue indexado

su hash coincide

Entonces deberá reutilizarse.

Nunca recalcular embeddings innecesariamente.

---

# 6.16 Errores

Si un documento falla.

No detener el pipeline.

Registrar error.

Continuar con el siguiente.

Al finalizar generar un resumen.

---

# 6.17 Logging

Durante la indexación deberá registrarse:

Documento leído.

Chunks creados.

Embeddings generados.

Tiempo por documento.

Errores.

Tiempo total.

Cantidad de documentos.

Cantidad de chunks.

---

# 6.18 Estadísticas

Al finalizar la indexación deberá mostrarse un resumen.

Ejemplo

```

Documentos procesados: 4

Documentos omitidos: 1

Chunks generados: 348

Embeddings creados: 348

Tiempo total: 18.4 s

```

---

# 6.19 Flujo Completo

```

Inicio

↓

Buscar documentos

↓

Leer documento

↓

Normalizar

↓

Validar

↓

Calcular hash

↓

¿Existe?

↓

No

↓

Chunking

↓

Metadata

↓

Embedding

↓

Persistir

↓

Siguiente documento

↓

Fin

```

---

# 6.20 Reglas de Ingeniería

Nunca:

Generar embeddings desde Controllers.

Leer documentos desde FastAPI.

Acceder directamente a Chroma.

Generar chunks dentro del LLM.

Mezclar múltiples responsabilidades.

---

# 6.21 Preparado para Evolución

La arquitectura deberá permitir incorporar en el futuro:

PDF

HTML

Markdown

TXT

XML

JSON

sin modificar el pipeline principal.

Únicamente agregando nuevos DocumentLoader.

---

# 6.22 Principio Final

La indexación representa la construcción del conocimiento del sistema.

Toda consulta futura dependerá de la calidad de este proceso.

Por esta razón deberá privilegiarse:

calidad

trazabilidad

mantenibilidad

antes que velocidad de implementación.

# 7. Pipeline de Consulta y Motor de Razonamiento

---

# 7.1 Objetivo

El objetivo de este pipeline es transformar una consulta en lenguaje natural en una respuesta fundamentada utilizando información documental y datos del afiliado.

El sistema no deberá responder únicamente recuperando texto.

Antes de generar una respuesta deberá ejecutar un proceso explícito de análisis y razonamiento.

El LLM será utilizado como motor de inferencia y redacción, no como fuente de conocimiento.

Toda afirmación deberá estar respaldada por evidencia recuperada.

---

# 7.2 Filosofía

El flujo del sistema se divide en dos grandes etapas.

1.

Obtención de evidencia.

2.

Razonamiento sobre la evidencia.

Nunca deberán mezclarse ambas responsabilidades.

---

# 7.3 Flujo General

```

Cliente

↓

FastAPI

↓

Controller

↓

AnalyzeCoverageUseCase

↓

Reasoning Engine

↓

Response Builder

↓

Cliente

```

---

# 7.4 Flujo Interno del Reasoning Engine

```

Consulta

↓

Intent Analyzer

↓

Affiliate Resolver

↓

Knowledge Retriever

↓

Evidence Evaluator

↓

Coverage Decision Engine

↓

Prompt Builder

↓

LLM

↓

Response Validator

↓

CoverageResponse

```

---

# 7.5 Intent Analyzer

Responsabilidad

Comprender la intención del usuario.

Debe identificar automáticamente:

- procedimiento solicitado
- afiliado
- tipo de consulta
- información faltante
- entidades relevantes

Ejemplo

Pregunta

"¿La resonancia lumbar de Juan Pérez está cubierta?"

Debe detectar:

procedimiento

resonancia lumbar

afiliado

Juan Pérez

tipo

consulta de cobertura

Nunca deberá consultar documentos.

---

# 7.6 Affiliate Resolver

Responsabilidad

Obtener toda la información del afiliado.

Debe consultar:

AffiliateRepository

Información esperada

- plan
- vigencia
- estado
- restricciones
- demás atributos disponibles

No interpreta reglas.

Solo obtiene datos.

---

# 7.7 Knowledge Retriever

Responsabilidad

Buscar evidencia documental.

Nunca responde preguntas.

Nunca genera texto.

Únicamente recupera información relevante.

Entradas

consulta

Salida

lista de chunks relevantes

---

# 7.8 Evidence Evaluator

Responsabilidad

Analizar la evidencia recuperada.

Debe determinar:

¿La evidencia es suficiente?

¿Existe contradicción?

¿Existen múltiples reglas?

¿Hay información ambigua?

Si la evidencia no es suficiente deberá indicarlo.

Nunca inventar información.

---

# 7.9 Coverage Decision Engine

Este componente representa el corazón del sistema.

Responsabilidad

Cruzar:

datos del afiliado

+

reglas documentales

+

consulta

Debe construir una decisión preliminar.

Ejemplo

Procede

No procede

Procede con restricciones

Información insuficiente

Todavía no utiliza el LLM.

---

# 7.10 Prompt Builder

Solo después del razonamiento se construirá el prompt.

Nunca antes.

El Prompt Builder deberá incluir:

Contexto documental.

Datos del afiliado.

Resultado preliminar.

Instrucciones.

Reglas del sistema.

Formato esperado.

---

# 7.11 LLM

El modelo recibe:

Pregunta

+

Contexto

+

Datos del afiliado

+

Resultado del análisis

+

Instrucciones

Nunca recibe documentos completos.

Nunca recibe información innecesaria.

---

# 7.12 Response Validator

Después de obtener la respuesta del LLM deberá ejecutarse una validación.

Debe comprobar:

La respuesta está vacía.

Existen citas.

La respuesta contradice la evidencia.

Se detectan alucinaciones evidentes.

El formato es correcto.

Si alguna validación falla deberá generarse un error controlado.

---

# 7.13 CoverageResponse

El sistema nunca devolverá texto plano.

Siempre devolverá un objeto estructurado.

Ejemplo

```

{

"status":"APPROVED",

"summary":"La solicitud procede.",

"reasoning":"El procedimiento está cubierto para este plan.",

"evidence":[

...

],

"confidence":0.94,

"warnings":[]

}

```

---

# 7.14 Principio de Evidencia

Toda respuesta deberá poder responder la siguiente pregunta:

"¿Qué fragmento documental respalda esta afirmación?"

Si no existe respuesta, dicha afirmación no deberá generarse.

---

# 7.15 Manejo de Incertidumbre

El sistema deberá reconocer cuando no posee suficiente información.

Ejemplos

"No fue posible encontrar evidencia suficiente."

"La documentación disponible no permite determinar la cobertura."

"Ningún documento respalda esta afirmación."

Nunca inventar una respuesta.

---

# 7.16 Flujo Completo

```

Consulta

↓

Analizar intención

↓

Buscar afiliado

↓

Buscar evidencia

↓

Evaluar evidencia

↓

Construir decisión preliminar

↓

Construir prompt

↓

LLM

↓

Validar respuesta

↓

Construir DTO

↓

Cliente

```

---

# 7.17 Preparación para Sistemas Agénticos

Aunque la implementación inicial utilizará un único flujo de razonamiento, la arquitectura deberá permitir incorporar posteriormente un coordinador de agentes.

El componente Reasoning Engine actuará como punto central de orquestación.

En versiones futuras podrá delegar tareas a múltiples agentes especializados.

Ejemplo

Agent

Afiliado

↓

Agent

Coberturas

↓

Agent

Reglas

↓

Agent

Validación

↓

Coordinador

↓

Respuesta

Sin modificar la API ni los casos de uso.

---

# 7.18 Trazabilidad

Cada respuesta deberá conservar información suficiente para reconstruir el proceso de decisión.

Como mínimo deberá registrarse:

- consulta original
- afiliado consultado
- chunks recuperados
- documentos utilizados
- modelo utilizado
- tiempo de respuesta
- nivel de confianza

---

# 7.19 Reglas de Ingeniería

Nunca permitir que el LLM decida sin evidencia.

Nunca construir prompts directamente en los Controllers.

Nunca acceder al Vector Store desde Presentation.

Nunca permitir que el LLM consulte directamente el Excel.

Nunca mezclar recuperación de evidencia con generación de respuestas.

---

# 7.20 Principio Final

El sistema no responde porque "el modelo lo sabe".

Responde porque encontró evidencia, la analizó, la relacionó con los datos del afiliado y finalmente generó una respuesta fundamentada.

El LLM es un componente de razonamiento y generación.

La fuente de verdad siempre serán los documentos y los datos estructurados del afiliado.

# 8. Arquitectura de Prompt Engineering

---

# 8.1 Objetivo

El sistema utilizará una arquitectura de prompts modular.

Los prompts no deberán considerarse cadenas de texto estáticas.

Cada prompt representará un componente del sistema con una responsabilidad específica.

El objetivo es garantizar:

- Consistencia.
- Reutilización.
- Mantenibilidad.
- Trazabilidad.
- Facilidad para realizar pruebas.

---

# 8.2 Principios

Los prompts deberán cumplir los siguientes principios:

- Una única responsabilidad.
- No duplicar instrucciones.
- Ser reutilizables.
- Ser componibles.
- Ser fácilmente modificables.
- Ser independientes del modelo utilizado.

---

# 8.3 Arquitectura General

El PromptBuilder construirá el prompt final a partir de varios componentes.

```

System Prompt

↓

Reasoning Prompt

↓

Evidence Prompt

↓

Context Prompt

↓

Response Prompt

↓

Guardrails

↓

Prompt Final

```

Ningún componente conocerá el contenido interno de otro.

---

# 8.4 System Prompt

Responsabilidad

Definir la identidad permanente del asistente.

Debe incluir:

- Rol del asistente.
- Objetivo.
- Alcance.
- Restricciones.
- Comportamiento esperado.

Ejemplo de responsabilidades

- Actuar como asistente de validación de cobertura.
- Priorizar precisión sobre creatividad.
- Utilizar únicamente evidencia disponible.
- No realizar suposiciones.

Nunca deberá contener información del afiliado ni de la consulta.

---

# 8.5 Reasoning Prompt

Responsabilidad

Indicar al modelo cómo debe razonar.

Debe especificar que:

- Analice la consulta.
- Relacione los datos del afiliado.
- Evalúe las reglas documentales.
- Identifique conflictos.
- Construya una conclusión lógica.

No deberá proporcionar evidencia.

Solo instrucciones de razonamiento.

---

# 8.6 Evidence Prompt

Responsabilidad

Explicar cómo utilizar la evidencia recuperada.

Debe indicar que:

- Solo puede utilizar los fragmentos suministrados.
- No debe inventar información.
- Debe citar la evidencia utilizada.
- Debe indicar cuando la evidencia sea insuficiente.

Este componente constituye el principal mecanismo para reducir alucinaciones.

---

# 8.7 Context Prompt

Responsabilidad

Insertar dinámicamente la información recuperada.

Debe incluir:

- Datos relevantes del afiliado.
- Fragmentos documentales.
- Consulta del usuario.

Nunca deberá incluir documentos completos.

Solo el contexto estrictamente necesario.

---

# 8.8 Response Prompt

Responsabilidad

Definir el formato esperado de la respuesta.

Debe indicar:

- Cómo estructurar la respuesta.
- Nivel de detalle.
- Lenguaje esperado.
- Uso de listas cuando sea necesario.
- Inclusión de referencias a la evidencia.

No deberá contener reglas de negocio.

---

# 8.9 Guardrails

Responsabilidad

Definir las restricciones obligatorias del modelo.

Como mínimo deberá incluir:

- No inventar información.
- No asumir cobertura si no existe evidencia.
- No responder utilizando conocimiento externo.
- Indicar cuando la evidencia sea insuficiente.
- No modificar datos del afiliado.

Los guardrails deberán aplicarse en todas las consultas.

---

# 8.10 PromptBuilder

El PromptBuilder será responsable de ensamblar todos los componentes.

Ejemplo conceptual

```

PromptBuilder

.add_system_prompt()

.add_reasoning()

.add_evidence()

.add_context()

.add_response_format()

.add_guardrails()

.build()

```

Nunca concatenar cadenas manualmente desde los servicios.

---

# 8.11 Variables Dinámicas

Los prompts deberán admitir variables.

Ejemplos

- Nombre del afiliado.
- Tipo de plan.
- Procedimiento solicitado.
- Fecha de consulta.
- Fragmentos recuperados.
- Nivel de confianza.

La sustitución de variables deberá realizarse únicamente durante la construcción del prompt.

---

# 8.12 Estrategia de Contexto

Solo deberá enviarse al modelo el contexto estrictamente necesario.

Nunca enviar:

- Documentos completos.
- Información duplicada.
- Fragmentos irrelevantes.
- Datos no relacionados con la consulta.

El objetivo es maximizar la relación señal/ruido.

---

# 8.13 Gestión del Tamaño del Contexto

Si la evidencia recuperada supera el límite permitido:

1. Eliminar duplicados.
2. Priorizar fragmentos más relevantes.
3. Mantener diversidad de fuentes.
4. Conservar trazabilidad.

Nunca truncar el contexto de forma arbitraria.

---

# 8.14 Citas y Referencias

Cuando el modelo afirme que una cobertura aplica o no aplica, deberá asociar dicha afirmación con la evidencia utilizada.

La respuesta deberá conservar referencias suficientes para reconstruir el razonamiento.

---

# 8.15 Manejo de Incertidumbre

El prompt deberá instruir explícitamente al modelo para reconocer incertidumbre.

Ejemplos válidos

- "No existe evidencia suficiente."
- "La documentación disponible no permite determinar la cobertura."
- "Se requiere información adicional."

Nunca deberá completar información faltante mediante inferencias no respaldadas.

---

# 8.16 Prevención de Alucinaciones

El prompt deberá reforzar las siguientes reglas:

- No utilizar conocimiento externo.
- No completar reglas incompletas.
- No interpretar silencios como aprobaciones.
- No responder con información no recuperada.

La ausencia de evidencia nunca deberá interpretarse como evidencia positiva.

---

# 8.17 Independencia del Modelo

La arquitectura de prompts no deberá depender de un modelo específico.

El mismo PromptBuilder deberá funcionar con:

- GPT-4.1
- GPT-4.1-mini
- Gemini
- Azure OpenAI

Las diferencias entre proveedores deberán resolverse únicamente en la implementación del `LLMProvider`.

---

# 8.18 Versionado

Los prompts deberán versionarse.

Ejemplo

v1.0

v1.1

v2.0

Esto permitirá:

- Comparar resultados.
- Revertir cambios.
- Medir impacto en calidad.

---

# 8.19 Evaluación

Toda modificación importante en los prompts deberá validarse mediante pruebas.

Como mínimo deberán verificarse:

- Calidad de las respuestas.
- Consistencia.
- Uso correcto de la evidencia.
- Cumplimiento de guardrails.
- Ausencia de alucinaciones evidentes.

---

# 8.20 Principio Final

Los prompts forman parte de la arquitectura del sistema.

No deberán tratarse como texto incrustado en el código.

Deben diseñarse, mantenerse y evolucionar con el mismo rigor que cualquier otro componente de software.

# 9. Configuración, Inicialización y Operación del Sistema

---

# 9.1 Objetivo

Este capítulo define cómo el sistema obtiene su configuración, inicializa sus componentes y garantiza un entorno de ejecución consistente.

Toda configuración deberá ser externa al código fuente.

La aplicación deberá comportarse de manera idéntica independientemente del entorno donde sea desplegada.

---

# 9.2 Principios

La configuración deberá cumplir los siguientes principios:

- Centralizada.
- Tipada.
- Validada.
- Reutilizable.
- Segura.
- Independiente del entorno.

Nunca deberán existir constantes de configuración distribuidas por el proyecto.

---

# 9.3 Variables de Entorno

Toda configuración deberá obtenerse mediante variables de entorno.

Como referencia, el proyecto deberá soportar al menos las siguientes:

## OpenAI

OPENAI_API_KEY

OPENAI_MODEL

EMBEDDING_MODEL

---

## Documentos

DOCUMENTS_PATH

AFFILIATES_FILE

---

## Vector Store

VECTOR_DB_PATH

TOP_K_RESULTS

---

## Chunking

CHUNK_SIZE

CHUNK_OVERLAP

---

## Logging

LOG_LEVEL

LOG_FILE

---

## API

HOST

PORT

DEBUG

---

# 9.4 Archivo .env.example

El repositorio nunca deberá incluir un archivo `.env` real.

Únicamente deberá versionarse un archivo `.env.example`.

Ejemplo

```text
OPENAI_API_KEY=

OPENAI_MODEL=gpt-4.1

EMBEDDING_MODEL=text-embedding-3-small

DOCUMENTS_PATH=documents/

AFFILIATES_FILE=data/BD_afiliados.xlsx

VECTOR_DB_PATH=storage/chroma

TOP_K_RESULTS=5

CHUNK_SIZE=1000

CHUNK_OVERLAP=200

HOST=0.0.0.0

PORT=8000

DEBUG=False

LOG_LEVEL=INFO

LOG_FILE=logs/application.log
```

---

# 9.5 Settings Centralizados

Toda la configuración deberá cargarse desde un único componente.

Ejemplo

config/settings.py

Este componente será responsable de:

- Leer variables de entorno.
- Validarlas.
- Aplicar valores por defecto cuando corresponda.
- Exponer una configuración tipada al resto del sistema.

Ninguna otra clase deberá acceder directamente a `os.getenv()`.

---

# 9.6 Configuración por Entornos

El sistema deberá soportar múltiples perfiles de ejecución.

Como mínimo:

- development
- testing
- production

Las diferencias entre entornos deberán resolverse mediante configuración, nunca mediante cambios de código.

---

# 9.7 Inicialización del Sistema

Durante el arranque, la aplicación deberá ejecutar la siguiente secuencia:

```text
Inicio

↓

Cargar configuración

↓

Validar variables requeridas

↓

Inicializar logger

↓

Inicializar proveedores

↓

Inicializar Vector Store

↓

Verificar índice

↓

Registrar dependencias

↓

Levantar API

↓

Listo para recibir solicitudes
```

La inicialización deberá ser determinística y registrarse en los logs.

---

# 9.8 Verificación del Índice

Antes de aceptar solicitudes, el sistema deberá comprobar el estado del índice vectorial.

Escenarios posibles:

- Índice existente y válido.
- Índice inexistente.
- Índice corrupto.
- Índice desactualizado.

Dependiendo del escenario, podrá:

- reutilizar el índice,
- solicitar reindexación,
- reconstruirlo,
- o impedir el arranque si la configuración así lo establece.

---

# 9.9 Estrategia de Reindexación

La indexación no deberá ejecutarse automáticamente en cada inicio.

Se definen tres modos de operación:

AUTO

Utiliza el índice existente si continúa siendo válido.

---

FORCE

Reconstruye completamente el índice.

---

MANUAL

El operador ejecuta explícitamente el proceso de indexación.

---

# 9.10 Registro (Logging)

Toda la aplicación utilizará una configuración centralizada de logging.

Como mínimo se registrará:

- inicio del sistema,
- carga de configuración,
- inicialización de componentes,
- consultas recibidas,
- recuperación de evidencia,
- llamadas al LLM,
- errores,
- tiempos de ejecución.

Nunca utilizar `print()` como mecanismo de diagnóstico.

---

# 9.11 Manejo de Errores

Los errores deberán clasificarse.

Como mínimo:

- Configuración.
- Infraestructura.
- Recuperación documental.
- LLM.
- Validación.
- Dominio.
- API.

Cada categoría deberá generar mensajes claros y trazables.

Nunca exponer detalles internos al cliente.

---

# 9.12 Recuperación

Siempre que sea posible, el sistema deberá recuperarse automáticamente.

Ejemplos:

- continuar indexando aunque falle un documento;
- reutilizar el índice si el proveedor LLM no está disponible temporalmente;
- registrar advertencias sin detener el proceso cuando el problema no sea crítico.

Los errores críticos deberán impedir el arranque.

---

# 9.13 Health Check

La API deberá exponer un endpoint de diagnóstico.

Ejemplo

GET /health

El resultado deberá indicar:

- estado del servicio,
- disponibilidad del Vector Store,
- disponibilidad del proveedor LLM,
- disponibilidad del repositorio de afiliados,
- versión del sistema.

---

# 9.14 Observabilidad

El sistema deberá registrar métricas relevantes.

Como mínimo:

- tiempo de indexación,
- tiempo de recuperación,
- tiempo de respuesta del LLM,
- cantidad de chunks recuperados,
- número de documentos procesados,
- consultas atendidas,
- errores por categoría.

Estas métricas facilitarán el diagnóstico y la optimización futura.

---

# 9.15 Gestión de Dependencias

Todas las dependencias deberán inicializarse mediante Dependency Injection.

Nunca crear proveedores directamente dentro de los casos de uso.

La inicialización se realizará desde:

config/dependencies.py

---

# 9.16 Docker

El proyecto deberá ser completamente reproducible.

Como mínimo deberá incluir:

Dockerfile

docker-compose.yml

Los contenedores deberán permitir ejecutar la aplicación sin modificaciones adicionales.

---

# 9.17 Scripts de Operación

Se recomienda incluir scripts para tareas operativas.

Ejemplos:

- index_documents.py
- rebuild_index.py
- validate_documents.py
- clear_storage.py

Estos scripts deberán reutilizar los mismos servicios del sistema.

Nunca duplicar lógica.

---

# 9.18 Seguridad

Nunca registrar:

- API Keys.
- Tokens.
- Contraseñas.
- Datos sensibles del afiliado.

Los logs deberán anonimizar cualquier información confidencial.

---

# 9.19 Principio de Configuración

Todo comportamiento configurable deberá obtenerse desde la configuración.

Nunca modificar el código para cambiar:

- modelos,
- rutas,
- parámetros de chunking,
- cantidad de resultados,
- proveedores.

---

# 9.20 Principio Final

La configuración constituye un componente de la arquitectura.

Un sistema correctamente diseñado puede migrar entre entornos cambiando únicamente su configuración, sin modificar una sola línea de código.

# 10. Estándares de Ingeniería y Calidad del Código

---

# 10.1 Objetivo

Este capítulo define los principios y estándares de desarrollo que deberán seguirse durante toda la implementación del proyecto.

Su propósito es garantizar:

- Consistencia.
- Legibilidad.
- Escalabilidad.
- Mantenibilidad.
- Testabilidad.
- Bajo acoplamiento.
- Alta cohesión.

Toda contribución deberá cumplir estas reglas antes de considerarse terminada.

---

# 10.2 Filosofía de Ingeniería

El proyecto prioriza:

- Arquitectura sobre velocidad.
- Simplicidad sobre complejidad.
- Claridad sobre ingenio.
- Mantenibilidad sobre optimización prematura.
- Evidencia sobre suposiciones.

Cada decisión técnica deberá poder justificarse.

---

# 10.3 Principios SOLID

Toda implementación deberá respetar los principios SOLID.

## Single Responsibility Principle

Cada clase deberá tener una única responsabilidad.

Ejemplo correcto

DocumentLoader

solo carga documentos.

Ejemplo incorrecto

DocumentLoader

↓

lee documentos

↓

genera embeddings

↓

consulta OpenAI

↓

guarda en Chroma

---

## Open / Closed Principle

Los componentes deberán permitir nuevas implementaciones sin modificar código existente.

Ejemplo

Agregar:

PdfDocumentLoader

No deberá requerir modificar:

WordDocumentLoader

---

## Liskov Substitution Principle

Toda implementación deberá poder sustituir su interfaz.

Ejemplo

LLMProvider

↓

OpenAIProvider

↓

GeminiProvider

Sin modificar Application.

---

## Interface Segregation Principle

Las interfaces deberán ser pequeñas y específicas.

Nunca crear interfaces gigantes.

---

## Dependency Inversion Principle

Application dependerá únicamente de abstracciones.

Nunca de implementaciones concretas.

---

# 10.4 DRY

No repetir lógica.

Si una lógica aparece dos veces, evaluar su extracción.

No aplicar DRY de forma obsesiva.

La claridad tiene prioridad.

---

# 10.5 KISS

La solución más simple que cumpla los requisitos será la preferida.

No introducir complejidad sin necesidad.

---

# 10.6 YAGNI

No implementar funcionalidades que aún no son necesarias.

La arquitectura podrá prepararse para evolucionar.

El código solo implementará los requerimientos actuales.

---

# 10.7 Clean Code

Todo código deberá ser:

- Fácil de leer.
- Fácil de modificar.
- Fácil de probar.
- Fácil de eliminar.

El código se escribe para personas.

Los compiladores son una consecuencia.

---

# 10.8 Convenciones de Nombres

Las clases deberán utilizar PascalCase.

Ejemplo

CoverageAnalysisService

---

Las funciones deberán utilizar snake_case.

Ejemplo

retrieve_documents()

---

Los archivos utilizarán snake_case.

Ejemplo

coverage_service.py

---

Las constantes utilizarán MAYÚSCULAS.

Ejemplo

DEFAULT_TOP_K

---

Los atributos privados utilizarán "_".

---

# 10.9 Type Hints

Todo método público deberá utilizar type hints.

Ejemplo

```python
def retrieve(query: str) -> list[DocumentChunk]:
```

Nunca utilizar Any salvo casos excepcionales claramente justificados.

---

# 10.10 Docstrings

Toda clase pública deberá documentarse.

Como mínimo deberá describir:

- propósito,
- parámetros,
- valor de retorno,
- excepciones relevantes.

Los docstrings deberán explicar el "por qué", no repetir el código.

---

# 10.11 Manejo de Excepciones

Nunca capturar excepciones genéricas sin justificación.

Incorrecto

```python
except:
    pass
```

Correcto

```python
except DocumentNotFoundError:
```

Toda excepción deberá aportar información útil.

---

# 10.12 Logging

Registrar únicamente eventos relevantes.

No utilizar logging como sustituto del depurador.

Nunca registrar:

- API Keys.
- Tokens.
- Datos sensibles.
- Información médica completa del afiliado.

---

# 10.13 Reglas de Importación

Presentation

↓

Application

↓

Domain

↓

Infrastructure

Nunca invertir esta dirección.

Ejemplo prohibido

Domain

↓

FastAPI

Application

↓

OpenAI SDK

Presentation

↓

Pandas

---

# 10.14 Reglas para Métodos

Preferir métodos pequeños.

Como referencia:

20–30 líneas.

Si un método requiere múltiples comentarios para entenderse, probablemente deba dividirse.

---

# 10.15 Reglas para Clases

Las clases deberán representar conceptos del dominio.

Evitar clases "utilitarias" con múltiples responsabilidades.

---

# 10.16 DTOs

Toda comunicación entre capas deberá realizarse mediante DTOs.

Nunca transportar diccionarios sin estructura.

Nunca devolver objetos del SDK de terceros.

---

# 10.17 Dependencias

Cada dependencia nueva deberá justificar:

- qué problema resuelve,
- por qué no existe una solución estándar,
- impacto en mantenimiento,
- facilidad de reemplazo.

---

# 10.18 Revisión de Código

Antes de aceptar una contribución deberán verificarse al menos los siguientes puntos:

- Compila.
- Supera las pruebas.
- Respeta la arquitectura.
- Mantiene el tipado.
- No introduce acoplamientos.
- No rompe interfaces existentes.
- Mantiene la trazabilidad.

---

# 10.19 Calidad Automatizada

El proyecto utilizará herramientas automáticas.

Como mínimo:

Ruff

Black

MyPy

Pytest

Todo cambio deberá superar estas validaciones antes de integrarse.

---

# 10.20 Definición de Terminado (Definition of Done)

Una funcionalidad se considerará terminada únicamente cuando:

- Cumpla el requerimiento funcional.
- Respete la arquitectura.
- Utilice Dependency Injection.
- Esté correctamente tipada.
- Disponga de pruebas.
- Pase las validaciones automáticas.
- Esté documentada cuando corresponda.
- No introduzca deuda técnica conocida.

---

# 10.21 Métricas de Calidad

Como guía general se recomienda:

- Cobertura de pruebas superior al 80%.
- Sin errores de tipado.
- Sin advertencias críticas del linter.
- Complejidad ciclomática baja.
- Métodos pequeños y cohesivos.

Estas métricas orientan la calidad, pero no sustituyen la revisión técnica.

---

# 10.22 Principio Final

El objetivo no es escribir código que funcione únicamente para esta prueba técnica.

El objetivo es construir una base de software que pueda mantenerse, ampliarse y evolucionar durante años sin perder claridad ni calidad.

Cada línea de código deberá contribuir a esa visión.

# 11. Estrategia de Validación y Plan Maestro de Pruebas

---

# 11.1 Objetivo

Este capítulo define la estrategia de validación utilizada para garantizar que el sistema cumple los requisitos funcionales, arquitectónicos y de calidad definidos en este documento.

El objetivo de las pruebas no es únicamente detectar errores.

También deben demostrar:

- Correctitud.
- Robustez.
- Trazabilidad.
- Mantenibilidad.
- Calidad del razonamiento.

Toda funcionalidad desarrollada deberá poder validarse mediante pruebas reproducibles.

---

# 11.2 Principios

La estrategia de pruebas seguirá los siguientes principios.

- Automatización.
- Independencia.
- Repetibilidad.
- Aislamiento.
- Cobertura.
- Claridad.

Cada prueba deberá validar un comportamiento concreto.

Nunca múltiples responsabilidades.

---

# 11.3 Pirámide de Pruebas

El proyecto utilizará una estrategia basada en la pirámide de testing.

```

               End to End
                  ▲
                  │
          Integration Tests
                  ▲
                  │
             Unit Tests

```

La mayor cantidad de pruebas deberá concentrarse en pruebas unitarias.

---

# 11.4 Pruebas Unitarias

Objetivo

Validar componentes de manera aislada.

Componentes candidatos.

- DocumentLoader
- ChunkStrategy
- MetadataBuilder
- PromptBuilder
- ResponseValidator
- RuleEngine
- CoverageDecisionEngine
- AffiliateRepository
- LLMProvider (Mock)

Nunca dependerán de OpenAI real.

Nunca dependerán de Chroma real.

Nunca dependerán del sistema de archivos.

---

# 11.5 Pruebas de Integración

Objetivo

Validar la interacción entre componentes.

Ejemplos.

DocumentLoader

↓

ChunkStrategy

↓

EmbeddingProvider

↓

VectorStore

---

AffiliateRepository

↓

ReasoningEngine

↓

PromptBuilder

---

Retriever

↓

VectorStore

↓

LLMProvider

---

Estas pruebas verifican que los componentes colaboran correctamente.

---

# 11.6 Pruebas End-to-End

Objetivo

Validar el flujo completo.

Ejemplo.

Usuario

↓

API

↓

Reasoning Engine

↓

Retriever

↓

LLM

↓

Respuesta

Estas pruebas representan el comportamiento esperado desde la perspectiva del usuario.

---

# 11.7 Validación del Pipeline de Ingesta

Deberán verificarse al menos los siguientes escenarios.

Documento válido.

Documento vacío.

Documento corrupto.

Documento duplicado.

Documento actualizado.

Documento nuevo.

Documento con caracteres especiales.

Documento muy grande.

Cada escenario deberá producir un resultado esperado claramente definido.

---

# 11.8 Validación del Chunking

Se verificará que.

Los chunks respetan el tamaño configurado.

Existe overlap.

No se pierde contenido.

No existen duplicados.

Los metadatos son correctos.

Los hashes permanecen consistentes.

---

# 11.9 Validación del Vector Store

Comprobar.

Inserción.

Persistencia.

Búsqueda.

Recuperación.

Actualización.

Reindexación.

---

# 11.10 Validación del Retrieval

Cada consulta deberá recuperar información relevante.

Casos mínimos.

Consulta exacta.

Consulta parcial.

Sin coincidencias.

Múltiples documentos.

Documentos similares.

Resultados ambiguos.

---

# 11.11 Validación del Motor de Razonamiento

Comprobar.

Interpretación correcta de la intención.

Obtención del afiliado.

Construcción de la decisión preliminar.

Manejo de evidencia contradictoria.

Manejo de evidencia insuficiente.

Construcción del prompt.

---

# 11.12 Validación del Prompt Builder

Verificar.

Construcción correcta.

Variables reemplazadas.

Orden correcto.

No duplicación.

Aplicación de guardrails.

Consistencia entre versiones.

---

# 11.13 Validación del LLM

Estas pruebas deberán ejecutarse utilizando un proveedor simulado cuando sea posible.

Aspectos a validar.

Construcción del request.

Interpretación del response.

Manejo de errores.

Timeouts.

Respuestas vacías.

Respuestas inválidas.

---

# 11.14 Validación de Guardrails

El sistema deberá demostrar que.

Nunca inventa información.

Reconoce incertidumbre.

No responde sin evidencia.

No contradice documentos.

No utiliza conocimiento externo.

Este conjunto de pruebas constituye uno de los principales mecanismos para reducir alucinaciones.

---

# 11.15 Casos Límite

Como mínimo deberán probarse.

Afiliado inexistente.

Documento vacío.

Sin documentos.

Sin embeddings.

Sin conexión al proveedor LLM.

Vector Store vacío.

Consulta ambigua.

Consulta muy larga.

Consulta sin procedimiento.

Consulta sin afiliado.

---

# 11.16 Pruebas de Rendimiento

Se recomienda medir.

Tiempo de indexación.

Tiempo de recuperación.

Tiempo del proveedor LLM.

Tiempo total por consulta.

Cantidad de chunks recuperados.

Estas métricas permitirán detectar cuellos de botella.

---

# 11.17 Métricas de Calidad

Como referencia.

Cobertura de pruebas superior al 80%.

Tiempo promedio de consulta inferior al objetivo definido.

Sin errores críticos.

Sin fallos de tipado.

Sin advertencias del linter.

Las métricas deberán revisarse de manera conjunta.

Nunca aisladamente.

---

# 11.18 Criterios de Aceptación

Una funcionalidad se considerará aceptada cuando.

Cumpla el requerimiento funcional.

Supere todas las pruebas.

Respete la arquitectura.

No introduzca deuda técnica.

Mantenga la trazabilidad.

No genere regresiones.

---

# 11.19 Evidencia de Calidad

El proyecto deberá generar evidencia objetiva de su funcionamiento.

Ejemplos.

Resultados de Pytest.

Cobertura.

Logs de indexación.

Logs de recuperación.

Capturas de ejecución.

Ejemplos de respuestas.

Esto facilitará la evaluación de la prueba técnica.

---

# 11.20 Principio Final

La calidad del sistema no se medirá únicamente por las respuestas que produce.

Se medirá por la capacidad de demostrar, mediante pruebas reproducibles y evidencia objetiva, que dichas respuestas son correctas, trazables y coherentes con la arquitectura definida.

# 12. Roadmap de Implementación

---

# 12.1 Objetivo

Este roadmap define el orden oficial de implementación del proyecto.

Las fases deberán ejecutarse secuencialmente.

Cada fase establece:

- Objetivos.
- Componentes.
- Dependencias.
- Entregables.
- Criterios de aceptación.

No deberá iniciarse una fase mientras la anterior no se encuentre completada.

---

# 12.2 Principios

El desarrollo seguirá una estrategia incremental.

Cada fase deberá producir un sistema funcional.

Nunca construir múltiples componentes críticos simultáneamente.

Cada incremento deberá ser:

- funcional,
- verificable,
- documentado,
- estable.

---

# 12.3 Fase 1 – Inicialización del Proyecto

## Objetivo

Preparar la base del proyecto.

---

### Actividades

- Crear estructura de carpetas.
- Configurar uv.
- Configurar pyproject.toml.
- Configurar Ruff.
- Configurar Black.
- Configurar MyPy.
- Configurar Pytest.
- Crear README.
- Crear ESPECIFICACION.md.
- Crear .env.example.
- Configurar logging.
- Configurar Dependency Injection.
- Configurar settings.

---

### Entregables

Proyecto compilando correctamente.

Sin lógica funcional.

---

### Criterio de aceptación

El proyecto inicia sin errores.

---

# 12.4 Fase 2 – Dominio

## Objetivo

Construir el núcleo del negocio.

---

### Actividades

Crear:

Entities

DTOs

Interfaces

Exceptions

Value Objects

Repositories

Providers

Factories

---

### Restricción

No utilizar OpenAI.

No utilizar Pandas.

No utilizar Chroma.

---

### Entregable

Dominio completamente desacoplado.

---

# 12.5 Fase 3 – Infraestructura

## Objetivo

Implementar las interfaces definidas.

---

### Componentes

WordDocumentLoader

ExcelAffiliateRepository

OpenAIProvider

OpenAIEmbeddingProvider

ChromaVectorStore

RecursiveChunkStrategy

---

### Entregable

Infraestructura completamente funcional.

---

# 12.6 Fase 4 – Pipeline de Ingesta

## Objetivo

Construir el proceso de indexación.

---

### Flujo

Leer documentos

↓

Normalizar

↓

Validar

↓

Chunking

↓

Metadata

↓

Embeddings

↓

Persistencia

---

### Validaciones

Documentos vacíos.

Duplicados.

Hash.

Reindexación.

---

### Entregable

Base vectorial creada.

---

# 12.7 Fase 5 – Pipeline de Consulta

## Objetivo

Implementar el flujo RAG.

---

### Componentes

Retriever

Reasoning Engine

Prompt Builder

Response Builder

Validator

---

### Flujo

Consulta

↓

Retriever

↓

Reasoning

↓

LLM

↓

Respuesta

---

### Entregable

Sistema capaz de responder consultas.

---

# 12.8 Fase 6 – API REST

## Objetivo

Exponer funcionalidades.

---

### Endpoints

POST /query

POST /reindex

GET /health

GET /metrics

---

### Restricción

Los Controllers nunca contendrán lógica de negocio.

---

### Entregable

API completamente funcional.

---

# 12.9 Fase 7 – Testing

## Objetivo

Construir pruebas automatizadas.

---

### Actividades

Unit Tests.

Integration Tests.

End-to-End.

Mocks.

Fixtures.

Cobertura.

---

### Entregable

Suite de pruebas automatizada.

---

# 12.10 Fase 8 – Optimización

## Objetivo

Mejorar calidad.

---

### Actividades

Optimización del Retriever.

Optimización del Prompt.

Optimización del Contexto.

Optimización de Latencia.

Optimización del Chunking.

---

### Entregable

Versión optimizada.

---

# 12.11 Fase 9 – Documentación

## Objetivo

Completar documentación.

---

### Documentos

README

ESPECIFICACION.md

ARCHITECTURE.md

ROADMAP.md

CHANGELOG.md

---

### Entregable

Proyecto completamente documentado.

---

# 12.12 Dependencias entre Fases

```

Fase 1

↓

Fase 2

↓

Fase 3

↓

Fase 4

↓

Fase 5

↓

Fase 6

↓

Fase 7

↓

Fase 8

↓

Fase 9

```

Nunca invertir el orden.

---

# 12.13 Definition of Ready

Una tarea podrá comenzar únicamente cuando:

- Se encuentren definidos los requisitos.
- Existan interfaces disponibles.
- Exista diseño aprobado.
- No existan dependencias bloqueantes.

---

# 12.14 Definition of Done

Una fase se considerará completada cuando:

- Compile correctamente.
- Pase todas las pruebas.
- Respete la arquitectura.
- Mantenga el tipado.
- Mantenga la trazabilidad.
- No introduzca deuda técnica crítica.
- Esté documentada.

---

# 12.15 Riesgos Técnicos

Riesgos identificados.

- Mala recuperación documental.
- Chunking inadecuado.
- Contexto excesivo.
- Hallucinations.
- Acoplamiento con OpenAI.
- Baja trazabilidad.

Cada riesgo deberá mitigarse mediante la arquitectura definida.

---

# 12.16 Criterios de Calidad Final

Antes de la entrega deberán verificarse.

- Arquitectura respetada.
- Pipeline funcional.
- Cobertura adecuada.
- Logs completos.
- Tipado correcto.
- Sin secretos en el repositorio.
- README actualizado.
- ESPECIFICACION.md actualizado.

---

# 12.17 Entregables Finales

El proyecto deberá contener como mínimo:

- Código fuente.
- API REST.
- Motor RAG.
- Índice vectorial.
- Suite de pruebas.
- README.
- ESPECIFICACION.md.
- Documentación técnica.
- .env.example.

---

# 12.18 Evolución Futura

La arquitectura deberá permitir incorporar sin rediseños mayores:

- Nuevos modelos LLM.
- Nuevos proveedores de embeddings.
- Nuevos formatos documentales.
- Nuevos Vector Stores.
- Múltiples repositorios de afiliados.
- Múltiples agentes especializados.
- Nuevas reglas de negocio.

---

# 12.19 Checklist de Entrega

Antes de entregar el proyecto deberá verificarse:

☐ El proyecto inicia correctamente.

☐ El índice se genera correctamente.

☐ La API responde consultas.

☐ Las respuestas contienen evidencia.

☐ Los datos del afiliado se utilizan correctamente.

☐ No existen credenciales en el repositorio.

☐ Todas las pruebas pasan.

☐ La documentación está completa.

☐ La arquitectura se mantiene desacoplada.

☐ El código sigue los estándares definidos.

---

# 12.20 Principio Final

El objetivo de este roadmap no es únicamente finalizar una prueba técnica.

Su propósito es construir un sistema cuya arquitectura, implementación, operación y evolución sigan una estrategia coherente desde el primer commit hasta su puesta en producción.

Cada fase representa un incremento funcional y verificable del sistema, reduciendo riesgos y facilitando la evolución futura.

# 13. Constitución Arquitectónica del Proyecto

---

# 13.1 Propósito

Este capítulo establece los principios fundamentales que gobiernan toda decisión de arquitectura, diseño e implementación del proyecto.

Estos principios prevalecen sobre decisiones particulares de implementación.

Si una decisión técnica entra en conflicto con alguno de estos principios, deberá justificarse explícitamente o descartarse.

---

# 13.2 Principio 1 — La fuente de verdad nunca será el LLM

El modelo de lenguaje no constituye la fuente oficial de conocimiento del sistema.

La fuente de verdad estará compuesta exclusivamente por:

- Los documentos indexados.
- Los datos estructurados del afiliado.

El LLM únicamente interpreta, relaciona y comunica la información disponible.

Nunca deberá generar conocimiento nuevo.

---

# 13.3 Principio 2 — Toda respuesta debe ser trazable

Cada respuesta emitida por el sistema deberá poder reconstruirse.

Como mínimo deberá conocerse:

- consulta original,
- afiliado utilizado,
- documentos consultados,
- fragmentos recuperados,
- modelo utilizado,
- versión del prompt,
- nivel de confianza.

Si una respuesta no puede explicarse, deberá considerarse inválida.

---

# 13.4 Principio 3 — La evidencia tiene prioridad sobre la confianza

Una respuesta con alta confianza pero sin evidencia documental es inaceptable.

El sistema siempre preferirá responder:

"No existe evidencia suficiente."

antes que producir una respuesta aparentemente correcta pero no verificable.

---

# 13.5 Principio 4 — El sistema debe reconocer la incertidumbre

La incertidumbre forma parte del dominio.

No constituye un error.

Cuando la información sea insuficiente, contradictoria o ambigua, el sistema deberá indicarlo explícitamente.

Nunca completar información mediante suposiciones.

---

# 13.6 Principio 5 — La arquitectura debe sobrevivir al cambio tecnológico

El proyecto deberá poder reemplazar:

- el proveedor LLM,
- el proveedor de embeddings,
- el Vector Store,
- el repositorio de afiliados,
- el formato documental,

sin modificar la lógica del negocio.

La dependencia de cualquier tecnología deberá permanecer encapsulada en Infrastructure.

---

# 13.7 Principio 6 — Las interfaces son contratos

Las interfaces representan acuerdos estables entre componentes.

Toda implementación deberá respetar completamente el contrato definido.

Las implementaciones podrán cambiar.

Los contratos deberán permanecer estables.

---

# 13.8 Principio 7 — Cada componente tiene una única responsabilidad

Todo componente deberá responder claramente a una pregunta:

"¿Cuál es exactamente mi responsabilidad?"

Si la respuesta contiene más de una responsabilidad, el diseño deberá revisarse.

---

# 13.9 Principio 8 — La simplicidad es una decisión arquitectónica

El proyecto favorecerá soluciones simples.

La complejidad únicamente será aceptable cuando resuelva un problema real.

Nunca introducir abstracciones innecesarias.

---

# 13.10 Principio 9 — El conocimiento fluye hacia arriba

La dependencia entre capas siempre seguirá esta dirección.

Presentation

↓

Application

↓

Domain

↓

Infrastructure

Nunca en sentido contrario.

---

# 13.11 Principio 10 — Los prompts también son software

Los prompts forman parte de la arquitectura.

Deberán:

- versionarse,
- probarse,
- documentarse,
- evolucionar,

igual que cualquier otro componente del sistema.

---

# 13.12 Principio 11 — La IA debe ser determinista siempre que sea posible

Todo comportamiento determinista deberá implementarse mediante código.

El LLM únicamente resolverá problemas donde realmente aporte valor.

Nunca utilizar IA para sustituir reglas simples.

---

# 13.13 Principio 12 — La observabilidad no es opcional

Todo comportamiento relevante deberá registrarse.

El sistema deberá facilitar la comprensión de:

- qué ocurrió,
- cuándo ocurrió,
- por qué ocurrió.

Nunca ocultar errores relevantes.

---

# 13.14 Principio 13 — La calidad se construye desde el diseño

Las pruebas no corrigen una mala arquitectura.

La calidad comienza:

- en las interfaces,
- en las responsabilidades,
- en el diseño de dependencias,
- en la claridad del dominio.

---

# 13.15 Principio 14 — La seguridad forma parte del diseño

La seguridad no deberá añadirse posteriormente.

Desde el inicio deberán protegerse:

- credenciales,
- configuraciones,
- datos sensibles,
- información del afiliado,
- registros del sistema.

---

# 13.16 Principio 15 — La evolución debe ser natural

Toda nueva funcionalidad deberá encontrar un lugar evidente dentro de la arquitectura existente.

Si una nueva característica obliga a reorganizar completamente el proyecto, la arquitectura deberá reconsiderarse.

---

# 13.17 Principio 16 — La mantenibilidad tiene prioridad sobre la optimización prematura

Una arquitectura clara produce mejores resultados a largo plazo que una optimización temprana.

Primero:

- claridad,
- diseño,
- pruebas.

Después:

- optimización.

---

# 13.18 Principio 17 — El sistema debe explicar sus decisiones

Toda decisión relevante deberá responder a dos preguntas.

¿Por qué respondió esto?

¿Con base en qué evidencia?

La capacidad de explicación constituye un requisito funcional del sistema.

---

# 13.19 Principio 18 — La arquitectura es el activo principal del proyecto

El valor del proyecto no reside únicamente en el código.

Reside en la capacidad de evolucionar, mantenerse y adaptarse sin perder coherencia.

Cada decisión deberá proteger esa capacidad.

---

# 13.20 Declaración Final

Este documento constituye la especificación oficial de arquitectura del proyecto.

Toda implementación futura deberá respetar los principios aquí definidos.

Las tecnologías podrán cambiar.

Las librerías podrán sustituirse.

Los modelos de IA evolucionarán.

Sin embargo, los principios arquitectónicos permanecerán como la base estable sobre la cual evolucionará el sistema.

La arquitectura deberá sobrevivir a la tecnología.

# 14. Addendum — Decisiones de Revisión Arquitectónica (Aprobadas)

Este capítulo registra las decisiones aprobadas tras la revisión arquitectónica (ver ARCHITECTURE_REVIEW.md, 2026-07-17).

**Este capítulo prevalece sobre cualquier sección anterior que lo contradiga.**

---

## 14.1 Dirección de dependencias (corrige §2.3, §10.13, §13.10)

La dirección correcta es:

```
Presentation → Application → Domain ← Infrastructure
```

Infrastructure implementa las interfaces (ports) declaradas en Domain.

Domain nunca depende de Infrastructure.

Los diagramas anteriores que muestran `Domain → Infrastructure` quedan corregidos.

---

## 14.2 Orquestación única (corrige §3.12)

Jerarquía oficial de orquestación:

1. `AnalyzeCoverageUseCase` (application/use_cases): punto de entrada único del flujo de consulta.
2. `ReasoningEngine` (application/reasoning): sub-orquestador exclusivo de la etapa de razonamiento.

`CoverageAnalysisService` queda eliminado del diseño.

El nombre oficial del caso de uso es `AnalyzeCoverageUseCase` (sustituye a `ResponderConsultaUseCase`).

---

## 14.3 Ubicación de interfaces y factories (corrige §4.6, §12.4)

- Todas las interfaces (ports) viven en Domain: `domain/repositories/`, `domain/providers/`.
- La carpeta `application/interfaces/` queda eliminada.
- Los factories viven en Infrastructure.
- `config/dependencies.py` es el composition root: único módulo autorizado a importar de todas las capas para cablear implementaciones.
- Se elimina "Factories" de las actividades de la Fase 2 (Dominio).

---

## 14.4 Reglas de negocio en Domain (corrige §4.6)

Las reglas de cobertura evaluables determinísticamente (vigencia, estado, periodos de carencia) se implementan en Domain como servicios de dominio.

`application/reasoning/` solo orquesta: invoca reglas de dominio, retrieval y prompt building.

---

## 14.5 Contrato de POST /query

El request incluye siempre:

```json
{
  "affiliate_id": "<identificador estructurado>",
  "question": "<consulta en lenguaje natural>"
}
```

El afiliado nunca se resuelve por extracción de nombre desde texto libre.

---

## 14.6 Una sola llamada al LLM

El flujo de consulta realiza exactamente una llamada al LLM, construida por el PromptBuilder.

El Intent Analyzer es determinístico (normalización y preparación de la consulta); no invoca al LLM.

La consulta del usuario se utiliza directamente como query de retrieval (embedding de la pregunta).

La decisión preliminar del Coverage Decision Engine se construye únicamente con datos estructurados del afiliado. La interpretación de reglas documentales corresponde al LLM con la evidencia recuperada.

---

## 14.7 EvidenceStrength (corrige §7.13)

Se elimina el campo numérico `confidence`.

Se utiliza el enum `EvidenceStrength` con valores:

- INSUFFICIENT
- PARTIAL
- STRONG

Derivado de reglas explícitas (scores de retrieval y evaluación de suficiencia), nunca inventado por el LLM.

---

## 14.8 Protección de /reindex

`POST /reindex` requiere API Key configurable mediante la variable de entorno `REINDEX_API_KEY`, enviada en el header `X-API-Key`.

---

## 14.9 Testing por fase (corrige §12.9)

Cada fase (2–6) entrega sus propias pruebas unitarias y de integración junto con el código.

La Fase 7 consolida: E2E, rendimiento y cobertura.

---

## 14.10 Retrieval con umbral de relevancia

El resultado del retrieval incluye el score de similitud de cada chunk.

Nueva variable de entorno: `MIN_SIMILARITY_SCORE`.

Cero chunks sobre el umbral constituye la señal de evidencia insuficiente.

---

## 14.11 Manifiesto del índice

Junto al índice vectorial se persiste un manifiesto con: `embedding_model`, `chunk_size`, `chunk_overlap` y versión del pipeline.

Si el manifiesto no coincide con la configuración actual, el índice se considera inválido y se requiere reindexación FULL.

Al reindexar un documento modificado, primero se eliminan sus chunks anteriores por `document_id`.

---

## 14.12 Aclaración de embeddings (corrige §6.12)

Un embedding por chunk; nunca un embedding de un documento completo.

El batching de chunks en una sola llamada a la API de embeddings está permitido y es deseable.

---

## 14.13 Trazabilidad v1

La trazabilidad se implementa mediante:

1. El `CoverageResponse` transporta evidencia y metadatos (modelo, versión de prompt, chunks utilizados).
2. Log estructurado JSON por consulta con `trace_id`.

Campos nunca registrables en logs: nombre del afiliado, número de documento, diagnósticos e información médica.

---

## 14.14 Herramientas de calidad

Se utiliza Ruff para linting y formateo (`ruff format` sustituye a Black).

---

## 14.15 Fuera de alcance v1 (aclaraciones)

- Historial de conversación / sesiones.
- Validación semántica de alucinaciones mediante segundo LLM (evolución futura; la v1 implementa validaciones determinísticas: formato, citas existentes, citas referenciando chunks realmente entregados).
