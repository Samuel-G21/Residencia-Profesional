import openpyxl

filepath = 'templates/SCPM-07.xlsx'
wb = openpyxl.load_workbook(filepath, keep_vba=False)
ws = wb.worksheets[0]

for row in ws.iter_rows(min_row=29, max_row=32):
    for cell in row:
        if cell.value:
            print(f"{cell.coordinate}: {cell.value!r}")
