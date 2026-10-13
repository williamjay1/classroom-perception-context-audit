"""Displayed-value audit for the revised manuscript and Additional file 1.

One counting rule is applied to tables and to continuous text alike:
a numeric token is a run of digits, with an optional decimal part, that is not
part of a word or of an identifier such as a variable name (for example the
digits inside C7SDQINT or IS4G16A are not counted).
"""
import json, re, sys
from pathlib import Path
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'deliverables'
TOKEN = re.compile(r'(?<![\w.])\d+(?:\.\d+)?(?![\w])')

def blocks(doc):
    for ch in doc.element.body.iterchildren():
        if ch.tag == qn('w:p'):
            yield Paragraph(ch, doc)
        elif ch.tag == qn('w:tbl'):
            yield Table(ch, doc)

def audit(path):
    doc = Document(path)
    tables = cells = table_values = text_values = 0
    for b in blocks(doc):
        if isinstance(b, Table):
            tables += 1
            for row in b.rows:
                for c in row.cells:
                    found = TOKEN.findall(c.text)
                    if found:
                        cells += 1
                        table_values += len(found)
        else:
            text_values += len(TOKEN.findall(b.text))
    return dict(file=Path(path).name, tables=tables, numeric_cells=cells,
                numeric_values_in_tables=table_values, numeric_values_in_text=text_values)

main = audit(OUT/'BMC_Psychology_revised_manuscript.docx')
supp = audit(OUT/'Additional_file_1_Supplementary_methods_and_results.docx')
report = {
  'tokenizer_rule': r'(?<![\w.])\d+(?:\.\d+)?(?![\w])  i.e. digit runs not embedded in a word or identifier, optional decimal part',
  'scope': 'revised manuscript and Additional file 1; headings, notes and captions included; the archive package, cover letter and response letter excluded',
  'documents': [main, supp],
  'totals': {
     'tables': main['tables'] + supp['tables'],
     'numeric_cells': main['numeric_cells'] + supp['numeric_cells'],
     'numeric_values_in_tables': main['numeric_values_in_tables'] + supp['numeric_values_in_tables'],
     'numeric_values_in_text': main['numeric_values_in_text'] + supp['numeric_values_in_text'],
  },
  'supersedes': 'results/round2_numeric_audit.json, which described the earlier document build (606 cells, 1093 values, 17 tables) under a different cell-scope rule',
}
(ROOT/'results/round3_displayed_value_audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report['totals'], indent=2))
