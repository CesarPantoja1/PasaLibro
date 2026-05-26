# app/chat/events.py
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app.extensions import socketio, db
from app.models import Message, ChatRoom, quito_now

# Este módulo maneja los eventos de WebSocket relacionados con el chat entre compradores y vendedores.
@socketio.on('join')
def handle_join(data):
    room_id = data.get('room_id')
    if not room_id:
        return

    #Validamos que la sala exista y que el usuario pertenezca a ella
    room = ChatRoom.query.get(int(room_id))
    if not room or (current_user.id != room.buyer_id and current_user.id != room.seller_id):
        print(f"[WebSocket SEGURIDAD] Intento de acceso no autorizado a la sala {room_id}")
        return  # Si no pertenece a la sala, lo bloqueamos silenciosamente

    join_room(str(room_id))
    print(f"[WebSocket] Usuario {current_user.nombre} unido de forma segura a la sala: {room_id}")

@socketio.on('send_message')
def handle_send_message(data):
    # Escucha cuando un estudiante envía un mensaje de texto. Donde lo procesa, lo guarda en PostgreSQL (Supabase) y lo difunde en la sala.
    if not current_user.is_authenticated:
        return

    room_id = int(data.get('room_id'))
    sender_id = current_user.id
    contenido = data.get('contenido', '').strip()

    room = ChatRoom.query.get(room_id)
    if not room or (sender_id != room.buyer_id and sender_id != room.seller_id):
        print(f"[WebSocket SEGURIDAD] Intento de envío no autorizado a la sala {room_id}")
        return
    
    # Validación básica para evitar mensajes vacíos o solo con espacios
    if not contenido:
        return 

    # Ajuste de zona horaria: guardar y emitir la hora local de Quito, Ecuador.
    fecha_quito = quito_now()
    
    # Guardar en la base de datos de Supabase
    nuevo_mensaje = Message(
        room_id=room_id,
        sender_id=sender_id,
        contenido=contenido,
        created_at=fecha_quito
    )
    
    db.session.add(nuevo_mensaje)
    db.session.commit()  # Guardado físico en Postgres con SQLAlchemy ORM
    
    # Armar el paquete de datos (Payload) para el Frontend
    payload = {
        'id': nuevo_mensaje.id,
        'room_id': room_id,
        'sender_id': sender_id,
        'contenido': contenido,
        'time': fecha_quito.strftime("%H:%M"),
        'created_at': fecha_quito.strftime("%H:%M") #Hora en formato militar (HH:MM)
    }
    
    # Broadcast selectivo
    # Emitimos el evento 'receive_message' ÚNICAMENTE a los dispositivos dentro de esa 'room'
    emit('receive_message', payload, room=str(room_id), include_self=True)


@socketio.on('leave')
def handle_leave(data):
    # Escucha cuando el estudiante cierra la pestaña del chat o regresa al catálogo y lo desconecta de la sala.
    room_id = str(data.get('room_id'))
    if room_id:
        leave_room(room_id)
        print(f"[WebSocket] Estudiante desconectado de la sala: {room_id}")
