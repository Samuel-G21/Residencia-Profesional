from jinja2 import Template
import re

strings = [
    "{{ nombre_evento }",
    "{% for participante in lista_participantes %}",
    "{{ficha_supervisor}",
    "{% tr %}",
    "{{nombre_supervisor}",
    "{{ participante.ficha }",
    "{% endfor %}",
    "{{ paticipante.nombe_completo }"
]

lista_participantes = [
    {"ficha": "123", "nombre_completo": "Juan Perez", "nombre_trabajador": "Juan Perez", "calificacion": 90},
    {"ficha": "456", "nombre_completo": "Maria Lopez", "nombre_trabajador": "Maria Lopez", "calificacion": 100}
]

data = {
    "clave_evento": "E-001",
    "nombre_evento": "Curso Seguridad",
    "lista_participantes": lista_participantes
}

# Fix missing closing brace manually as if openpyxl was parsing correctly 
# (assuming it's a bug in how we extracted it, they likely have proper braces in excel)
# Actually let's assume they are proper Jinja strings:
strings = [
    "{{ nombre_evento }}",
    "{% for participante in lista_participantes %}",
    "{{ficha_supervisor}}",
    "{% tr %}",
    "{{nombre_supervisor}}",
    "{{ participante.ficha }}",
    "{% endfor %}",
    "{{ paticipante.nombe_completo }}"
]

for val in strings:
    original = val
    # Prior worker's logic:
    val = val.replace('{% tr %}', '')
    val = val.replace('paticipante.nombe_completo', 'participante.nombre_completo')
    val = val.replace('{% for participante in lista_participantes %}', '')
    val = val.replace('{% endfor %}', '')
    
    # Render with row_data
    row_data = data.copy()
    row_data['participante'] = lista_participantes[0]
    
    try:
        if val.strip() != '':
            res = Template(val).render(row_data)
            print(f"'{original}' -> '{res}'")
        else:
            print(f"'{original}' -> (empty string after replace)")
    except Exception as e:
        print(f"Error on '{original}': {e}")
