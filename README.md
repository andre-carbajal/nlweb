# 📰 NLWeb - Sitio de Noticias con Inteligencia Artificial
Este proyecto es una implementación de NLWeb para un sitio web de noticias ficticio (basado en un feed de BuzzFeed). Integra un sistema de Búsqueda Vectorial (RAG) y un Chatbot con IA que permite a los usuarios interactuar con el contenido de las noticias utilizando lenguaje natural.

## 🚀 Características
- Frontend Moderno:Interfaz limpia y responsiva para leer noticias.
- Chatbot Integrado: Widget flotante que responde preguntas sobre las noticias publicadas.
Búsqueda Vectorial (RAG): Utiliza Qdrant para buscar contexto relevante en las noticias y OpenAI (GPT-4o) para generar respuestas precisas.
- Estandarización de Datos: Convierte noticias XML a formato estructurado Schema.org.
- Scripts de Automatización: Archivos `.bat` para facilitar la instalación y ejecución en Windows.

## 🛠️ Requisitos Previos
Antes de comenzar, asegúrate de tener instalado:
- Python 3.12 o superior.
- UV (Gestor de paquetes de Python moderno) o pip.
- Una instancia de Qdrant (puede ser Qdrant Cloud o local con Docker).
- Una API Key de OpenAI.

## ⚙️ Configuración e Instalación
1. Clonar el repositorio
```bash
git clone https://github.com/andre-carbajal/nlweb.git
cd nlweb
```
2. Configurar Variables de EntornoCrea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
```
OPENAI_API_KEY=tu_api_key_de_openai_aqui
QDRANT_URL=tu_url_de_qdrant_aqui
```
(Si usas Qdrant Cloud, asegúrate de incluir la API Key en la URL o ajustar el código si es necesario).

3. Instalar Dependencias Puedes usar el script automático para Windows:
- Ejecuta `install_dependencies.bat` o hacerlo manualmente con uv:
```bash
uv add flask flask-cors qdrant-client openai python-dotenv requests xmltodict
```

## 📦 Carga de Datos (ETL)
Antes de usar el chat, necesitas procesar el feed de noticias y cargarlo en la base de datos vectorial.
1. Asegúrate de que el archivo `feed.xml` esté en la raíz.
2. Ejecuta el script de carga:
- Windows: Doble clic en `load_data.bat`.
- Manual:
```bash
uv run python cargar_datos.py
```
Esto leerá el XML, generará embeddings para cada noticia y las almacenará en la colección noticias-futuro en Qdrant.

## ▶️ Ejecución del Servidor
Para iniciar la aplicación web y el backend:
- Windows: Doble clic en `start_services.bat`.
- Manual:
```bash
uv run python server.py
```
El servidor se iniciará en `http://localhost:8000`. Abre esa dirección en tu navegador para ver el sitio web y probar el chatbot.

## 📂 Estructura del Proyecto
```
nlweb/
├── cargar_datos.py        # Script ETL: XML -> Qdrant
├── server.py              # Backend Flask (API RAG + Archivos estáticos)
├── feed.xml               # Fuente de datos (RSS Feed)
├── .env                   # Variables de entorno (no incluido en repo)
├── pyproject.toml         # Configuración de dependencias (UV)
│
├── frontend/              # Archivos del Sitio Web
│   ├── index.html         # Página principal
│   ├── style.css          # Estilos
│   └── app.js             # Lógica del cliente y chat
│
└── scripts                # Automatización para Windows
    ├── install_dependencies.bat
    ├── load_data.bat
    └── start_services.bat
```

## 🧠 Cómo funciona el Chatbot
1. El usuario envía una pregunta desde el widget en `index.html`.
2. `server.py` recibe la pregunta y crea un embedding (vector) usando OpenAI.
3. Busca en Qdrant las 3 noticias más similares semánticamente.
4. Construye un prompt con el contenido de esas noticias como contexto.
5. Envía el prompt a GPT-4o para generar una respuesta basada exclusivamente en las noticias encontradas.
6. Devuelve la respuesta al frontend junto con los datos estructurados (Schema.org) de las fuentes.

## 📄 Licencia
Este proyecto es para fines educativos y de demostración.