import subprocess
import json
import re
import os
import sys

# Configurar stdout para UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Cargar modelo de spaCy para español
try:
    import spacy
    try:
        nlp = spacy.load("es_core_news_sm")
    except:
        nlp = None
except ImportError:
    nlp = None

def extract_name(text):
    """Extrae el nombre usando patrones mejorados"""
    # Buscar solo en la primera parte del CV
    search_text = text[:1000]
    
    # 1. Patrones comunes en CVs
    name_patterns = [
        r'(?i)nombre:\s*([^\n]{5,40})',
        r'(?i)curriculum vitae de\s+([^\n]{5,40})',
        r'(?i)cv de\s+([^\n]{5,40})',
        r'(?i)datos personales[^\n]*\n\s*([^\n]{5,40})',
        r'(?i)perfil profesional de\s+([^\n]{5,40})'
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, search_text)
        if match:
            name = match.group(1).strip()
            # Validar que tenga al menos 2 palabras y no contenga palabras comunes de CV
            if (len(name.split()) >= 2 and 
                not any(word in name.lower() for word in ['tecnología', 'informática', 'profesional', 'curriculum'])):
                return name
    
    # 2. Buscar la primera línea que parezca un nombre completo
    lines = search_text.split('\n')
    for line in lines:
        line = line.strip()
        # Debe contener 2-4 palabras, cada una comenzando con mayúscula
        if re.match(r'^([A-ZÁÉÍÓÚÜ][a-záéíóúüñ]+\s){1,3}[A-ZÁÉÍÓÚÜ][a-záéíóúüñ]+$', line):
            # Filtrar líneas que contengan palabras comunes de CV
            if not any(word in line.lower() for word in ['tecnología', 'informática', 'profesional', 'curriculum']):
                return line
    
    # 3. Si está disponible spaCy, usar NLP
    if nlp:
        try:
            doc = nlp(search_text)
            best_name = ""
            longest_name = 0
            
            for ent in doc.ents:
                if ent.label_ == "PER":
                    name = ent.text.strip()
                    word_count = len(name.split())
                    
                    # Preferir nombres con 2-4 palabras y más de 8 caracteres
                    if (word_count >= 2 and word_count <= 4 and 
                        len(name) > 8 and 
                        len(name) > longest_name and
                        not any(word in name.lower() for word in ['tecnología', 'informática', 'profesional'])):
                        best_name = name
                        longest_name = len(name)
            
            if best_name:
                return best_name
        except:
            pass
    
    return "Desconocido"

