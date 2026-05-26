# app/chat/routes.py
from flask import Blueprint, current_app, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from app.models import ChatRoom, Message, Book, db

chat_bp = Blueprint('chat', __name__, template_folder='templates')

# Ruta para abrir la sala de chat entre comprador y vendedor para un libro específico
@chat_bp.route('/chat/book/<int:book_id>/vendedor/<int:seller_id>')
@login_required
def abrir_chat(book_id, seller_id):
    buyer_id = current_user.id
    room = None

    if current_user.id == seller_id:
        # El vendedor abre una sala existente desde su bandeja.
        room = ChatRoom.query.filter_by(
            book_id=book_id,
            seller_id=seller_id
        ).order_by(ChatRoom.created_at.desc()).first()

        if not room:
            flash('No se encontro una conversacion activa para este libro.', 'warning')
            return redirect(url_for('chat.bandeja'))
    else:
        # Buscamos si ya existe una sala de chat para este libro entre este comprador y vendedor
        room = ChatRoom.query.filter_by(
            book_id=book_id,
            buyer_id=buyer_id,
            seller_id=seller_id
        ).first()

        # Si no existe la sala de chat, la creamos
        if not room:
            room = ChatRoom(book_id=book_id, buyer_id=buyer_id, seller_id=seller_id)
            db.session.add(room)
            db.session.commit()
    
    # Obtenemos el historial de mensajes para mostrar en la sala de chat (ordenados del mas viejo al mas nuevo)    
    historial_mensajes = room.messages.order_by(Message.created_at.asc()).all()
    libro = Book.query.get_or_404(book_id)
    
    #Mandamos a la plantilla la sala de chat, el historial de mensajes y los datos del libro
    return render_template('chat/room.html', room=room, mensajes=historial_mensajes, libro=libro)

@chat_bp.route('/chat/bandeja', endpoint='bandeja')
@login_required
def bandeja_entrada():
    try:
        # Precargamos libro, vendedor y comprador para evitar consultas perezosas en la vista.
        opciones_chat = (
            joinedload(ChatRoom.book).joinedload(Book.owner),
            joinedload(ChatRoom.buyer)
        )

        # Chats iniciados por libros que el usuario quiere comprar.
        compras = ChatRoom.query.options(*opciones_chat).filter(
            ChatRoom.buyer_id == current_user.id
        ).order_by(ChatRoom.created_at.desc()).all()

        # Chats recibidos por libros publicados por el usuario.
        ventas = ChatRoom.query.options(*opciones_chat).filter(
            ChatRoom.seller_id == current_user.id
        ).order_by(ChatRoom.created_at.desc()).all()
    except Exception:
        current_app.logger.exception('Error al cargar la bandeja de entrada')
        flash('No se pudieron cargar tus mensajes. Intentalo nuevamente.', 'error')
        compras = []
        ventas = []

    return render_template("chat/inbox.html", compras=compras, ventas=ventas)

# Importamos los eventos de SocketIO al final para evitar importaciones circulares
from app.chat import events
