import re

with open('frontend/src/pages/Generador.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update SCPM-05A.xls to SCPM-05A.xlsx
content = content.replace("'SCPM-05A.xls',", "'SCPM-05A.xlsx',")

# 2. Remove SIRCE from list
content = content.replace("  'SCPM-07.xlsx',\n  'SIRCE_Automatizado.xlsm'\n", "  'SCPM-07.xlsx'\n")

# 3. Remove modoSirce state
content = re.sub(r"  const \[modoSirce, setModoSirce\] = useState\('vacio'\);\n", "", content)

# 4. Remove modo_sirce append
content = re.sub(r"    formData\.append\('modo_sirce', modoSirce\);\n", "", content)

# 5. Remove SIRCE HTML block
sirce_html = """            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>4. SIRCE Automatizado (Modo de Generación):</label>
            <select id="modo_sirce_select" className="text-input" style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc', width: '100%', marginBottom: '1rem' }} value={modoSirce} onChange={(e) => setModoSirce(e.target.value)}>
              <option value="vacio">Descargar formato original en blanco (Recomendado)</option>
              <option value="con_datos">Generar e inyectar información de trabajadores</option>
            </select>\n"""
content = content.replace(sirce_html, "")

# 6. Change 5. Selecciona to 4. Selecciona
content = content.replace("5. Selecciona los documentos a generar:", "4. Selecciona los documentos a generar:")

with open('frontend/src/pages/Generador.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated Generador.tsx')
