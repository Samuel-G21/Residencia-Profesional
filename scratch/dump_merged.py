import openpyxl

wb = openpyxl.load_workbook("backend/templates/SCPM-05A.xlsx")
ws = wb.active

for merged_range in ws.merged_cells.ranges:
    print(merged_range)
