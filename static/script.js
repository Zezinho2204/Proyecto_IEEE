
async function processCVs() {
    const roleInput = document.getElementById('role');
    const processBtn = document.getElementById('processBtn');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    
    // Deshabilitar botón y mostrar loading
    processBtn.disabled = true;
    loadingDiv.style.display = 'block';
    resultsDiv.innerHTML = '';
    
    try {
        const role = roleInput.value.trim();
        const url = role 
            ? `/process-cvs?role=${encodeURIComponent(role)}`
            : `/process-cvs`;
            
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displaySuccess(data);
            // Cargar candidatos después del procesamiento
            setTimeout(loadCandidates, 1000);
        } else {
            displayError(data.error || 'Error desconocido');
        }
        
    } catch (error) {
        displayError(`Error de conexión: ${error.message}`);
    } finally {
        // Rehabilitar botón y ocultar loading
        processBtn.disabled = false;
        loadingDiv.style.display = 'none';
    }
}

function displaySuccess(data) {
    const resultsDiv = document.getElementById('results');
    
    const html = `
        <div class="success">
            <h3>✅ Procesamiento completado</h3>
            <p><strong>Mensaje:</strong> ${data.message}</p>
            <p><strong>Rol:</strong> ${data.role || 'No especificado'}</p>
            
            ${data.files && data.files.length > 0 ? `
                <div class="files-processed">
                    <h4>Archivos procesados:</h4>
                    <ul>
                        ${data.files.map(file => `<li>${file}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

function displayError(errorMessage) {
    const resultsDiv = document.getElementById('results');
    
    const html = `
        <div class="error">
            <h3>❌ Error</h3>
            <p>${errorMessage}</p>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

async function checkAPIStatus() {
    const statusDiv = document.getElementById('apiStatus');
    
    try {
        const response = await fetch(`/api`);
        const data = await response.json();
        
        if (response.ok) {
            statusDiv.innerHTML = `
                <span class="status-online">🟢 API Online</span>
                <small>${data.message}</small>
            `;
        } else {
            throw new Error('API no disponible');
        }
    } catch (error) {
        statusDiv.innerHTML = `
            <span class="status-offline">🔴 API Offline</span>
            <small>Error de conexión con el servidor</small>
        `;
    }
}

async function loadCandidates() {
    const candidatesDiv = document.getElementById('candidates');
    
    try {
        const response = await fetch('/candidates');
        const data = await response.json();
        
        if (response.ok && data.candidates) {
            // Guardar los datos globalmente para el modal
            window.candidatesData = data.candidates;
            displayCandidates(data.candidates);
        } else {
            candidatesDiv.innerHTML = `
                <div class="error">
                    <p>Error al cargar candidatos: ${data.error || 'Error desconocido'}</p>
                </div>
            `;
        }
    } catch (error) {
        candidatesDiv.innerHTML = `
            <div class="error">
                <p>Error de conexión al cargar candidatos: ${error.message}</p>
            </div>
        `;
    }
}

function displayCandidates(candidates) {
    const candidatesDiv = document.getElementById('candidates');
    
    if (candidates.length === 0) {
        candidatesDiv.innerHTML = `
            <div class="no-data">
                <p>No hay candidatos en la base de datos</p>
            </div>
        `;
        return;
    }
    
    const cardsHTML = `
        <div class="candidates-section">
            <h3>📊 Candidatos Procesados (${candidates.length})</h3>
            <div class="cards-container">
                ${candidates.map(candidate => `
                    <div class="candidate-card">
                        <div class="card-header">
                            <h4 class="candidate-name">${candidate.nombre || 'Nombre no disponible'}</h4>
                            <div class="match-badge ${getMatchClass(candidate.match)}">
                                ${candidate.match ? candidate.match.toFixed(1) + '%' : 'N/A'}
                            </div>
                        </div>
                        <div class="card-body">
                            <p class="candidate-area"><strong>Área:</strong> ${candidate.area_profesional || 'No especificada'}</p>
                            <p class="candidate-seniority"><strong>Nivel:</strong> ${candidate.seniority || 'No especificado'}</p>
                        </div>
                        <div class="card-footer">
                            <button class="btn-details" onclick="showCandidateDetails(${candidate.id})">
                                Ver Detalles
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    candidatesDiv.innerHTML = cardsHTML;
}

function getMatchClass(match) {
    if (!match) return 'match-na';
    if (match >= 80) return 'match-high';
    if (match >= 60) return 'match-medium';
    return 'match-low';
}

function showCandidateDetails(candidateId) {
    // Buscar el candidato en los datos ya cargados
    const candidatesDiv = document.getElementById('candidates');
    // Necesitamos acceder a los datos, así que los guardaremos globalmente
    const candidate = window.candidatesData?.find(c => c.id === candidateId);
    
    if (!candidate) {
        showToast('No se pudieron cargar los detalles del candidato', 'error');
        return;
    }
    
    const modalHTML = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>${candidate.nombre || 'Candidato'}</h3>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="detail-section">
                        <h4>Información Personal</h4>
                        <p><strong>Nombre:</strong> ${candidate.nombre || 'No disponible'}</p>
                        <p><strong>Email:</strong> ${candidate.email || 'No disponible'}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h4>Perfil Profesional</h4>
                        <p><strong>Área Profesional:</strong> ${candidate.area_profesional || 'No especificada'}</p>
                        <p><strong>Nivel de Seniority:</strong> ${candidate.seniority || 'No especificado'}</p>
                        <p><strong>Compatibilidad:</strong> 
                            <span class="match-score ${getMatchClass(candidate.match)}">
                                ${candidate.match ? candidate.match.toFixed(1) + '%' : 'N/A'}
                            </span>
                        </p>
                    </div>
                    
                    <div class="detail-section">
                        <h4>Perfil Detallado</h4>
                        <p>${candidate.perfil || 'No disponible'}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h4>Habilidades y Competencias</h4>
                        <p>${candidate.skills || 'No especificadas'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }
}

async function loadPDFFiles() {
    const pdfFilesDiv = document.getElementById('pdfFiles');
    
    try {
        const response = await fetch('/pdf-files');
        const data = await response.json();
        
        if (response.ok && data.files) {
            displayPDFFiles(data.files);
        } else {
            pdfFilesDiv.innerHTML = `
                <div class="error">
                    <p>Error al cargar archivos PDF: ${data.error || 'Error desconocido'}</p>
                </div>
            `;
        }
    } catch (error) {
        pdfFilesDiv.innerHTML = `
            <div class="error">
                <p>Error de conexión al cargar archivos PDF: ${error.message}</p>
            </div>
        `;
    }
}

function displayPDFFiles(files) {
    const pdfFilesDiv = document.getElementById('pdfFiles');
    
    if (files.length === 0) {
        pdfFilesDiv.innerHTML = `
            <div class="no-data">
                <p>No hay archivos PDF en la carpeta cvs/</p>
            </div>
        `;
        return;
    }
    
    const filesHTML = `
        <div class="files-grid">
            ${files.map(file => `
                <div class="file-item">
                    <div class="file-info">
                        <span class="file-name">📄 ${file.name}</span>
                        <span class="file-size">${file.size_mb} MB</span>
                    </div>
                    <button class="btn-delete" onclick="deletePDF('${file.name}')">
                        🗑️ Eliminar
                    </button>
                </div>
            `).join('')}
        </div>
    `;
    
    pdfFilesDiv.innerHTML = filesHTML;
}

async function uploadPDFs() {
    const fileInput = document.getElementById('pdfFile');
    const files = fileInput.files;
    
    if (files.length === 0) {
        showToast('Por favor selecciona al menos un archivo PDF', 'warning');
        return;
    }
    
    for (let file of files) {
        if (!file.name.endsWith('.pdf')) {
            showToast(`El archivo ${file.name} no es un PDF válido`, 'warning');
            continue;
        }
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/pdf-files', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                console.log(`Archivo ${file.name} subido correctamente`);
            } else {
                if (response.status === 409) {
                    showToast(`El archivo ${file.name} ya existe`, 'warning');
                } else {
                    showToast(`Error al subir ${file.name}: ${data.error || data.detail || 'Error desconocido'}`, 'error');
                }
            }
        } catch (error) {
            showToast(`Error al subir ${file.name}: ${error.message}`, 'error');
        }
    }
    
    // Limpiar el input y recargar la lista
    fileInput.value = '';
    updateFileCount(); // Actualizar contador
    loadPDFFiles();
    
    showToast('Proceso de subida completado', 'success');
}

async function deletePDF(filename) {
    const confirmed = await showConfirm({
        title: 'Eliminar archivo',
        message: `¿Estás seguro de que quieres eliminar el archivo "${filename}"?`,
        icon: '🗑️',
        confirmText: 'Eliminar',
        cancelText: 'Cancelar',
        type: 'danger'
    });

    if (!confirmed) return;
    
    try {
        const response = await fetch(`/pdf-files/${encodeURIComponent(filename)}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(`Archivo ${filename} eliminado correctamente`, 'success');
            loadPDFFiles(); // Recargar la lista
        } else {
            showToast(`Error al eliminar archivo: ${data.error || data.detail || 'Error desconocido'}`, 'error');
        }
    } catch (error) {
        showToast(`Error de conexión al eliminar archivo: ${error.message}`, 'error');
    }
}

async function clearDatabase() {
    const confirmed = await showConfirm({
        title: 'Limpiar Base de Datos',
        message: '¿Estás seguro de que quieres eliminar todos los registros de candidatos? Esta acción no se puede deshacer.',
        icon: '🗑️',
        confirmText: 'Limpiar',
        cancelText: 'Cancelar',
        type: 'danger'
    });

    if (!confirmed) return;
    
    try {
        const response = await fetch('/database', {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message, 'success');
            // Recargar candidatos para mostrar que está vacía
            loadCandidates();
        } else {
            showToast(`Error al limpiar base de datos: ${data.error || 'Error desconocido'}`, 'error');
        }
    } catch (error) {
        showToast(`Error de conexión al limpiar base de datos: ${error.message}`, 'error');
    }
}

// Sistema de notificaciones toast
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toast-container');
    
    // Crear el toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Icono según el tipo
    const icons = {
        success: '✅',
        error: '❌', 
        info: 'ℹ️',
        warning: '⚠️'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-content">${message}</span>
        <button class="toast-close" onclick="hideToast(this.parentElement)">×</button>
    `;
    
    // Añadir al contenedor
    toastContainer.appendChild(toast);
    
    // Auto-ocultar después de la duración especificada
    setTimeout(() => {
        hideToast(toast);
    }, duration);
    
    return toast;
}

function hideToast(toast) {
    if (toast && !toast.classList.contains('toast-hiding')) {
        toast.classList.add('toast-hiding');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
}

// Sistema de confirmación modal
function showConfirm(options) {
    return new Promise((resolve) => {
        const {
            title = '¿Estás seguro?',
            message = '¿Deseas continuar con esta acción?',
            icon = '⚠️',
            confirmText = 'Confirmar',
            cancelText = 'Cancelar',
            type = 'danger'
        } = options;

        // Crear el modal
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'confirm-modal-overlay';
        
        modalOverlay.innerHTML = `
            <div class="confirm-modal">
                <span class="confirm-modal-icon">${icon}</span>
                <div class="confirm-modal-title">${title}</div>
                <div class="confirm-modal-message">${message}</div>
                <div class="confirm-modal-buttons">
                    <button class="confirm-btn confirm-btn-cancel" onclick="closeConfirmModal(false)">${cancelText}</button>
                    <button class="confirm-btn confirm-btn-${type}" onclick="closeConfirmModal(true)">${confirmText}</button>
                </div>
            </div>
        `;

        // Función para cerrar el modal
        window.closeConfirmModal = (result) => {
            modalOverlay.remove();
            resolve(result);
            delete window.closeConfirmModal;
        };

        // Cerrar con click fuera del modal
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                window.closeConfirmModal(false);
            }
        });

        // Cerrar con Escape
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                window.closeConfirmModal(false);
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);

        // Añadir al DOM
        document.body.appendChild(modalOverlay);
    });
}

// Función para actualizar el contador de archivos
function updateFileCount() {
    const fileInput = document.getElementById('pdfFile');
    const fileCount = document.getElementById('fileCount');
    
    if (fileInput.files.length > 0) {
        fileCount.textContent = `${fileInput.files.length} archivo${fileInput.files.length > 1 ? 's' : ''} seleccionado${fileInput.files.length > 1 ? 's' : ''}`;
    } else {
        fileCount.textContent = '';
    }
}

// Verificar estado de la API al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    checkAPIStatus();
    loadCandidates(); // Cargar candidatos al inicio
    loadPDFFiles(); // Cargar archivos PDF al inicio
    
    // Agregar evento al input de archivos para actualizar el contador
    const fileInput = document.getElementById('pdfFile');
    fileInput.addEventListener('change', updateFileCount);
    
    // Verificar estado cada 30 segundos
    setInterval(checkAPIStatus, 30000);
});