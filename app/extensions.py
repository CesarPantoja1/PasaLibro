from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
csrf = CSRFProtect()
socketio = SocketIO(cors_allowed_origins="*") # El CORS evita bloqueos locales de seguridad