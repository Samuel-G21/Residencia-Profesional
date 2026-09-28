import openpyxl
wb = openpyxl.load_workbook("test_out.xlsx", data_only=False)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                if "{{" in cell.value or "{%" in cell.value:
                    print(f"Row {cell.row}, Col {cell.column}: {cell.value}")
            if cell.value == "Alice" or cell.value == "Bob" or cell.value == "Charlie":
                print(f"Found participant at Row {cell.row}, Col {cell.column}: {cell.value}")
