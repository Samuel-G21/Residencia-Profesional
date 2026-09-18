import os
import zipfile
import io
import re
from flask import request, jsonify

def upload_template():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No se subió ningún archivo"}), 400
    
    file = request.files['file']
    if not file.filename.endswith('.docx'):
        return jsonify({"status": "error", "message": "Solo se permiten archivos .docx"}), 400

    filename = file.filename
    # Define mapping from simple tags to jinja tags
    tag_mapping = {
        '[FICHA]': '{{ ficha }}',
        '[APELLIDO_PATERNO]': '{{ apellido_paterno }}',
        '[APELLIDO_MATERNO]': '{{ apellido_materno }}',
        '[NOMBRE]': '{{ nombre }}',
        '[NOMBRE_COMPLETO]': '{{ nombre_completo }}',
        '[CURP]': '{{ curp }}',
        '[NOMBRE_EVENTO]': '{{ nombre_evento }}',
        '[CLAVE_EVENTO]': '{{ clave_evento }}',
        '[DURACION]': '{{ duracion }}',
        '[NOMBRE_INSTRUCTOR]': '{{ nombre_instructor }}',
        '[FICHA_INSTRUCTOR]': '{{ ficha_instructor }}',
        '[FECHA_INICIO]': '{{ fecha_inicio }}',
        '[FECHA_TERMINO]': '{{ fecha_termino }}',
        '[DIA_INICIO]': '{{ dia_inicio }}',
        '[MES_INICIO]': '{{ mes_inicio }}',
        '[ANIO_INICIO]': '{{ anio_inicio }}',
        '[DIA_TERMINO]': '{{ dia_termino }}',
        '[MES_TERMINO]': '{{ mes_termino }}',
        '[ANIO_TERMINO]': '{{ anio_termino }}',
        '[CATEGORIA]': '{{ categoria }}',
        '[NIVEL]': '{{ nivel }}',
        '[DEPARTAMENTO]': '{{ departamento }}',
        '[TIPO_CURSO]': '{{ tipo_curso }}',
    }

    def replace_tags(xml_str):
        # A simple replace works for tags not split across runs
        for simple_tag, jinja_tag in tag_mapping.items():
            xml_str = xml_str.replace(simple_tag, jinja_tag)
        
        # A more robust regex to handle split tags in XML:
        # e.g. [</w:t></w:r><w:r><w:t>NOMBRE_EVENTO</w:t></w:r><w:r><w:t>]
        # We find all matches of the simple tag ignoring XML tags between letters
        for simple_tag, jinja_tag in tag_mapping.items():
            pattern_str = ''
            for char in simple_tag:
                if char == '[':
                    pattern_str += r'\[(?:<[^>]+>)*'
                elif char == ']':
                    pattern_str += r'\]'
                else:
                    pattern_str += re.escape(char) + r'(?:<[^>]+>)*'
            
            def repl(match, jt=jinja_tag):
                m_str = match.group(0)
                parts = re.split(r'(<[^>]+>)', m_str)
                first_text_idx = -1
                for i in range(0, len(parts), 2):
                    if parts[i]:
                        if first_text_idx == -1:
                            first_text_idx = i
                        parts[i] = ""
                
                if first_text_idx != -1:
                    parts[first_text_idx] = jt
                else:
                    parts[0] = jt
                    
                return "".join(parts)

            xml_str = re.sub(pattern_str, repl, xml_str)

        return xml_str

    try:
        # Read the docx file as a zip
        file_bytes = file.read()
        
        # We will process the XML directly to replace the simple tags with jinja tags
        out_bytes = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zin:
            with zipfile.ZipFile(out_bytes, 'w') as zout:
                for item in zin.infolist():
                    content = zin.read(item.filename)
                    if item.filename.endswith('.xml') and (item.filename.startswith('word/document') or item.filename.startswith('word/header') or item.filename.startswith('word/footer')):
                        xml_str = content.decode('utf-8')
                        xml_str = replace_tags(xml_str)
                        content = xml_str.encode('utf-8')
                    zout.writestr(item, content)
        
        out_bytes.seek(0)
        
        # Save the new template in templates directory
        # The frontend expects them in backend/templates
        templates_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        save_path = os.path.join(templates_dir, filename)
        
        with open(save_path, 'wb') as f:
            f.write(out_bytes.read())
            
        return jsonify({"status": "success", "message": f"Plantilla '{filename}' procesada y guardada exitosamente."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al procesar la plantilla: {str(e)}"}), 500
