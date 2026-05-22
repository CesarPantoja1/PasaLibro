# PasaLibro

Plataforma web para la compra y venta de libros de inglés de segunda mano entre estudiantes. Permite publicar textos, buscar por nivel (A1–C2) y negociar directamente dentro de la plataforma mediante chat en tiempo real.

---

## Grupo OmniDevs

| Integrante | Módulo |
|---|---|
| Tumbaco Oscar | Autenticación + Base de datos |
| Pantoja César | CRUD de libros |
| Naranjo Juan | Chat WebSocket |
| Guachamin Emilia | Frontend + Presentación |

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Flask 3 (Python) |
| Plantillas | Jinja2 |
| ORM | SQLAlchemy + Flask-Migrate |
| Base de datos | PostgreSQL |
| WebSocket | Flask-SocketIO + Socket.IO |
| Formularios | Flask-WTF + WTForms |
| Autenticación | Flask-Login + Flask-Bcrypt |

---

## Estructura del proyecto

```
pasalibro/
├── app/
│   ├── __init__.py          # Application factory
│   ├── extensions.py        # Instancias: db, login_manager, bcrypt, socketio
│   ├── models.py            # Modelos: User, Book, ChatRoom, Message
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── forms.py         # RegisterForm, LoginForm, ForgotPasswordForm
│   │   └── routes.py        # /auth/register, /auth/login, /auth/logout
│   ├── books/
│   │   ├── __init__.py
│   │   ├── forms.py         # BookForm, SearchForm
│   │   └── routes.py        # CRUD completo de libros
│   ├── chat/
│   │   ├── __init__.py
│   │   ├── routes.py        # /chat/start/<book_id>, /chat/room/<room_id>
│   │   └── events.py        # Eventos SocketIO: join, send_message, leave
│   ├── static/
│   │   ├── css/main.css
│   │   └── js/main.js
│   └── templates/
│       ├── shared/base.html
│       ├── auth/            # login.html, register.html, forgot_password.html
│       ├── books/           # index.html, detail.html, form.html
│       └── chat/room.html
├── migrations/              # Generado por Flask-Migrate
├── tests/
├── config.py                # Configuración por entorno
├── run.py                   # Punto de entrada
├── requirements.txt
└── .env.example
```

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/OmniDevs/pasalibro.git
cd pasalibro
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus datos:

```
FLASK_ENV=development
SECRET_KEY=una-clave-secreta-segura
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/pasalibro
```

### 4. Crear la base de datos

```bash
# Crear la base en PostgreSQL primero
createdb pasalibro

# Aplicar migraciones
flask db init
flask db migrate -m "initial"
flask db upgrade
```

### 5. Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`.

---

## Pantallas implementadas

| Pantalla | Ruta | Descripción |
|---|---|---|
| Login | `/auth/login` | Inicio de sesión con email y contraseña |
| Registro | `/auth/register` | Creación de cuenta nueva |
| Recuperar clave | `/auth/forgot-password` | Reseteo de contraseña por email |
| Dashboard | `/books/` | Catálogo de libros con filtros |
| Publicar libro | `/books/new` | Formulario para nueva publicación |
| Detalle libro | `/books/<id>` | Vista del libro + botón de contacto |
| Editar libro | `/books/<id>/edit` | Actualizar publicación propia |
| Chat | `/chat/room/<id>` | Chat en tiempo real con WebSocket |

---

## Modelos de base de datos

```
users          → id, nombre, email, password_hash, created_at
books          → id, titulo, autor, nivel, precio, descripcion, estado, user_id
chat_rooms     → id, book_id, buyer_id, seller_id, created_at
messages       → id, contenido, room_id, sender_id, created_at
```

---

## Funcionalidades principales

- Registro y login con contraseña encriptada (bcrypt)
- CRUD completo de libros con filtros por nivel A1–C2 y precio
- Solo el dueño puede editar o marcar como vendido su libro
- Chat en tiempo real entre comprador y vendedor (Flask-SocketIO)
- Historial de mensajes persistido en PostgreSQL
- Validaciones en formularios (frontend + backend)
- Navegación protegida con `@login_required`

---

## Comandos útiles

```bash
# Crear nueva migración tras cambiar modelos
flask db migrate -m "descripcion del cambio"
flask db upgrade

# Abrir shell de Flask con contexto de app
flask shell

# Correr en modo producción con eventlet
gunicorn --worker-class eventlet -w 1 "app:create_app()"
```

---

## Contribución

Cada integrante trabaja en su rama y hace PR a `main`:

```bash
git checkout -b feature/nombre-funcionalidad
# ... commits ...
git push origin feature/nombre-funcionalidad
```

Todos los commits deben aparecer en el repositorio público para la evaluación.
