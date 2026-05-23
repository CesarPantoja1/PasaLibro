from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Book
from app.books.forms import BookForm
from app.books.storage import upload_image, delete_image

books_bp = Blueprint('books', __name__)


@books_bp.route('/dashboard')
@login_required
def dashboard():
    """Listado principal de libros con filtros (HU-05)."""
    query = Book.query

    # Filtro por búsqueda de texto
    q = request.args.get('q', '').strip()
    if q:
        query = query.filter(
            db.or_(
                Book.titulo.ilike(f'%{q}%'),
                Book.autor.ilike(f'%{q}%')
            )
        )

    # Filtro por nivel de inglés
    nivel = request.args.get('nivel', '')
    if nivel:
        query = query.filter_by(nivel=nivel)

    # Filtro por rango de precio
    precio_min = request.args.get('precio_min', type=float)
    precio_max = request.args.get('precio_max', type=float)
    if precio_min is not None:
        query = query.filter(Book.precio >= precio_min)
    if precio_max is not None:
        query = query.filter(Book.precio <= precio_max)

    # Filtro por estado (disponible / vendido)
    estado = request.args.get('estado', '')
    if estado:
        query = query.filter_by(estado=estado)

    books = query.order_by(Book.created_at.desc()).all()
    niveles = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

    return render_template('books/dashboard.html', books=books, niveles=niveles)


@books_bp.route('/books/new', methods=['GET', 'POST'])
@login_required
def create():
    """Crear un nuevo libro (HU-04)."""
    form = BookForm()
    if form.validate_on_submit():
        imagen_url = None
        if form.imagen.data:
            try:
                imagen_url = upload_image(form.imagen.data)
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('books/crear.html', form=form)
            except Exception as e:
                flash('Error subiendo la imagen. Intenta de nuevo.', 'danger')
                return render_template('books/crear.html', form=form)

        book = Book(
            titulo=form.titulo.data.strip(),
            autor=form.autor.data.strip(),
            nivel=form.nivel.data,
            precio=form.precio.data,
            descripcion=form.descripcion.data.strip() if form.descripcion.data else None,
            imagen_url=imagen_url,
            user_id=current_user.id
        )
        db.session.add(book)
        db.session.commit()
        flash('¡Libro publicado exitosamente!', 'success')
        return redirect(url_for('books.detail', id=book.id))

    return render_template('books/crear.html', form=form)


@books_bp.route('/books/<int:id>')
@login_required
def detail(id):
    """Vista detallada de un libro (parte de HU-04, HU-07, HU-08)."""
    book = Book.query.get_or_404(id)
    return render_template('books/detalle.html', book=book)


@books_bp.route('/books/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar un libro existente — solo el dueño (HU-06)."""
    book = Book.query.get_or_404(id)

    if book.user_id != current_user.id:
        abort(403)

    form = BookForm(obj=book)

    if form.validate_on_submit():
        book.titulo = form.titulo.data.strip()
        book.autor = form.autor.data.strip()
        book.nivel = form.nivel.data
        book.precio = form.precio.data
        book.descripcion = form.descripcion.data.strip() if form.descripcion.data else None

        if form.imagen.data:
            try:
                if book.imagen_url:
                    delete_image(book.imagen_url)
                book.imagen_url = upload_image(form.imagen.data)
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('books/editar.html', form=form, book=book)
            except Exception:
                flash('Error subiendo la imagen. Intenta de nuevo.', 'danger')
                return render_template('books/editar.html', form=form, book=book)

        db.session.commit()
        flash('Libro actualizado correctamente.', 'success')
        return redirect(url_for('books.detail', id=book.id))

    return render_template('books/editar.html', form=form, book=book)


@books_bp.route('/books/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Eliminar un libro — solo el dueño (HU-07)."""
    book = Book.query.get_or_404(id)

    if book.user_id != current_user.id:
        abort(403)

    if book.imagen_url:
        delete_image(book.imagen_url)

    db.session.delete(book)
    db.session.commit()
    flash('Libro eliminado correctamente.', 'info')
    return redirect(url_for('books.my_books'))


@books_bp.route('/books/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(id):
    """Cambiar estado entre disponible y vendido — solo el dueño (HU-07)."""
    book = Book.query.get_or_404(id)

    if book.user_id != current_user.id:
        abort(403)

    book.estado = 'vendido' if book.estado == 'disponible' else 'disponible'
    db.session.commit()

    estado_msg = 'vendido' if book.estado == 'vendido' else 'disponible'
    flash(f'Libro marcado como {estado_msg}.', 'success')
    return redirect(url_for('books.detail', id=book.id))


@books_bp.route('/books/mis-libros')
@login_required
def my_books():
    """Listado de libros del usuario actual (HU-04 — ver mis publicaciones)."""
    books = Book.query.filter_by(user_id=current_user.id)\
                      .order_by(Book.created_at.desc()).all()
    return render_template('books/mis_libros.html', books=books)