def extract_email(text):
    """Extrae email usando expresiones regulares"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else ""

def analyze_cv(text, role=None):
    # Extraer nombre y email antes del análisis
    nombre = extract_name(text)
    email = extract_email(text)
    
    # Limitar texto para evitar que se rompa
    max_chars = 4000
    if len(text) > max_chars:
        text = text[:max_chars] + "... [Texto truncado]"

    # Prompt mejorado con instrucciones más estrictas
    if role:
        prompt = f"""
        ### INSTRUCCIONES ###
        1. Analiza el CV para el rol específico: "{role}"
        2. Devuelve EXCLUSIVAMENTE un objeto JSON válido
        3. No incluyas ningún texto adicional, ni explicaciones
        4. No uses markdown, solo el JSON puro
        5. La estructura debe ser exactamente:
        {{
          "perfil": "Resumen breve (máx. 2 líneas)",
          "skills": ["Skill1", "Skill2", ...],
          "experiencia": "Descripción concisa",
          "seniority": "Junior | Semi-Senior | Senior",
          "area_profesional": "Área sugerida",
          "match": "Porcentaje (0-100)"
        }}
        
        ### CV ###
        {text}
        """
    else:
        prompt = f"""
        ### INSTRUCCIONES ###
        1. Analiza el CV para detectar el área profesional
        2. Devuelve EXCLUSIVAMENTE un objeto JSON válido
        3. No incluyas ningún texto adicional, ni explicaciones
        4. No uses markdown, solo el JSON puro
        5. La estructura debe ser exactamente:
        {{
          "perfil": "Resumen breve (máx. 2 líneas)",
          "skills": ["Skill1", "Skill2", ...],
          "experiencia": "Descripción concisa",
          "seniority": "Junior | Semi-Senior | Senior",
          "area_profesional": "Área sugerida",
          "match": "100"
        }}
        
        ### CV ###
        {text}
        """

    try:
        # Forzar codificación UTF-8
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        # Ejecutar con manejo robusto de codificación
        result = subprocess.run(
            ["ollama", "run", "deepseek-r1"],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env
        )

        output = result.stdout.strip()
        
        # Si hay error en stderr, mostrarlo
        if result.stderr:
            print(f"⚠️ Error en Ollama: {result.stderr[:200]}...")

        # Mejorar la extracción del JSON
        json_text = extract_json_from_output(output)
        
        if json_text:
            try:
                analysis = json.loads(json_text)
                
                # Limpiar y convertir el campo 'match'
                if "match" in analysis:
                    match_str = str(analysis["match"])
                    # Extraer solo números y punto decimal
                    match_clean = re.sub(r'[^\d.]', '', match_str)
                    try:
                        match_value = float(match_clean)
                        analysis["match"] = max(0, min(100, match_value))
                    except:
                        analysis["match"] = 0.0
                
                # Agregar nombre y email extraídos
                analysis["nombre"] = nombre
                analysis["email"] = email
                return analysis
            except json.JSONDecodeError as e:
                return {
                    "error": f"JSON inválido: {str(e)}", 
                    "raw": output[:500] + "..." if len(output) > 500 else output,
                    "nombre": nombre,
                    "email": email
                }
        else:
            return {
                "error": "No se encontró JSON en la respuesta", 
                "raw": output[:500] + "..." if len(output) > 500 else output,
                "nombre": nombre,
                "email": email
            }

    except Exception as e:
        return {
            "error": f"Error ejecutando Ollama: {str(e)}", 
            "raw": "",
            "nombre": nombre,
            "email": email
        }

def extract_json_from_output(output):
    """Extrae el JSON de la salida del modelo, incluso si tiene texto adicional"""
    # Estrategia 1: Buscar JSON válido completo
    try:
        # Buscar desde el primer { hasta el último }
        start_index = output.find('{')
        end_index = output.rfind('}')
        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_text = output[start_index:end_index+1]
            # Intentar validar
            json.loads(json_text)
            return json_text
    except:
        pass
    
    # Estrategia 2: Buscar JSON en formato de código
    try:
        # Buscar en bloques ```json ... ```
        match = re.search(r'```json\s*({.*?})\s*```', output, re.DOTALL)
        if match:
            json_text = match.group(1)
            json.loads(json_text)  # Validar
            return json_text
        
        # Buscar en bloques ``` ... ``` sin especificar json
        match = re.search(r'```\s*({.*?})\s*```', output, re.DOTALL)
        if match:
            json_text = match.group(1)
            json.loads(json_text)  # Validar
            return json_text
    except:
        pass
    
    # Estrategia 3: Buscar el primer objeto JSON válido
    try:
        # Buscar todos los posibles objetos JSON
        json_candidates = []
        start = 0
        while start < len(output):
            start_index = output.find('{', start)
            if start_index == -1:
                break
                
            end_index = output.find('}', start_index)
            if end_index == -1:
                break
                
            # Buscar el cierre completo
            depth = 1
            current = start_index + 1
            while current < len(output) and depth > 0:
                if output[current] == '{':
                    depth += 1
                elif output[current] == '}':
                    depth -= 1
                current += 1
                
            if depth == 0:
                json_text = output[start_index:current]
                try:
                    json.loads(json_text)
                    json_candidates.append(json_text)
                except:
                    pass
                
            start = current
        
        # Seleccionar el candidato más largo
        if json_candidates:
            return max(json_candidates, key=len)
    except:
        pass
    
    return None