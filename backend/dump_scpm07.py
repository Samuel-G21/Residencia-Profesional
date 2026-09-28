import openpyxl

filepath = 'templates/SCPM-07.xlsx'
wb = openpyxl.load_workbook(filepath, keep_vba=False)

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and '{' in cell.value:
                print(f"{cell.coordinate}: {cell.value!r}")
