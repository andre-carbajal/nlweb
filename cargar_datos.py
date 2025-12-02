import os
import asyncio
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI

load_dotenv()

# Configuración
XML_FILE = "feed.xml"
COLLECTION_NAME = "noticias-futuro"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL)

def get_embedding(text):
    text = text.replace("\n", " ")
    return openai_client.embeddings.create(input=[text], model="text-embedding-ada-002").data[0].embedding

async def main():
    print(f"📦 Leyendo {XML_FILE}...")
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    items = root.findall('.//item')
    
    print(f"💾 Reiniciando Base de Datos Qdrant...")
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )

    print(f"🧠 Estandarizando {len(items)} noticias a Schema.org...")
    points = []
    
    for idx, item in enumerate(items):
        title = item.find('title').text or "Sin título"
        desc = item.find('description').text or ""
        link = item.find('link').text or ""
        pub_date = item.find('pubDate').text or ""
        
        # --- ESTO ES LO NUEVO: Objeto Schema.org ---
        schema_obj = {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": title,
            "description": desc,
            "url": link,
            "datePublished": pub_date,
            "author": { "@type": "Organization", "name": "BuzzFeed" }
        }
        # -------------------------------------------

        # Texto para búsqueda vectorial (el humano busca por significado)
        full_text = f"{title}. {desc}"
        
        try:
            vector = get_embedding(full_text)
            points.append(PointStruct(
                id=idx,
                vector=vector,
                payload={
                    "text": full_text,     # Para buscar
                    "schema": schema_obj   # Para entregar al Agente (Dato puro)
                }
            ))
            print(f"   - Procesado: {title[:30]}...")
        except Exception as e:
            print(f"   ⚠️ Error en noticia {idx}: {e}")

    if points:
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"\n✅ ¡ÉXITO! Datos cargados con formato Schema.org.")

if __name__ == "__main__":
    asyncio.run(main())