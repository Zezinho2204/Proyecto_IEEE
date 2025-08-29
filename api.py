from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from main import process_cv
from db import init_db
from models import Candidate, SessionLocal

app = FastAPI(title="CV Processor API", version="1.0.0")

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Servir el index.html en la raíz
@app.get("/")
def read_index():
    return FileResponse("index.html")

@app.get("/api")
def read_root():
    return {"message": "CV Processor API"}

@app.post("/process-cvs")
def process_all_cvs(role: str = None):
    """
    Procesa todos los CVs en la carpeta 'cvs'
    """
    try:
        # Inicializar base de datos antes de procesar
        init_db()
        
        folder = "cvs"
        if not os.path.exists(folder):
            return {"error": f"La carpeta '{folder}' no existe"}
        
        pdf_files = [f for f in os.listdir(folder) if f.endswith(".pdf")]
        
        if not pdf_files:
            return {"message": "No se encontraron archivos PDF en la carpeta 'cvs'"}
        
        processed_files = []
        for file in pdf_files:
            file_path = os.path.join(folder, file)
            process_cv(file_path, role if role else None)
            processed_files.append(file)
        
        return {
            "message": f"Procesados {len(processed_files)} archivos CV",
            "files": processed_files,
            "role": role if role else "detección automática"
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/candidates")
def get_candidates():
    """
    Obtiene todos los candidatos de la base de datos
    """
    try:
        session = SessionLocal()
        candidates = session.query(Candidate).all()
        
        candidates_data = []
        for candidate in candidates:
            candidates_data.append({
                "id": candidate.id,
                "nombre": candidate.nombre,
                "email": candidate.email,
                "perfil": candidate.perfil,
                "skills": candidate.skills,
                "seniority": candidate.seniority,
                "area_profesional": candidate.area_profesional,
                "match": candidate.match
            })
        
        session.close()
        return {"candidates": candidates_data}
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/pdf-files")
def get_pdf_files():
    """
    Lista todos los archivos PDF en la carpeta 'cvs'
    """
    try:
        folder = "cvs"
        if not os.path.exists(folder):
            os.makedirs(folder)
            return {"files": []}
        
        pdf_files = [f for f in os.listdir(folder) if f.endswith(".pdf")]
        
        # Obtener información adicional de cada archivo
        files_info = []
        for file in pdf_files:
            file_path = os.path.join(folder, file)
            file_size = os.path.getsize(file_path)
            files_info.append({
                "name": file,
                "size": file_size,
                "size_mb": round(file_size / 1024 / 1024, 2)
            })
        
        return {"files": files_info}
        
    except Exception as e:
        return {"error": str(e)}

@app.delete("/pdf-files/{filename}")
def delete_pdf_file(filename: str):
    """
    Elimina un archivo PDF específico de la carpeta 'cvs'
    """
    try:
        folder = "cvs"
        file_path = os.path.join(folder, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        if not filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Solo se pueden eliminar archivos PDF")
        
        os.remove(file_path)
        return {"message": f"Archivo {filename} eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}

@app.post("/pdf-files")
async def upload_pdf_file(file: UploadFile = File(...)):
    """
    Sube un archivo PDF a la carpeta 'cvs'
    """
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
        
        folder = "cvs"
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        file_path = os.path.join(folder, file.filename)
        
        # Verificar si el archivo ya existe
        if os.path.exists(file_path):
            raise HTTPException(status_code=409, detail="El archivo ya existe")
        
        # Guardar el archivo
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        return {
            "message": f"Archivo {file.filename} subido correctamente",
            "filename": file.filename,
            "size": len(contents)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}

@app.delete("/database")
def clear_database():
    """
    Limpia todos los registros de la base de datos candidates
    """
    try:
        session = SessionLocal()
        
        # Contar registros antes de eliminar
        count_before = session.query(Candidate).count()
        
        # Eliminar todos los registros
        session.query(Candidate).delete()
        session.commit()
        
        session.close()
        
        return {"message": f"Base de datos limpiada correctamente. Se eliminaron {count_before} registros."}
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)