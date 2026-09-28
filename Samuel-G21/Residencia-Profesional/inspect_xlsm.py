import zipfile
import xml.etree.ElementTree as ET
import os

try:
    z = zipfile.ZipFile('D:\\BASE PLANTILLA SIRCE_Automatizado.xlsm')
    with z.open('xl/workbook.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        namespaces = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        sheets = root.findall('.//ns:sheet', namespaces)
        print('Sheets:')
        for sheet in sheets:
            print(f"- {sheet.attrib.get('name')}")
except Exception as e:
    print(f"Error: {e}")
