import openpyxl

filepath = 'templates/SCPM-07.xlsx'
wb = openpyxl.load_workbook(filepath, keep_vba=False)
ws = wb.worksheets[0]

print("Merged cells:")
for merged in ws.merged_cells.ranges:
    if "30" in str(merged) or "31" in str(merged):
        print(merged)
