import fitz
import re

def extract_text_from_pdf(file_path):
    """Extrae texto de PDF con manejo robusto de caracteres"""
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text", sort=True)
    except Exception as e:
        print(f"⚠️ Error abriendo PDF {file_path}: {str(e)}")
        return ""
    
    # Limpiar caracteres no válidos y corregir codificación
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Correcciones específicas para caracteres mal codificados
    replacements = {
        "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
        "Ã±": "ñ", "Ã‘": "Ñ", "Ã€": "À", "Ã‰": "É", "Ã“": "Ó",
        "Ãš": "Ú", "Ã±": "ñ", "Ãˆ": "È", "Ã¼": "ü", "Ã§": "ç",
        "Ã¢": "â", "Ãª": "ê", "Ã®": "î", "Ã´": "ô", "Ã»": "û",
        "Ã…": "Å", "Ã¸": "ø", "Ã†": "Æ", "Ã…": "Å", "ÃŸ": "ß"
    }
    
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    
    return text