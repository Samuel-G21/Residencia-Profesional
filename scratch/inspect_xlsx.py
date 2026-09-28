import openpyxl

wb = openpyxl.load_workbook("backend/templates/SCPM-05A.xlsx")
found_jinja = False
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and "{{" in cell.value:
                print(f"Sheet {ws.title}, Cell {cell.coordinate}: {cell.value}")
                found_jinja = True

if not found_jinja:
    print("No Jinja tags found in SCPM-05A.xlsx")
