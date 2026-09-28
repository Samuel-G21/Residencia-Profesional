import zipfile
import re

with zipfile.ZipFile('templates/SCPM-07.xlsx', 'r') as z:
    content = z.read('xl/sharedStrings.xml').decode('utf-8')
    print(content)
