/**
 * PasaLibro — Books Module JavaScript
 * Validación de formularios, preview de imágenes, confirmaciones y filtros.
 */

document.addEventListener('DOMContentLoaded', () => {
    initImageUpload();
    initFormValidation();
    initDeleteConfirmation();
    initCharCounter();
    initFilterAnimations();
});


/* ======================================================
   IMAGE UPLOAD — Preview + Drag & Drop
   ====================================================== */
function initImageUpload() {
    const uploadZone = document.querySelector('.book-upload-zone');
    const fileInput = document.getElementById('imagen');
    const preview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    const previewName = document.getElementById('preview-name');
    const previewSize = document.getElementById('preview-size');
    const removeBtn = document.getElementById('remove-image');

    if (!uploadZone || !fileInput) return;

    // Click en la zona abre el selector de archivos
    uploadZone.addEventListener('click', (e) => {
        if (e.target !== removeBtn && !removeBtn?.contains(e.target)) {
            fileInput.click();
        }
    });

    // Drag & Drop
    ['dragenter', 'dragover'].forEach(event => {
        uploadZone.addEventListener(event, (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(event => {
        uploadZone.addEventListener(event, (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
        });
    });

    uploadZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect(files[0]);
        }
    });

    // Cuando se selecciona un archivo
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Botón para remover imagen
    if (removeBtn) {
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.value = '';
            if (preview) preview.style.display = 'none';
            uploadZone.classList.remove('has-file');
        });
    }

    function handleFileSelect(file) {
        // Validar tipo
        const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
        if (!allowedTypes.includes(file.type)) {
            showToast('Solo se permiten imágenes JPG, PNG, WEBP o GIF', 'danger');
            fileInput.value = '';
            return;
        }

        // Validar tamaño (5MB)
        if (file.size > 5 * 1024 * 1024) {
            showToast('La imagen no debe superar 5 MB', 'danger');
            fileInput.value = '';
            return;
        }

        // Mostrar preview
        const reader = new FileReader();
        reader.onload = (e) => {
            if (previewImg) previewImg.src = e.target.result;
            if (previewName) previewName.textContent = file.name;
            if (previewSize) previewSize.textContent = formatFileSize(file.size);
            if (preview) {
                preview.style.display = 'flex';
                preview.classList.add('preview-enter');
                setTimeout(() => preview.classList.remove('preview-enter'), 300);
            }
            uploadZone.classList.add('has-file');
        };
        reader.readAsDataURL(file);
    }
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}


/* ======================================================
   FORM VALIDATION — Validación en tiempo real
   ====================================================== */
function initFormValidation() {
    const form = document.getElementById('book-form');
    if (!form) return;

    const validators = {
        titulo: (value) => {
            if (!value.trim()) return 'El título es obligatorio';
            if (value.trim().length < 2) return 'Mínimo 2 caracteres';
            if (value.trim().length > 200) return 'Máximo 200 caracteres';
            return null;
        },
        autor: (value) => {
            if (!value.trim()) return 'El autor es obligatorio';
            if (value.trim().length < 2) return 'Mínimo 2 caracteres';
            if (value.trim().length > 150) return 'Máximo 150 caracteres';
            return null;
        },
        nivel: (value) => {
            if (!value) return 'Selecciona un nivel';
            return null;
        },
        precio: (value) => {
            if (!value) return 'El precio es obligatorio';
            const num = parseFloat(value);
            if (isNaN(num) || num <= 0) return 'Ingresa un precio válido';
            if (num > 999.99) return 'El precio máximo es $999.99';
            return null;
        }
    };

    // Validación en tiempo real (blur)
    Object.keys(validators).forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (!field) return;

        field.addEventListener('blur', () => {
            validateField(field, validators[fieldName]);
        });

        field.addEventListener('input', () => {
            // Limpiar error mientras escribe
            if (field.classList.contains('is-invalid')) {
                validateField(field, validators[fieldName]);
            }
        });
    });

    // Validación al enviar
    form.addEventListener('submit', (e) => {
        let hasErrors = false;

        Object.keys(validators).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                const error = validateField(field, validators[fieldName]);
                if (error) hasErrors = true;
            }
        });

        if (hasErrors) {
            e.preventDefault();
            showToast('Por favor corrige los errores en el formulario', 'warning');
            // Scroll al primer error
            const firstError = form.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        }
    });
}

function validateField(field, validator) {
    const value = field.value;
    const error = validator(value);
    const wrapper = field.closest('.book-form-group');
    let feedback = wrapper?.querySelector('.invalid-feedback');

    if (error) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        if (feedback) {
            feedback.textContent = error;
            feedback.style.display = 'block';
        }
        return error;
    } else {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        if (feedback) feedback.style.display = 'none';
        return null;
    }
}


/* ======================================================
   CHARACTER COUNTER — Contador para descripción
   ====================================================== */
function initCharCounter() {
    const textarea = document.getElementById('descripcion');
    const counter = document.getElementById('char-counter');
    if (!textarea || !counter) return;

    const maxLength = 1000;

    function updateCounter() {
        const remaining = maxLength - textarea.value.length;
        counter.textContent = `${textarea.value.length} / ${maxLength}`;
        counter.classList.toggle('text-danger', remaining < 50);
        counter.classList.toggle('text-warning', remaining >= 50 && remaining < 150);
    }

    textarea.addEventListener('input', updateCounter);
    updateCounter();
}


/* ======================================================
   DELETE CONFIRMATION — Modal de confirmación
   ====================================================== */
function initDeleteConfirmation() {
    const deleteForms = document.querySelectorAll('.delete-form');

    deleteForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const bookTitle = form.dataset.bookTitle || 'este libro';

            if (confirm(`¿Estás seguro de eliminar "${bookTitle}"?\n\nEsta acción no se puede deshacer.`)) {
                form.submit();
            }
        });
    });
}


/* ======================================================
   FILTER ANIMATIONS — Mejoras visuales en filtros
   ====================================================== */
function initFilterAnimations() {
    // Animar tarjetas al cargar
    const cards = document.querySelectorAll('.book-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.05}s`;
    });

    // Limpiar filtros
    const clearBtn = document.querySelector('.books-clear-filters');
    if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = clearBtn.href;
        });
    }
}


/* ======================================================
   TOAST NOTIFICATIONS — Notificaciones temporales
   ====================================================== */
function showToast(message, type = 'info') {
    const container = document.querySelector('.toast-container') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'danger' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Animación de entrada
    requestAnimationFrame(() => toast.classList.add('toast-show'));

    // Auto-remover después de 4s
    setTimeout(() => {
        toast.classList.remove('toast-show');
        toast.addEventListener('transitionend', () => toast.remove());
    }, 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}
