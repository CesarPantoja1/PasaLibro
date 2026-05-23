from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
from app.extensions import db, bcrypt, mail
from app.models import User
from app.auth.forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from flask_mail import Message

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def send_reset_email(user, token):
    reset_url = url_for('auth.restablecer_password', token=token, _external=True)
    subject = 'Recuperación de contraseña - PasaLibro'
    body = f'''Hola {user.nombre},

Para restablecer tu contraseña, haz clic aquí:
{reset_url}

Si no solicitaste esto, ignora este mensaje.
'''
    # Si hay servidor SMTP configurado, envía email. Si no, imprime en consola.
    if current_app.config.get('MAIL_SERVER'):
        msg = Message(subject, recipients=[user.email], body=body)
        try:
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False
    else:
        print(f"\n{'='*60}")
        print("RECUPERACIÓN DE CONTRASEÑA (modo desarrollo - sin SMTP)")
        print(f"{'='*60}")
        print(f"Usuario: {user.email}")
        print(f"Link:   {reset_url}")
        print(f"{'='*60}\n")
        return True


@auth_bp.route('/registro', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            nombre=form.nombre.data.strip(),
            email=form.email.data.lower().strip(),
            password_hash=hashed
        )
        db.session.add(user)
        db.session.commit()
        flash('¡Cuenta creada! Ahora inicia sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/registro.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'¡Bienvenido, {user.nombre}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main_index'))
        else:
            flash('Email o contraseña incorrectos.', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/password_olvidado', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main_index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user:
            serializer = get_serializer()
            token = serializer.dumps(user.email, salt='password-reset')
            send_reset_email(user, token)
        # Mensaje genérico por seguridad (no revelar si existe el email)
        flash('Si el email está registrado, recibirás instrucciones.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/password_olvidado.html', form=form)


@auth_bp.route('/restablecer-password/<token>', methods=['GET', 'POST'])
def restablecer_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main_index'))
    
    serializer = get_serializer()
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except Exception:
        flash('El link es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.password_olvidado'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('auth.password_olvidado'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Contraseña actualizada. Inicia sesión ahora.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/restablecer_password.html', form=form)