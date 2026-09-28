import openpyxl

wb = openpyxl.load_workbook("backend/templates/SCPM-05A.xlsx")
ws = wb.active
for row in range(8, 12):
    for col in range(1, 16):
        cell = ws.cell(row=row, column=col)
        val = cell.value
        print(f"{cell.coordinate}: {repr(val)}")
