"""
Módulo de almacenamiento de imágenes con Supabase Storage.
Sube imágenes de portada de libros a Supabase Storage y retorna la URL pública.
Si Supabase no está configurado, guarda localmente como fallback.
"""

import os
import uuid
import requests
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_image(file):
    """
    Sube una imagen a Supabase Storage y retorna la URL pública.
    Si Supabase no está configurado, guarda localmente.
    
    Args:
        file: FileStorage object de Flask
    
    Returns:
        str: URL pública de la imagen subida, o None si no hay archivo
    
    Raises:
        ValueError: Si el tipo de archivo no es permitido o excede el tamaño
    """
    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        raise ValueError('Tipo de archivo no permitido. Usa: JPG, PNG, WEBP o GIF')

    # Verificar tamaño
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValueError('La imagen no debe superar 5 MB')

    supabase_url = current_app.config.get('SUPABASE_URL')
    supabase_key = current_app.config.get('SUPABASE_KEY')
    bucket = current_app.config.get('SUPABASE_BUCKET', 'book-covers')

    if not supabase_url or not supabase_key:
        return _save_locally(file)

    # Generar nombre único
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    # Subir a Supabase Storage
    headers = {
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': file.content_type or 'image/jpeg',
        'Cache-Control': 'max-age=3600',
    }

    url = f"{supabase_url}/storage/v1/object/{bucket}/{filename}"

    try:
        response = requests.post(url, headers=headers, data=file.read())
        if response.status_code in (200, 201):
            return f"{supabase_url}/storage/v1/object/public/{bucket}/{filename}"
        else:
            current_app.logger.error(f"Supabase Storage error: {response.status_code} - {response.text}")
            raise Exception(f'Error subiendo imagen a Supabase: {response.status_code}')
    except requests.exceptions.ConnectionError:
        current_app.logger.error("No se pudo conectar a Supabase Storage")
        raise Exception('No se pudo conectar al servicio de almacenamiento')


def delete_image(image_url):
    """
    Elimina una imagen de Supabase Storage.
    
    Args:
        image_url: URL pública de la imagen a eliminar
    """
    if not image_url:
        return

    supabase_url = current_app.config.get('SUPABASE_URL')
    supabase_key = current_app.config.get('SUPABASE_KEY')
    bucket = current_app.config.get('SUPABASE_BUCKET', 'book-covers')

    if not supabase_url or not supabase_key:
        _delete_locally(image_url)
        return

    # Extraer el nombre del archivo de la URL pública
    prefix = f"{supabase_url}/storage/v1/object/public/{bucket}/"
    if not image_url.startswith(prefix):
        return

    filename = image_url[len(prefix):]

    headers = {
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json',
    }

    url = f"{supabase_url}/storage/v1/object/{bucket}"

    try:
        response = requests.delete(url, headers=headers, json={"prefixes": [filename]})
        if response.status_code not in (200, 204):
            current_app.logger.warning(f"No se pudo eliminar imagen: {response.text}")
    except Exception as e:
        current_app.logger.warning(f"Error eliminando imagen de Supabase: {e}")


def _save_locally(file):
    """Fallback: guarda la imagen en static/uploads/ localmente."""
    upload_dir = os.path.join(current_app.static_folder, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    file.save(filepath)
    return f"/static/uploads/{filename}"


def _delete_locally(image_url):
    """Elimina una imagen guardada localmente."""
    if image_url and image_url.startswith('/static/uploads/'):
        filepath = os.path.join(current_app.static_folder, 'uploads',
                                image_url.replace('/static/uploads/', ''))
        if os.path.exists(filepath):
            os.remove(filepath)
