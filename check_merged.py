import openpyxl
wb = openpyxl.load_workbook("backend/templates/SCPM-07.xlsx")
ws = wb.active
for rng in ws.merged_cells.ranges:
    if 28 <= rng.min_row <= 32:
        print(f"Merged range: {rng}")
