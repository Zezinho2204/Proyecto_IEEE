import os
from utils import extract_text_from_pdf
from analysis import analyze_cv
from models import Candidate, SessionLocal
import traceback
import json
import re

def convert_to_text(data):
    """Convierte cualquier tipo de dato a texto para la base de datos"""
    if data is None:
        return ""
    
    if isinstance(data, list):
        # Si es una lista, convertir a string separado por comas
        return ", ".join(str(item) for item in data)
    elif isinstance(data, dict):
        # Si es un diccionario, convertirlo a string JSON
        try:
            return json.dumps(data, ensure_ascii=False)
        except:
            return str(data)
    else:
        # Para strings, números, etc.
        return str(data)

def safe_float(value):
    """Conversión segura a float"""
    try:
        return float(value)
    except:
        return 0.0

def process_cv(file_path, role=None):
    print(f"📄 Procesando: {file_path}")
    try:
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            print(f"❌ PDF vacío o no se pudo extraer texto: {file_path}")
            return
            
        analysis = analyze_cv(text, role)

        if analysis is not None and "error" in analysis:
            print(f"❌ Error en análisis: {analysis['error']}")
            if analysis.get("raw"):
                print(f"Raw output: {analysis['raw'][:200]}...")
            nombre = analysis.get("nombre", "Desconocido")
            email = analysis.get("email", "")
        else:
            nombre = analysis.get("nombre", "Desconocido")
            email = analysis.get("email", "")

        # Guardar en DB - SIN truncamiento excesivo
        session = SessionLocal()
        candidato = Candidate(
            nombre=nombre,
            email=email,
            perfil=analysis.get("perfil", ""),
            skills=analysis.get("skills", ""),
            experiencia=analysis.get("experiencia", ""),
            seniority=analysis.get("seniority", ""),
            area_profesional=analysis.get("area_profesional", ""),
            match=float(analysis.get("match", 0)),
            cv_text=text[:15000]  # Guardar más texto del CV
        )
        session.add(candidato)
        session.commit()
        session.close()
        print(f"✅ {file_path} procesado y guardado en DB\n")
        
    except Exception as e:
        print(f"🔥 Error crítico procesando {file_path}:")
        traceback.print_exc()
        print("")

if __name__ == "__main__":
    role = input("¿Quieres evaluar para un rol específico? (deja vacío para detectar automáticamente): ")
    folder = "cvs"
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            process_cv(os.path.join(folder, file), role if role else None)