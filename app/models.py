from datetime import datetime
from app.extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    books = db.relationship('Book', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='sender', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'


class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(150), nullable=False)
    nivel = db.Column(db.String(10), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(50), default='disponible')
    imagen_url = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chat_rooms = db.relationship('ChatRoom', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Book {self.titulo}>'


class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    messages = db.relationship('Message', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChatRoom {self.id}>'


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.id}>'