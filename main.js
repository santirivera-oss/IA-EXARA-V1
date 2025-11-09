const chatHistory = document.getElementById("chatHistory");

// Cargar historial de localStorage al inicio
window.addEventListener("load", () => {
    const historial = JSON.parse(localStorage.getItem("historialMinero") || "[]");
    historial.forEach(item => {
        agregarMensaje(item.tipo, formatearRespuestaIA(item.texto));
    });
    chatHistory.scrollTop = chatHistory.scrollHeight;
});

async function enviarPregunta() {
    const preguntaInput = document.getElementById("pregunta");
    const pregunta = preguntaInput.value.trim();
    if (!pregunta) return;

    agregarMensaje("user", pregunta);
    guardarHistorial("user", pregunta);
    preguntaInput.value = "";

    const loaderDiv = agregarMensaje("bot", "<span class='loader-bounce'>⛏️ Procesando...</span>", true);

    try {
        const res = await fetch("https://ia-exara-backend.onrender.com", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: pregunta })
        });
        const data = await res.json();
        const respuestaNatural = humanizarRespuestaNatural(data.answer);

        await escribirMensajeFluido(loaderDiv, formatearRespuestaIA(respuestaNatural));
        guardarHistorial("bot", respuestaNatural);

        agregarBotonCopiar(loaderDiv);

    } catch (err) {
        actualizarMensaje(loaderDiv, "❌ Error al conectar con el backend.");
        console.error(err);
    }

    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Humanización estilo ChatGPT
function humanizarRespuestaNatural(texto) {
    // Limpiamos exceso de saltos y espacios
    texto = texto.trim().replace(/\n{3,}/g, "\n\n");

    // Añadimos saludos y cierres naturales si no hay ya
    if (!/^(hola|hey|buenas)/i.test(texto)) {
        texto = "¡Hola! 👋\n\n" + texto;
    }
    if (!/(\?|!|\.|\n)$/.test(texto)) {
        texto += " 🙂";
    }

    // Emojis contextuales muy sutiles
    const reemplazos = [
        { regex: /\b(correcto|exacto|perfecto|bien)\b/gi, emoji: " ✅" },
        { regex: /\b(peligro|riesgo|cuidado)\b/gi, emoji: " ⚠️" },
        { regex: /\b(gracias|agradecido)\b/gi, emoji: " 🙏" },
        { regex: /\b(genial|excelente|bueno)\b/gi, emoji: " ✨" }
    ];
    reemplazos.forEach(r => {
        texto = texto.replace(r.regex, match => match + r.emoji);
    });

    // Frases de cierre sutiles
    if (!/\b(¡hasta luego|nos vemos|espero haberte ayudado)/i.test(texto)) {
        texto += "\n\nEspero que esto te ayude 👍";
    }

    return texto;
}

// Agregar mensaje
function agregarMensaje(tipo, html, esLoader = false) {
    const div = document.createElement("div");
    div.classList.add(
        "p-4", "rounded-lg", "max-w-[80%]", "break-words",
        "transition-all", "duration-300", "flex", "flex-col",
        "gap-2", "relative", "fade-slide-in"
    );

    if (tipo === "user") div.classList.add("self-end");
    else div.classList.add("self-start");

    if (esLoader) div.querySelector('span')?.classList.add('loader-bounce');

    div.innerHTML = html;
    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return div;
}

// Actualizar mensaje
function actualizarMensaje(div, nuevoTexto) {
    div.classList.remove("animate-bounce");
    div.innerHTML = nuevoTexto;
}

// Formatear Markdown simple
function formatearRespuestaIA(texto) {
    const parrafos = texto.split("\n\n");
    return parrafos.map(p => {
        let formateado = p
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/^\d+\.\s+(.*)/gm, "<li>$1</li>")
            .replace(/^\* (.*)/gm, "<li>$1</li>");
        return `<p class="mb-2">${formateado}</p>`;
    }).join("");
}

// Escribir mensaje palabra por palabra
async function escribirMensajeFluido(div, html, velocidad = 20, palabrasPorBloque = 3) {
    div.innerHTML = "";
    const temp = document.createElement("div");
    temp.innerHTML = html;

    async function escribirNodo(nodo, contenedor) {
        if (nodo.nodeType === Node.TEXT_NODE) {
            const palabras = nodo.textContent.split(/(\s+)/);
            let buffer = "";
            let contador = 0;
            for (const palabra of palabras) {
                buffer += palabra;
                contador++;
                if (contador >= palabrasPorBloque || palabra.includes("\n")) {
                    contenedor.appendChild(document.createTextNode(buffer));
                    buffer = "";
                    contador = 0;
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                    if (/[.,!?]/.test(palabra.trim())) await new Promise(r => setTimeout(r, 80 + Math.random() * 100));
                    else await new Promise(r => setTimeout(r, velocidad * palabrasPorBloque));
                }
            }
            if (buffer) contenedor.appendChild(document.createTextNode(buffer));
        } else if (nodo.nodeType === Node.ELEMENT_NODE) {
            const nuevoNodo = nodo.cloneNode(false);
            contenedor.appendChild(nuevoNodo);
            for (const hijo of Array.from(nodo.childNodes)) {
                await escribirNodo(hijo, nuevoNodo);
            }
        }
    }

    for (const nodo of Array.from(temp.childNodes)) {
        await escribirNodo(nodo, div);
    }
}

// Botón copiar
function agregarBotonCopiar(div) {
    const button = document.createElement("button");
    button.innerText = "📋";
    button.classList.add("ml-2", "text-sm", "text-gray-100", "hover:text-yellow-400", "self-end");
    button.onclick = () => {
        navigator.clipboard.writeText(div.innerText).then(() => {
            button.innerText = "✅";
            setTimeout(() => (button.innerText = "📋"), 1000);
        });
    };
    div.appendChild(button);
}

// Historial persistente
function guardarHistorial(tipo, texto) {
    const historial = JSON.parse(localStorage.getItem("historialMinero") || "[]");
    historial.push({ tipo, texto });
    localStorage.setItem("historialMinero", JSON.stringify(historial));
}

// Limpiar historial
function limpiarHistorial() {
    localStorage.removeItem("historialMinero");
    chatHistory.innerHTML = "";
}
