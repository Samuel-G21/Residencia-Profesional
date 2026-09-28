import openpyxl

wb = openpyxl.load_workbook("backend/templates/SCPM-05A.xlsx")
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                val = cell.value.strip()
                if val:
                    print(f"{cell.coordinate}: {val[:50]}")
