import sqlite3
from tabulate import tabulate
from reportlab.lib.pagesizes import landscape, A3
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import sys
import re
import json

# Forzar UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def view_database(db_path="candidates.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email, perfil, skills, experiencia, seniority, area_profesional, match FROM candidates")
    rows = cursor.fetchall()
    headers = ["ID", "Nombre", "Email", "Perfil", "Habilidades", "Experiencia", "Nivel", "Área", "Match %"]

    # Mostrar en consola
    if rows:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        generate_pdf(headers, rows)
    else:
        print("📂 La base de datos está vacía.")

    conn.close()

def generate_pdf(headers, rows, filename="analisis_cvs.pdf"):
    # Configurar documento A3 horizontal con márgenes más amplios
    doc = SimpleDocTemplate(
        filename, 
        pagesize=landscape(A3),
        leftMargin=0.3 * inch,  # Reducido para más espacio
        rightMargin=0.3 * inch, # Reducido para más espacio
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Título más compacto
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=14,  # Reducido
        spaceAfter=10,
        alignment=1,
        textColor=colors.HexColor("#2c3e50")
    )
    title = Paragraph("<b>INFORME DE ANÁLISIS DE CVs</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Preparar datos para la tabla
    data = [headers]
    
    # Estilo para celdas más compacto pero legible
    wrap_style = ParagraphStyle(
        "WrapStyle",
        parent=styles["Normal"],
        fontSize=7,  # Reducido
        leading=8,   # Reducido
        spaceAfter=1,
        spaceBefore=1,
        wordWrap='CJK'
    )
    
    def clean_text(text):
        if not isinstance(text, str) or not text.strip():
            return ""
            
        text = text.strip()
        
        # Limpiar JSON y listas
        if (text.startswith('[') or text.startswith('{')):
            try:
                if text.startswith('['):
                    data_list = json.loads(text)
                    text = ", ".join(str(item) for item in data_list if str(item).strip())
                elif text.startswith('{'):
                    data_dict = json.loads(text)
                    text = ", ".join(f"{k}: {v}" for k, v in data_dict.items() if str(v).strip())
            except:
                text = re.sub(r'[\[\]\{\}\'\"]', '', text)
        
        # Corregir términos comunes
        corrections = {
            r'\bTechnología\b': 'Tecnología',
            r'\bElectrons\b': 'Electrónica',
            r'\bMicrocenter\b': 'Micro Center',
            r'\bPower Point\b': 'PowerPoint',
            r'\bSeniority\b': 'Nivel',
            r'\bAnálisis de perfil en proceso\b': 'Perfil análisis',
            r'\bAnálisis de experiencia en proceso\b': 'Experiencia análisis',
            r'\bÁrea profesional en análisis\b': 'Área análisis',
            r'\bNo especificado\b': 'Por analizar',
            r'\bHabilidades no especificadas\b': 'Habilidades análisis',
            r'\bExperiencia no especificada\b': 'Experiencia análisis'
        }
        
        for wrong, correct in corrections.items():
            text = re.sub(wrong, correct, text, flags=re.IGNORECASE)
        
        return text

    # Procesar cada fila con truncamiento más inteligente
    for row in rows:
        processed_row = []
        
        for i, item in enumerate(row):
            text = str(item) if item is not None else ""
            text = clean_text(text)
            
            # Asignar texto por defecto más corto
            if not text:
                if i == 3:  # Perfil
                    text = "Perfil análisis"
                elif i == 4:  # Habilidades
                    text = "Habilidades análisis"
                elif i == 5:  # Experiencia
                    text = "Experiencia análisis"
                elif i == 6:  # Nivel
                    text = "Por determinar"
                elif i == 7:  # Área
                    text = "Área análisis"
                elif i == 8:  # Match %
                    text = "0"
            
            # Truncamiento más agresivo pero inteligente
            if i == 3 and len(text) > 120:  # Perfil
                # Buscar punto natural para cortar
                cut_point = text.find('.', 80)
                if cut_point > 0:
                    text = text[:cut_point + 1]
                else:
                    text = text[:120] + "..."
                    
            elif i == 4 and len(text) > 100:  # Habilidades
                text = text[:100] + "..."
                
            elif i == 5 and len(text) > 150:  # Experiencia
                cut_point = text.find('.', 120)
                if cut_point > 0:
                    text = text[:cut_point + 1]
                else:
                    text = text[:150] + "..."
            
            processed_row.append(text)
        
        data.append(processed_row)
    
    # Convertir datos a Paragraphs para la tabla
    table_data = []
    for row_idx, row in enumerate(data):
        processed_row = []
        for col_idx, text in enumerate(row):
            if row_idx == 0:
                p = Paragraph(f"<b>{text}</b>", wrap_style)
            else:
                p = Paragraph(text, wrap_style)
            processed_row.append(p)
        table_data.append(processed_row)
    
    # ANCHOS DE COLUMNA OPTIMIZADOS - MÁS ESPACIO PARA COLUMNAS CLAVE
    col_widths = [
        0.4 * inch,   # ID (reducido)
        1.2 * inch,   # Nombre (reducido)
        1.6 * inch,   # Email (reducido)
        3.0 * inch,   # Perfil (aumentado)
        2.5 * inch,   # Habilidades (aumentado)
        3.5 * inch,   # Experiencia (aumentado)
        0.8 * inch,   # Nivel (reducido)
        1.5 * inch,   # Área (reducido)
        0.7 * inch    # Match % (reducido)
    ]
    
    # Calcular el ancho total
    total_width = sum(col_widths)
    available_width = landscape(A3)[0] - doc.leftMargin - doc.rightMargin
    
    # Ajustar proporcionalmente si es necesario
    if total_width > available_width:
        scale_factor = available_width / total_width
        col_widths = [w * scale_factor * 0.95 for w in col_widths]  # 95% para margen
    
    # Crear tabla
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Estilo de tabla ULTRA COMPACTO pero legible
    table_style = TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f2f3")),
        ('FONTSIZE', (0, 0), (-1, 0), 7),  # Reducido
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        
        # Filas de datos
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),  # Reducido
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        
        # Filas alternadas
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        
        # Alineación específica
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (8, 1), (8, -1), 'CENTER'),
        ('ALIGN', (6, 1), (6, -1), 'CENTER'),
    ])
    
    # Aplicar colores condicionales a match
    for i in range(1, len(table_data)):
        try:
            match_text = table_data[i][8].getPlainText()
            if match_text.isdigit():
                match_value = int(match_text)
                if match_value == 0:
                    table_style.add('BACKGROUND', (8, i), (8, i), colors.HexColor("#ffebee"))
                elif match_value < 50:
                    table_style.add('BACKGROUND', (8, i), (8, i), colors.HexColor("#fff3e0"))
                elif match_value < 80:
                    table_style.add('BACKGROUND', (8, i), (8, i), colors.HexColor("#e3f2fd"))
                else:
                    table_style.add('BACKGROUND', (8, i), (8, i), colors.HexColor("#e8f5e8"))
        except:
            pass
    
    table.setStyle(table_style)
    elements.append(table)
    
    # Pie de página mínimo
    elements.append(Spacer(1, 0.3 * inch))
    
    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=styles["Normal"],
        fontSize=8,
        alignment=1,
        textColor=colors.HexColor("#666666")
    )
    
    total_candidates = len(rows)
    footer = Paragraph(f"<b>Total de CVs analizados:</b> {total_candidates}", footer_style)
    elements.append(footer)
    
    # Generar PDF
    try:
        doc.build(elements)
        print(f"✅ PDF generado: {filename}")
        print(f"📊 Se analizaron {total_candidates} CVs")
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        # Intentar con página vertical si falla
        print("🔄 Intentando con formato vertical...")
        generate_pdf_fallback(headers, rows, filename)

