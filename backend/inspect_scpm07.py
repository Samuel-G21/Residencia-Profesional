import zipfile
import re

with zipfile.ZipFile('templates/SCPM-07.xlsx', 'r') as z:
    for filename in z.namelist():
        if filename.endswith('.xml'):
            content = z.read(filename).decode('utf-8')
            if 'lista_participantes' in content or '{' in content:
                print(f"File: {filename}")
                matches = re.findall(r'{[^}]+}', content)
                for m in set(matches):
                    print("  ", m)
