# CV Processor - Sistema de Análisis Automático de CVs con IA

Sistema inteligente para el análisis automático de currículums vitae utilizando inteligencia artificial local (Ollama + DeepSeek-R1) con aceleración GPU NVIDIA. El sistema procesa archivos PDF, extrae información relevante y proporciona análisis detallados de candidatos.

## 🌟 Características Principales

- **Análisis de CV con IA**: Utiliza DeepSeek-R1 para análisis inteligente y preciso
- **Interfaz Web**: Interfaz moderna para gestión de archivos y visualización de resultados
- **API REST**: Endpoints completos para integración con otros sistemas
- **Aceleración GPU**: Optimizado para GPUs NVIDIA con CUDA
- **Procesamiento PDF**: Extracción de texto avanzada con corrección de caracteres
- **Base de Datos SQLite**: Almacenamiento persistente de candidatos y análisis
- **Gestión de Archivos**: Upload, listado y eliminación de CVs

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   FastAPI        │───▶│   Ollama        │
│   (HTML/JS/CSS) │    │   REST API       │    │   + DeepSeek-R1 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
                       ┌──────────────┐           ┌─────────────┐
                       │   SQLite     │           │   GPU       │
                       │   Database   │           │   NVIDIA    │
                       └──────────────┘           └─────────────┘
```

## 📋 Requisitos del Sistema

### Hardware
- **GPU**: NVIDIA GTX 1050 o superior (mínimo 4GB VRAM)
- **RAM**: 8GB mínimo, 16GB recomendado
- **Almacenamiento**: 10GB libres para modelos de IA

### Software
- **OS**: Linux (Ubuntu 20.04+ recomendado)
- **Python**: 3.8+
- **NVIDIA Drivers**: 535.x o superior
- **CUDA**: 12.x
- **Ollama**: Última versión

---

# 🚀 Documentación instalar drivers de Nvidia para usar CUDA en linux

## 1. Verificar la tarjeta gráfica NVIDIA

```bash
# Verificar que tienes una GPU NVIDIA
lspci | grep -i nvidia

# Verificar el modelo específico
nvidia-smi

```

## 2. Instalar drivers NVIDIA

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar drivers recomendados
sudo ubuntu-drivers devices
sudo ubuntu-drivers autoinstall

# O instalar manualmente (reemplaza XXX con la versión)
sudo apt install nvidia-driver-535

# Reiniciar el sistema
sudo reboot

```

## 3. Verificar instalación de drivers

```bash
# Verificar que los drivers están funcionando
nvidia-smi

# Debería mostrar información de tu GPU

```

## 4. Instalar CUDA Toolkit

```bash
# Descargar e instalar CUDA (versión 12.x)
wget https://developer.download.nvidia.com/compute/cuda/12.3.0/local_installers/cuda_12.3.0_545.23.06_linux.run

# Hacer ejecutable
chmod +x cuda_12.3.0_545.23.06_linux.run

# Instalar (NO instalar drivers si ya están instalados)
sudo sh cuda_12.3.0_545.23.06_linux.run

```

## 5. Configurar variables de entorno

```bash
# Editar .bashrc
nano ~/.bashrc

# Agregar al final del archivo:
export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

# Recargar configuración
source ~/.bashrc

```

## 6. Verificar instalación de CUDA

```bash
# Verificar versión de CUDA
nvcc --version

# Verificar que las librerías están disponibles
nvidia-smi

```

## 7. Instalar Ollama

```bash
# Método 1: Script oficial
curl -fsSL https://ollama.ai/install.sh | sh

# Método 2: Manual
wget https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64
sudo mv ollama-linux-amd64 /usr/local/bin/ollama
sudo chmod +x /usr/local/bin/ollama

```

## 8. Configurar Ollama para usar GPU

```bash
# Iniciar servicio Ollama
sudo systemctl start ollama
sudo systemctl enable ollama

# O ejecutar manualmente
ollama serve &

```

## 9. Verificar que Ollama detecta CUDA

```bash
# Verificar información del sistema
ollama --version

# Descargar un modelo para probar
ollama pull llama2

# Ejecutar modelo (debería usar GPU automáticamente)
ollama run llama2

```

## 10. Comandos de diagnóstico

```bash
# Verificar uso de GPU mientras ejecutas Ollama
watch -n 1 nvidia-smi

# Verificar logs de Ollama
journalctl -u ollama -f

# Verificar procesos usando GPU
nvidia-smi pmon

# Verificar librerías CUDA
ldconfig -p | grep cuda

```

## 11. Solución de problemas comunes

### Si Ollama no detecta CUDA:

