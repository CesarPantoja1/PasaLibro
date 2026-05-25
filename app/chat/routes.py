# app/chat/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import ChatRoom, Message, Book, db

chat_bp = Blueprint('chat', __name__, template_folder='templates')

# Ruta para abrir la sala de chat entre comprador y vendedor para un libro específico
@chat_bp.route('/chat/book/<int:book_id>/vendedor/<int:seller_id>')
@login_required
def abrir_chat(book_id, seller_id):
    buyer_id = current_user.id
    
    # Evitamos que el usuario inicie un chat consigo mismo
    if buyer_id == seller_id:
        flash('No puedes iniciar un chat contigo mismo.', 'warning')
        return redirect(url_for('main.index'))
    
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

# Importamos los eventos de SocketIO al final para evitar importaciones circulares
from app.chat import events