def generate_pdf_fallback(headers, rows, filename):
    """Versión de fallback con página vertical"""
    from reportlab.lib.pagesizes import letter
    
    doc = SimpleDocTemplate(
        filename.replace('.pdf', '_vertical.pdf'), 
        pagesize=letter,
        leftMargin=0.3 * inch,
        rightMargin=0.3 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=12,
        spaceAfter=8,
        alignment=1
    )
    
    title = Paragraph("<b>INFORME DE CVs (Formato Vertical)</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Para formato vertical, mostrar menos datos por fila
    for row_idx, row in enumerate(rows):
        if row_idx > 0:  # Saltar encabezados
            elements.append(Paragraph(f"<b>CV {row[0]}: {row[1]}</b>", styles["Normal"]))
            elements.append(Paragraph(f"Email: {row[2]}", styles["Normal"]))
            elements.append(Paragraph(f"Perfil: {row[3][:100]}...", styles["Normal"]))
            elements.append(Paragraph(f"Habilidades: {row[4][:80]}...", styles["Normal"]))
            elements.append(Paragraph(f"Match: {row[8]}%", styles["Normal"]))
            elements.append(Spacer(1, 0.1 * inch))
            
            if row_idx % 3 == 0 and row_idx != len(rows) - 1:
                elements.append(PageBreak())
    
    try:
        doc.build(elements)
        print(f"✅ PDF vertical generado: {filename.replace('.pdf', '_vertical.pdf')}")
    except Exception as e:
        print(f"❌ Error también con formato vertical: {e}")

if __name__ == "__main__":
    view_database()