from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

NIVELES = [
    ('', 'Selecciona el nivel'),
    ('A1', 'A1 - Principiante'),
    ('A2', 'A2 - Elemental'),
    ('B1', 'B1 - Intermedio'),
    ('B2', 'B2 - Intermedio Alto'),
    ('C1', 'C1 - Avanzado'),
    ('C2', 'C2 - Maestría'),
]


class BookForm(FlaskForm):
    titulo = StringField('Título del libro', validators=[
        DataRequired(message='El título es obligatorio'),
        Length(min=2, max=200, message='El título debe tener entre 2 y 200 caracteres')
    ])
    autor = StringField('Autor', validators=[
        DataRequired(message='El autor es obligatorio'),
        Length(min=2, max=150, message='El autor debe tener entre 2 y 150 caracteres')
    ])
    nivel = SelectField('Nivel de inglés', choices=NIVELES, validators=[
        DataRequired(message='Selecciona un nivel')
    ])
    precio = DecimalField('Precio ($)', validators=[
        DataRequired(message='El precio es obligatorio'),
        NumberRange(min=0.01, max=999.99, message='El precio debe estar entre $0.01 y $999.99')
    ], places=2)
    descripcion = TextAreaField('Descripción', validators=[
        Optional(),
        Length(max=1000, message='Máximo 1000 caracteres')
    ])
    imagen = FileField('Imagen del libro', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'gif'],
                     'Solo se permiten imágenes (JPG, PNG, WEBP, GIF)')
    ])
    submit = SubmitField('Publicar libro')
