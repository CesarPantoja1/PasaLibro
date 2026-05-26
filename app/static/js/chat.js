// app/static/js/chat.js
document.addEventListener("DOMContentLoaded", () => {
    // 1. Extraer los datos de configuración inyectados por Flask de forma segura
    const configCard = document.getElementById("chat-config");
    const chatBox = document.getElementById("chat-box");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");

    if (!configCard || !chatBox || !chatForm || !chatInput) {
        return;
    }

    const roomId = configCard.dataset.roomId;
    const currentUserId = Number(configCard.dataset.senderId);

    // Función auxiliar para mantener la ventana del chat fija abajo en el último mensaje
    const scrollToBottom = () => {
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // Auto-scroll inicial al cargar el historial histórico
    scrollToBottom();

    // 2. Establecer el túnel persistente bidireccional con el servidor de Flask
    const socket = io();

    // Notificar al servidor el ingreso al cuarto virtual privado
    socket.emit('join', { room_id: roomId });

    // 3. Capturar el envío del formulario (Estudiante escribe un mensaje)
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault(); // Previene la recarga HTTP del navegador

        const contenido = chatInput.value.trim();
        if (!contenido) return;

        // Mandar el paquete JSON estructurado por la tubería hacia events.py
        socket.emit('send_message', {
            room_id: roomId,
            sender_id: currentUserId,
            contenido: contenido
        });

        chatInput.value = ""; // Limpiar la caja de texto
    });

    // 4. Escuchar las transmisiones en vivo del servidor ('events.py')
    socket.on('receive_message', (data) => {
        // Validar si el mensaje pertenece a la sala actual (Seguridad por diseño)
        if (!data) return;
        if (String(data.room_id) !== String(roomId)) return;

        // Determinar dinámicamente si el mensaje es propio o del otro usuario
        const isSent = Number(data.sender_id) === currentUserId;
        const messageClass = isSent ? "sent" : "received";

        // Crear nodos seguros para evitar XSS
        const msgDiv = document.createElement("div");
        msgDiv.className = `chat-message ${messageClass}`;
        msgDiv.textContent = data.contenido || "";

        const timeSmall = document.createElement("small");
        timeSmall.textContent = data.created_at || "";
        msgDiv.appendChild(timeSmall);

        chatBox.appendChild(msgDiv);
        scrollToBottom(); // Desplazar hacia abajo para ver el mensaje nuevo
    });

    // Notificar la salida si el usuario decide cerrar o cambiar de página de forma controlada
    window.addEventListener("beforeunload", () => {
        socket.emit('leave', { room_id: roomId });
    });
});
