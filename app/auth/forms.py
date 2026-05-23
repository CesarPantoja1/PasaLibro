from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class RegisterForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(min=2, max=100)
    ])
    email = StringField('Correo electrónico', validators=[
        DataRequired(message='El email es obligatorio'),
        Email(message='Ingresa un email válido')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=6, message='Mínimo 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Crear cuenta')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Este email ya está registrado.')


class LoginForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar sesión')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[
        DataRequired(),
        Email()
    ])
    submit = SubmitField('Enviar instrucciones')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nueva contraseña', validators=[
        DataRequired(),
        Length(min=6, message='Mínimo 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Restablecer contraseña')