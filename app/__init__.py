from flask import Flask, render_template
from config import Config
from app.extensions import db, migrate, login_manager, bcrypt, socketio, mail

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)
    
    # Configurar LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder.'
    login_manager.login_message_category = 'warning'
    
    # Cargar usuario
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    # Blueprint temporal para que no dé 404 al redirigir
    @app.route('/')
    def main_index():
        return render_template('shared/base.html')
      
    return app