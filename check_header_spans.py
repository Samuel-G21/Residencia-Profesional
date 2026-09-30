import zipfile
import re

with zipfile.ZipFile("backend/templates/SCPM-05 2025.docx") as docx:
    xml = docx.read("word/document.xml").decode("utf-8")
    trs = re.findall(r"<w:tr[ >].*?</w:tr>", xml)
    for i, tr in enumerate(trs):
        tr_text = re.sub(r"<[^>]+>", "", tr)
        if "Ficha" in tr_text and "Nombre del participante" in tr_text:
            print(f"\nRow {i}")
            tcs = re.findall(r"<w:tc[ >].*?</w:tc>", tr)
            for j, tc in enumerate(tcs):
                text = re.sub(r"<[^>]+>", "", tc)
                grid_span = re.search(r"<w:gridSpan w:val=\"(\d+)\"", tc)
                span = grid_span.group(1) if grid_span else "1"
                print(f"Cell {j} (span {span}): {text}")
