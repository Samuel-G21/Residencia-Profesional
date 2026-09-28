import sys
sys.path.append('.')
from jinja2 import Template

row_data = {
    'participante': {'ficha': '12345', 'nombre_completo': 'Juan Perez'}
}

val = "{% tr %}{% for participante in lista_participantes %}{{ participante.ficha }}"
val = val.replace('{% tr %}', '')
val = val.replace('paticipante.nombe_completo', 'participante.nombre_completo')
val = val.replace('{% for participante in lista_participantes %}', '')
val = val.replace('{% endfor %}', '')

print("Template string:", val)
print("Rendered:", Template(val).render(row_data))