```bash
# Verificar que CUDA está en el PATH
echo $PATH
echo $LD_LIBRARY_PATH

# Reinstalar Ollama con soporte CUDA explícito
curl -fsSL https://ollama.ai/install.sh | sh

# Verificar compatibilidad de versiones
nvidia-smi
nvcc --version

```

### Si hay conflictos de drivers:

```bash
# Limpiar instalaciones previas
sudo apt remove --purge nvidia-*
sudo apt autoremove
sudo apt autoclean

# Reinstalar drivers
sudo ubuntu-drivers autoinstall
sudo reboot

```

### Variables de entorno adicionales:

```bash
# Si persisten problemas, agregar a ~/.bashrc:
export CUDA_HOME=/usr/local/cuda
export CUDA_ROOT=/usr/local/cuda
export NVIDIA_VISIBLE_DEVICES=all
export NVIDIA_DRIVER_CAPABILITIES=compute,utility

```

## 12. Optimizaciones adicionales

```bash
# Configurar límites de memoria GPU (opcional)
export OLLAMA_GPU_MEMORY_FRACTION=0.8

# Configurar número de capas en GPU
export OLLAMA_NUM_GPU_LAYERS=35

# Verificar configuración
env | grep OLLAMA

```

## 13. Comandos de mantenimiento

```bash
# Actualizar drivers NVIDIA
sudo apt update && sudo apt upgrade nvidia-driver-*

# Verificar temperatura GPU
nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits

# Monitorear uso en tiempo real
nvidia-smi dmon

```

---

# 📦 Instalación del Proyecto CV Processor

## 1. Instalar dependencias del sistema

```bash
# Instalar Python y pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Instalar dependencias del sistema para PDF
sudo apt install python3-dev build-essential
```

## 2. Clonar y configurar el proyecto

```bash
# Clonar el repositorio (ajustar según tu repositorio)
git clone <tu-repositorio>
cd cv-processor

# Crear entorno virtual
python3 -m venv .env
source .env/bin/activate

# Instalar dependencias Python
pip install -r requirements.txt
```

## 3. Configurar Ollama y descargar modelo

```bash
# Descargar el modelo DeepSeek-R1 (requerido por el sistema)
ollama pull deepseek-r1:1.5b

# Verificar que el modelo está disponible
ollama list
```

## 4. Preparar estructura de directorios

```bash
# Crear directorio para CVs
mkdir -p cvs

# Crear directorio para estáticos (ya debería existir)
mkdir -p static
```

## 5. Inicializar base de datos

```bash
# Ejecutar script de inicialización
python db.py
```

---

# 🚀 Uso del Sistema

## Opción 1: Interfaz Web

```bash
# Iniciar servidor web
python api.py

# O con uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Acceder a**: `http://localhost:8000`

### Funciones disponibles en la interfaz web:
- ✅ Upload de archivos PDF
- ✅ Listar CVs en el sistema
- ✅ Procesar todos los CVs automáticamente
- ✅ Ver resultados de análisis
- ✅ Gestión de base de datos

## Opción 2: Línea de Comandos

```bash
# Procesar todos los CVs en la carpeta 'cvs'
python main.py

# Se solicitará rol específico (opcional)
```

## Opción 3: API REST

### Endpoints disponibles:

**GET** `/` - Página principal
**GET** `/api` - Estado de la API
**POST** `/process-cvs` - Procesar todos los CVs
**GET** `/candidates` - Obtener candidatos procesados
**GET** `/pdf-files` - Listar archivos PDF
**POST** `/pdf-files` - Subir nuevo PDF
**DELETE** `/pdf-files/{filename}` - Eliminar PDF
**DELETE** `/database` - Limpiar base de datos

### Ejemplo de uso con curl:

```bash
# Procesar CVs
curl -X POST "http://localhost:8000/process-cvs" \
     -H "Content-Type: application/json" \
     -d '{"role": "desarrollador"}'

# Obtener candidatos
curl -X GET "http://localhost:8000/candidates"
```

---

# 📁 Estructura del Proyecto

```
cv-processor/
├── README.md                 # Este archivo
├── requirements.txt          # Dependencias Python
├── main.py                  # Procesamiento por lotes
├── api.py                   # Servidor FastAPI
├── analysis.py              # Lógica de análisis con IA
├── models.py                # Modelos de base de datos
├── db.py                    # Inicialización de BD
├── utils.py                 # Utilidades (extracción PDF)
├── view_db.py              # Visualizador de BD
├── index.html              # Interfaz web principal
├── candidates.db           # Base de datos SQLite
├── static/                 # Recursos web
│   ├── style.css           # Estilos
│   └── script.js           # JavaScript
├── cvs/                    # Directorio para CVs
│   └── *.pdf               # Archivos PDF a procesar
└── .env/                   # Entorno virtual Python
```

