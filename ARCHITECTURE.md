# Arquitectura del Sistema NLWeb - Noticias

Este documento describe la arquitectura técnica de la implementación de un sitio web de noticias ficticio compatible con el estándar **NLWeb** (Natural Language Web). El sistema utiliza un patrón RAG (Retrieval-Augmented Generation) para permitir a los usuarios conversar con el contenido del sitio.

## 1. Visión General

El sistema es una aplicación web híbrida que combina:
1.  **Frontend Estático/Dinámico:** Renderiza noticias desde un feed XML local.
2.  **Backend API (Flask):** Sirve la aplicación, maneja la lógica de búsqueda vectorial y actúa como puente hacia los servicios de IA.
3.  **Pipeline de Datos (ETL):** Un script de ingesta que procesa las noticias, genera embeddings y las almacena en una base de datos vectorial (Qdrant) con formato estructurado (Schema.org).

## 2. Diagrama de Componentes

```mermaid
graph TD
    User[Usuario / Navegador]
    
    subgraph Frontend
        HTML[index.html]
        JS[app.js]
    end
    
    subgraph Backend Server
        Flask[server.py (Flask)]
        Static[Servidor de Archivos]
        SearchAPI[/search Endpoint]
    end
    
    subgraph Data Pipeline
        Feed[feed.xml]
        ETL[cargar_datos.py]
    end
    
    subgraph External Services
        OpenAI_Emb[OpenAI Embeddings]
        OpenAI_Chat[OpenAI GPT-4o]
        Qdrant[(Qdrant Vector DB)]
    end

    %% Flujos
    User -->|Visita| Flask
    Flask -->|Sirve| HTML
    JS -->|Fetch GET| Static
    Static -->|Retorna| Feed
    JS -->|Renderiza| HTML
    
    %% Flujo de Chat
    User -->|Pregunta| JS
    JS -->|GET /search?q=...| SearchAPI
    SearchAPI -->|Texto| OpenAI_Emb
    OpenAI_Emb -->|Vector| SearchAPI
    SearchAPI -->|Busca Vector| Qdrant
    Qdrant -->|Contexto + Schema| SearchAPI
    SearchAPI -->|Prompt + Contexto| OpenAI_Chat
    OpenAI_Chat -->|Respuesta Natural| SearchAPI
    SearchAPI -->|JSON (Answer + Source Data)| JS
    
    %% Flujo de Ingesta
    ETL -->|Lee| Feed
    ETL -->|Genera| OpenAI_Emb
    ETL -->|Upsert (Payload Schema.org)| Qdrant
```

## 3. Descripción de Componentes

### 3.1 Frontend (`frontend/`)
El cliente es una Single Page Application (SPA) ligera.
- `index.html`: Estructura base. Contiene el contenedor de noticias y el widget de chat flotante.
- `app.js`:
    - Carga de Noticias: Realiza un `fetch` a `/feed.xml`, parsea el XML en el navegador y renderiza las tarjetas de noticias.
    - Chatbot: Captura la entrada del usuario y realiza peticiones GET al endpoint `/search` del backend, siguiendo el estándar NLWeb. Muestra la respuesta del bot en la interfaz.

### 3.2 Fuente de Datos (`feed.xml`)
Un archivo RSS 2.0 estático que actúa como la "base de datos" cruda para la visualización del frontend y como fuente para el proceso de ingesta de datos.

### 3.3 Backend (`server.py`)
Servidor web construido con Flask.
- Rutas Estáticas: Sirve el frontend y el archivo `feed.xml`.
- Cumplimiento NLWeb: Expone rutas estándar como `/.well-known/ai-plugin.json` y `/openapi.yaml` (referenciadas en código).
- Endpoint `/search`:
    - Recibe una consulta (q).
    - Vectoriza la consulta usando text-embedding-ada-002.
    - Consulta a Qdrant para obtener los 3 fragmentos más relevantes.
    - Construye un prompt con el contexto recuperado.
    - Solicita una respuesta a GPT-4o.
    - Retorna un JSON enriquecido con la respuesta en texto y los datos estructurados (`source_data`).

### 3.4 Ingesta de Datos (`cargar_datos.py`)
Script ejecutado bajo demanda (`load_data.bat`) para poblar la memoria de la IA.
1. Lee feed.xml.
2. Extrae título, descripción, enlace y fecha.
3. Crea un objeto JSON compatible con Schema.org (NewsArticle).
4. Genera embeddings del texto combinado (Título + Descripción).
5. Sube a Qdrant: Vector + Payload (Texto + Schema).

## 4. Stack Tecnológico
- Lenguaje: Python 3.12
- Framework Web: Flask 3.1.2
- IA & LLM: OpenAI API (gpt-4o, text-embedding-ada-002)
- Base de Datos Vectorial: Qdrant (vía `qdrant-client`)
- Gestor de Paquetes: `uv` (basado en `pyproject.toml` y `uv.lock`)
- Utilidades: `xmltodict`, `python-dotenv`.

## 5. Flujo de Datos (Data Flow)

A. Flujo de Renderizado (Usuario abre la web)
1. El navegador solicita `index.html`.
2. `app.js` solicita `/feed.xml`.
3. El navegador parsea el XML y genera el HTML de las noticias dinámicamente.

B. Flujo de Ingesta (Administrador ejecuta carga)
1. Python lee `feed.xml`.
2. Se transforma cada `<item>` en un diccionario Python y luego en un objeto Schema.org.
3. Se envían los textos a OpenAI para obtener vectores (1536 dimensiones).
4. Se guardan vectores y metadatos en la colección `noticias-futuro` en Qdrant.

C. Flujo de Consulta (Usuario pregunta al Chat)
1. Usuario escribe: "¿Qué pasó con Millie Bobby Brown?".
2. Frontend envía GET: `/search?q=Qué pasó con Millie....`.
3. Backend convierte la pregunta en vector.
4. Qdrant devuelve las noticias semánticamente similares (ej. el artículo sobre su entrevista).
5. Backend envía a GPT-4o: "Contexto: [Texto de la noticia]... Pregunta: ¿Qué pasó con...?".
6. Backend devuelve JSON:
```json
{
    "answer": "Millie fue defendida por fans tras...",
    "source_data": [{ "@type": "NewsArticle", "headline": "...", "url": "..." }]
}
```
7. Frontend muestra la respuesta.

## 6. Consideraciones de Seguridad y Despliegue
- Variables de Entorno: Las claves de API (OpenAI, Qdrant URL) se manejan mediante `.env` para no exponerlas en el código.
- CORS: Habilitado (`flask-cors`) para permitir peticiones si el frontend se alojara en otro dominio.
- Scripts Batch: Se incluyen `.bat` para facilitar la instalación y ejecución en entornos Windows.