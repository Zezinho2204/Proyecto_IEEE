import os
from utils import extract_text_from_pdf
from analysis import analyze_cv
from models import Candidate, SessionLocal
import traceback

def process_cv(file_path, role=None):
    print(f"📄 Procesando: {file_path}")
    try:
        text = extract_text_from_pdf(file_path)
        analysis = analyze_cv(text, role)

        if "error" in analysis:
            print(f"❌ Error en análisis: {analysis['error']}")
            print(f"Raw output: {analysis['raw'][:200]}...")
            # Guardar igualmente con los datos básicos
            nombre = analysis.get("nombre", "Desconocido")
            email = analysis.get("email", "")
        else:
            nombre = analysis.get("nombre", "Desconocido")
            email = analysis.get("email", "")

        # Guardar en DB
        session = SessionLocal()
        candidato = Candidate(
            nombre=analysis.get("nombre", "Desconocido"),
            email=analysis.get("email", ""),
            perfil=analysis.get("perfil", ""),
            skills=",".join(analysis.get("skills", [])),
            experiencia=analysis.get("experiencia", ""),
            seniority=analysis.get("seniority", ""),
            area_profesional=analysis.get("area_profesional", ""),
            # Usar directamente el valor ya convertido
            match=analysis.get("match", 0),
            cv_text=text[:10000]  # Guardar solo parte del texto
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