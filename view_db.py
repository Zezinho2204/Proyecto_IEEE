import sqlite3
from tabulate import tabulate
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import sys
import re

# Forzar UTF-8 para Windows
sys.stdout.reconfigure(encoding='utf-8')

def view_database(db_path="candidates.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email, perfil, skills, experiencia, seniority, area_profesional, match FROM candidates")
    rows = cursor.fetchall()
    headers = ["ID", "Nombre", "Email", "Perfil", "Skills", "Experiencia", "Seniority", "Área", "Match %"]

    # Recortar columnas largas para la consola
    formatted_rows = []
    for r in rows:
        formatted_rows.append((
            r[0],
            r[1] or "",
            r[2] or "",
            (r[3][:50] + "...") if r[3] and len(r[3]) > 50 else (r[3] or ""),
            (r[4][:30] + "...") if r[4] and len(r[4]) > 30 else (r[4] or ""),
            (r[5][:50] + "...") if r[5] and len(r[5]) > 50 else (r[5] or ""),
            r[6] or "",
            r[7] or "",
            r[8]
        ))

    if rows:
        print(tabulate(formatted_rows, headers=headers, tablefmt="fancy_grid"))
        generate_pdf(headers, rows)
    else:
        print("📂 La base de datos está vacía.")

    conn.close()

def generate_pdf(headers, rows, filename="analisis_cvs.pdf"):
    # Configurar documento en horizontal con márgenes mínimos
    doc = SimpleDocTemplate(
        filename, 
        pagesize=landscape(letter),
        leftMargin=0.15 * inch,
        rightMargin=0.15 * inch,
        topMargin=0.25 * inch,
        bottomMargin=0.25 * inch
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Título más compacto
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=12,
        spaceAfter=6
    )
    title = Paragraph("Informe de Análisis de CVs", title_style)
    elements.append(title)
    
    # Preparar datos para la tabla
    data = [headers]
    
    # Estilo para celdas con texto largo - fuente más pequeña
    wrap_style = ParagraphStyle(
        "WrapStyle",
        parent=styles["Normal"],
        fontSize=6,  # Tamaño reducido
        leading=7,   # Interlineado reducido
        spaceAfter=0,
        spaceBefore=0
    )
    
    # Función para corregir caracteres mal codificados
    def fix_encoding(text):
        # Correcciones comunes para caracteres latinos
        replacements = {
            "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
            "Ã±": "ñ", "Ã‘": "Ñ", "Ã€": "À", "Ã‰": "É", "Ã“": "Ó",
            "Ãš": "Ú", "Ã±": "ñ", "Ãˆ": "È", "Ã¼": "ü", "Ã§": "ç",
            "Ã¢": "â", "Ãª": "ê", "Ã®": "î", "Ã´": "ô", "Ã»": "û",
            "Ã…": "Å", "Ã¸": "ø", "Ã†": "Æ", "Ã…": "Å", "ÃŸ": "ß"
        }
        
        # Aplicar reemplazos
        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)
        
        # Eliminar caracteres de control
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        return text
    
    # Procesar filas para el PDF - AUMENTAMOS LOS LÍMITES DE TRUNCAMIENTO
    for row in rows:
        processed_row = []
        for i, item in enumerate(row):
            text = str(item) if item is not None else ""
            
            # Corregir codificación de caracteres
            text = fix_encoding(text)
            
            # TRUNCAMIENTO MODIFICADO PARA MOSTRAR MÁS CONTENIDO
            # Perfil: 200 → 300 caracteres
            # Skills: 100 → 300 caracteres
            # Experiencia: 200 → 600 caracteres
            if i == 3:  # Perfil
                if len(text) > 300: text = text[:300] + "..."
            elif i == 4:  # Skills
                if len(text) > 300: text = text[:300] + "..."
            elif i == 5:  # Experiencia
                if len(text) > 600: text = text[:600] + "..."
                
            p = Paragraph(text, wrap_style)
            processed_row.append(p)
        data.append(processed_row)
    
    # Anchos de columna optimizados - AUMENTAMOS ESPECIALMENTE PARA EXPERIENCIA
    col_widths = [
        0.25 * inch,  # ID (más pequeño)
        0.75 * inch,  # Nombre
        1.0 * inch,   # Email
        1.5 * inch,   # Perfil
        1.5 * inch,   # Skills (aumentado)
        2.5 * inch,   # Experiencia (aumentado significativamente)
        0.7 * inch,   # Seniority
        1.2 * inch,   # Área
        0.5 * inch    # Match % (más pequeño)
    ]
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Estilo de la tabla ultra compacto
    table_style = TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 6),  # Fuente más pequeña
        ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
        
        # Filas de datos
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 1), (-1, -1), 6), # Fuente más pequeña
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        
        # Filas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        
        # Alineación específica para columnas
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID centrado
        ('ALIGN', (8, 1), (8, -1), 'CENTER'),  # Match % centrado
    ])
    
    table.setStyle(table_style)
    
    elements.append(table)
    
    # Pie de página compacto
    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=styles["Normal"],
        fontSize=6,
        alignment=1
    )
    elements.append(Spacer(1, 0.05 * inch))
    footer = Paragraph(f"Total de candidatos analizados: {len(rows)}", footer_style)
    elements.append(footer)
    
    # Generar PDF
    doc.build(elements)
    print(f"✅ PDF generado: {filename}")

if __name__ == "__main__":
    view_database()