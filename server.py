from flask import Flask, request, jsonify, Response, send_from_directory, send_file
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests

load_dotenv()
app = Flask(__name__)
CORS(app)

client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
QDRANT_HOST = os.getenv("QDRANT_URL")
COLLECTION_NAME = "noticias-futuro"

# --- RUTAS DE ESTÁNDAR NLWEB ---
@app.route('/.well-known/ai-plugin.json')
def serve_manifest():
    return send_from_directory('.well-known', 'ai-plugin.json')

@app.route('/openapi.yaml')
def serve_openapi():
    return send_file('openapi.yaml')

# --- RUTA PARA SERVIR EL FRONTEND ---
@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)


# --- RUTA DE DATOS VISUALES ---
@app.route('/feed.xml')
def serve_feed():
    path = os.path.join(os.path.dirname(__file__), 'feed.xml')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='application/xml')
    return jsonify({"error": "No feed found"}), 404

# --- RUTA PRINCIPAL DE BÚSQUEDA (GET) ---
@app.route('/search', methods=['GET'])
def search_news():
    # 1. Leer parámetro de la URL (?q=...)
    query = request.args.get('q')
    
    if not query:
        return jsonify({"error": "Falta el parámetro 'q'"}), 400

    try:
        # 2. Vectorizar
        emb = client_openai.embeddings.create(input=[query], model="text-embedding-ada-002").data[0].embedding

        # 3. Buscar en Qdrant (HTTP directo)
        search_url = f"{QDRANT_HOST}/collections/{COLLECTION_NAME}/points/search"
        payload = { "vector": emb, "limit": 3, "with_payload": True }
        
        qdrant_res = requests.post(search_url, json=payload).json()
        results = qdrant_res.get('result', [])

        # 4. Construir Contexto
        context_text = ""
        source_schemas = []
        
        for hit in results:
            data = hit.get('payload', {})
            # Extraemos el Schema puro para devolverlo también
            if 'schema' in data:
                source_schemas.append(data['schema'])
            
            # Texto para el prompt
            context_text += f"- {data.get('text', '')}\n\n"

        # 5. Generar Respuesta GPT
        prompt = f"Contexto:\n{context_text}\n\nPregunta: {query}\n\nResponde usando el contexto."
        gpt_res = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        # 6. Devolver respuesta enriquecida
        return jsonify({
            "answer": gpt_res.choices[0].message.content,
            "source_data": source_schemas # ¡Entregamos los datos estructurados!
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Servidor NLWeb Oficial corriendo en http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)