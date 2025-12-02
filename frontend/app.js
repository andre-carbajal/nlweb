// --- CONFIGURACIÓN DE SERVIDORES ---
// Usamos rutas relativas para que funcione en cualquier host/IP
const DATA_SERVER = '/feed.xml';
const BRAIN_SERVER = '/search';

// --- 1. LÓGICA DE CARGA DE NOTICIAS (FEED) ---
async function loadNews() {
    const container = document.getElementById('news-container');

    try {
        // Petición al servidor para obtener el XML
        const response = await fetch(DATA_SERVER);

        if (!response.ok) throw new Error("No se pudo descargar el feed XML");

        const text = await response.text();
        const parser = new DOMParser();
        const xml = parser.parseFromString(text, "text/xml");
        const items = xml.querySelectorAll("item");

        // Limpiamos el contenedor
        container.innerHTML = '';

        if (items.length === 0) {
            container.innerHTML = '<p>No hay noticias para mostrar.</p>';
            return;
        }

        // Renderizamos cada noticia
        items.forEach(item => {
            const title = item.querySelector("title")?.textContent || "Sin título";
            const descRaw = item.querySelector("description")?.textContent || "";

            // Truco para limpiar el HTML que viene dentro de la descripción
            const tempDiv = document.createElement("div");
            tempDiv.innerHTML = descRaw;
            const desc = tempDiv.textContent || tempDiv.innerText || "";

            // Lógica para encontrar la imagen (BuzzFeed es tramposo con esto)
            let imgUrl = "https://placehold.co/600x400?text=News"; // Imagen por defecto

            // Intento 1: Etiqueta media:thumbnail
            const media = item.querySelector("media\\:thumbnail, thumbnail");
            if (media && media.getAttribute("url")) {
                imgUrl = media.getAttribute("url");
            }

            // Intento 2: Buscar <img> dentro de la descripción
            const imgInDesc = tempDiv.querySelector("img");
            if (imgInDesc) {
                imgUrl = imgInDesc.src;
            }

            // Extraer el link original
            const link = item.querySelector("link")?.textContent || "#";

            // Crear la tarjeta HTML
            const card = `
                <div class="news-card">
                    <img src="${imgUrl}" class="news-img" alt="Imagen noticia">
                    <div class="news-content">
                        <span class="news-tag">Tendencia</span>
                        <h3 class="news-title"><a href="${link}" target="_blank" style="text-decoration: none; color: inherit;">${title}</a></h3>
                        <p class="news-desc">${desc}</p>
                        <a href="${link}" target="_blank" style="display: inline-block; margin-top: 10px; color: #007bff; text-decoration: none; font-weight: bold;">Leer más &rarr;</a>
                    </div>
                </div>
            `;
            container.innerHTML += card;
        });

    } catch (error) {
        console.error("Error cargando noticias:", error);
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; color: red; background: #fff0f0; padding: 20px; border-radius: 8px;">
                <h3>⚠️ Error de Conexión</h3>
                <p>No puedo leer las noticias desde <b>${DATA_SERVER}</b>.</p>
                <p>Asegúrate de ejecutar <code>python server.py</code> en la terminal.</p>
            </div>
        `;
    }
}

// --- 2. LÓGICA DEL CHATBOT (Compatible con NLWeb Oficial) ---

function toggleChat() {
    document.getElementById('chat-widget').classList.toggle('active');
}

function handleEnter(e) {
    if (e.key === 'Enter') sendMessage();
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const loading = document.getElementById('loading');
    const txt = input.value.trim();

    if (!txt) return;

    // 1. Mostrar mensaje del usuario en el chat
    chatBox.innerHTML += `<div class="msg msg-user">${txt}</div>`;
    input.value = '';

    // Scroll automático hacia abajo
    chatBox.scrollTop = chatBox.scrollHeight;
    loading.style.display = 'block';

    try {
        // --- CAMBIO IMPORTANTE: Usamos GET para seguir el estándar NLWeb ---
        // Codificamos el texto para que sea seguro en la URL
        const queryParam = encodeURIComponent(txt);
        const url = `${BRAIN_SERVER}?q=${queryParam}`;

        const res = await fetch(url, {
            method: 'GET', // Método estándar para búsqueda
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!res.ok) throw new Error("Error en la respuesta del servidor");

        const data = await res.json();

        // Obtenemos la respuesta. Si viene vacía, ponemos un mensaje de error.
        let botReply = data.answer || "Lo siento, hubo un error procesando tu respuesta.";

        // --- NUEVO: Agregar fuentes si existen ---
        if (data.source_data && Array.isArray(data.source_data) && data.source_data.length > 0) {
            botReply += '<div class="sources-section" style="margin-top: 10px; font-size: 0.9em; border-top: 1px solid #eee; padding-top: 5px;">';
            botReply += '<strong>Fuentes:</strong><ul style="margin: 5px 0; padding-left: 20px;">';

            data.source_data.forEach(source => {
                const url = source.url || "#";
                const headline = source.headline || "Noticia original";
                botReply += `<li><a href="${url}" target="_blank" style="color: #007bff; text-decoration: none;">${headline}</a></li>`;
            });

            botReply += '</ul></div>';
        }

        // 2. Mostrar respuesta del bot
        chatBox.innerHTML += `<div class="msg msg-bot">${botReply}</div>`;

    } catch (err) {
        console.error(err);
        chatBox.innerHTML += `
            <div class="msg msg-bot" style="background:#ffddd0; color: #d32f2f;">
                ❌ Error: No puedo conectar con el cerebro (Puerto 8000).
            </div>
        `;
    }

    // Limpieza final
    loading.style.display = 'none';
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Iniciar la carga de noticias al abrir la página
loadNews();