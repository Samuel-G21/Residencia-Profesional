import openpyxl
import os

template_path = "templates/SCPM-07.xlsx"

if os.path.exists(template_path):
    wb = openpyxl.load_workbook(template_path, data_only=True)
    for sheet_name in wb.sheetnames:
        print(f"Sheet: {sheet_name}")
        ws = wb[sheet_name]
        for row in ws.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    if "{{" in cell.value or "nombre_evento" in cell.value.lower():
                        print(f"({cell.row},{cell.column}): {cell.value}")
else:
    print("Template not found!")
