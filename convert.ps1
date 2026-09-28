$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$workbook = $excel.Workbooks.Open("C:\Users\samy2\OneDrive\Escritorio\Escuela\Escuela\TECNM CLASES\9NO SEMESTRE\backend\templates\SCPM-05A.xls")
$workbook.SaveAs("C:\Users\samy2\OneDrive\Escritorio\Escuela\Escuela\TECNM CLASES\9NO SEMESTRE\backend\templates\SCPM-05A.xlsx", 51)
$workbook.Close()
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