---

# 🔧 Configuración Avanzada

## Variables de Entorno para GPU

El sistema está optimizado para aprovechar al máximo las GPUs NVIDIA:

```bash
# En analysis.py se configuran automáticamente:
export OLLAMA_GPU=1
export OLLAMA_GPU_LAYERS=35
export OLLAMA_VRAM_FRACTION=0.8
export CUDA_VISIBLE_DEVICES=0
export NVIDIA_VISIBLE_DEVICES=0
export OLLAMA_CUDA=1
export OLLAMA_DEBUG=1
```

## Configuración del Modelo IA

En `analysis.py`, puedes ajustar:

```python
MODEL_NAME = "deepseek-r1:1.5b"  # Modelo utilizado
MAX_RETRIES = 2                  # Reintentos en caso de error
```

## Personalización de Análisis

El sistema permite personalizar:
- **Extracción de habilidades**: Lista whitelist en `extract_skills_from_text()`
- **Áreas profesionales**: Categorías en `extract_professional_area()`
- **Prompts de IA**: Template en `create_honest_prompt()`

---

# 🔍 Monitoreo y Depuración

## Verificar uso de GPU

```bash
# Durante el procesamiento, monitorear GPU
watch -n 1 nvidia-smi

# El sistema mostrará automáticamente:
# ✅ GPU ACEPTADA: XXXX MB libres
# 🚀 EJECUTANDO CON GPU FORZADA...
# ✅ CONFIRMADO: Ollama utilizó GPU durante la ejecución
```

## Logs del sistema

```bash
# Ver logs de Ollama
journalctl -u ollama -f

# Ver procesos GPU activos
nvidia-smi pmon

# Monitorear temperatura y uso
nvidia-smi dmon
```

## Troubleshooting Común

### ❌ Error: GPU no disponible
```bash
# Verificar drivers
nvidia-smi

# Reiniciar servicio Ollama
sudo systemctl restart ollama

# Verificar variables de entorno
env | grep CUDA
env | grep OLLAMA
```

### ❌ Error: Modelo no encontrado
```bash
# Descargar modelo requerido
ollama pull deepseek-r1:1.5b

# Verificar modelos disponibles
ollama list
```

### ❌ Error: PDF no se puede procesar
```bash
# Verificar permisos del directorio cvs/
ls -la cvs/

# Verificar que el PDF no esté corrupto
file cvs/tu-archivo.pdf
```

---

# 📊 Métricas y Rendimiento

## Rendimiento esperado (con GPU NVIDIA GTX 1050):
- **Tiempo por CV**: 15-45 segundos
- **Memoria GPU utilizada**: ~1.5-2GB
- **Precisión de extracción**: 85-95%
- **Formatos soportados**: PDF (texto extraíble)

## Monitoreo de métricas:
- El sistema incluye timestamps de procesamiento
- Verificación automática de uso de GPU
- Logging detallado de errores y excepciones

---

# 🤝 Contribución

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

# 🛠️ Notas Técnicas Importantes

## Compatibilidad GPU
1. **Requerimientos mínimos**: GTX 600 series o superior
2. **Memoria recomendada**: Para modelos grandes (7B+) necesitas al menos 8GB de VRAM
3. **Compatibilidad de versiones**: Mantén consistencia entre driver NVIDIA, CUDA toolkit y Ollama
4. **Reinicio obligatorio**: Después de instalar drivers, siempre reinicia el sistema

## Verificación Final de Instalación

Si todo está configurado correctamente, cuando ejecutes el análisis de CVs deberías ver:

- ✅ GPU utilizada en `nvidia-smi`
- ✅ Respuestas más rápidas del modelo de IA
- ✅ Uso de VRAM en lugar de RAM del sistema
- ✅ Logs confirmando "CONFIRMADO: Ollama utilizó GPU durante la ejecución"

## Seguridad y Privacidad

- ⚠️ Los CVs se procesan localmente (no se envían a servidores externos)
- ⚠️ Los datos se almacenan en SQLite local
- ⚠️ Se recomienda configurar backups regulares de la BD
- ⚠️ Implementar autenticación para uso en producción

---

# 📞 Soporte

Para reportar problemas o solicitar funcionalidades:
- Crear issue en el repositorio
- Incluir logs relevantes y especificaciones del sistema
- Describir pasos para reproducir el problema

**¡El sistema está optimizado para aprovechar al máximo la aceleración GPU y proporcionar análisis precisos de CVs en español!**# Proyecto_IEEE
