from pathlib import Path
import pymupdf as fitz,json,xml.etree.ElementTree as ET,hashlib,re
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'temp/visual_20261013_candidate';Q=ROOT/'temp/visual_20261013_qa'
result={}
for name in ['Figure_1','Figure_2']:
    p=fitz.open(D/'figures'/f'{name}.pdf');page=p[0]
    fonts=page.get_fonts(full=True)
    png=Image.open(D/'figures'/f'{name}.png')
    svg=ET.parse(D/'figures'/f'{name}.svg')
    record={'pdf_dimensions_mm':[float(page.rect.width)*25.4/72,float(page.rect.height)*25.4/72],
        'pdf_raster_image_count':len(page.get_images()),
        'pdf_vector_paths':len(page.get_drawings()),
        'fonts':[{'name':f[3],'type':f[2],'embedded_bytes':len(p.extract_font(f[0])[3])} for f in fonts],
        'svg_text_elements':len(svg.findall('.//{http://www.w3.org/2000/svg}text')),
        'png_pixels':list(png.size),'png_dpi':png.info.get('dpi'),
        'file_bytes':{e:(D/'figures'/f'{name}.{e}').stat().st_size for e in ['pdf','svg','png']}}
    assert record['pdf_raster_image_count']==0 and record['pdf_vector_paths']>0
    assert all(f['type']!='Type3' and f['embedded_bytes']>0 for f in record['fonts'])
    assert min(record['png_dpi'])>1199
    assert record['svg_text_elements']>0
    result[name]=record
for stem in ['manuscript','manuscript_marked']:
    pdf=fitz.open(D/f'{stem}.pdf')
    result[stem]={'pages':len(pdf),'blank_pages':[i+1 for i,p in enumerate(pdf) if len(p.get_text().strip())<10],
                 'fonts_type3':[f[3] for p in pdf for f in p.get_fonts() if f[2]=='Type3']}
    assert not result[stem]['blank_pages']
    thumbs=[]
    for i,p in enumerate(pdf):
        im=Image.frombytes('RGB',[p.get_pixmap(matrix=fitz.Matrix(.45,.45)).width,p.get_pixmap(matrix=fitz.Matrix(.45,.45)).height],p.get_pixmap(matrix=fitz.Matrix(.45,.45)).samples)
        canvas=Image.new('RGB',(280,410),'#eeeeee');im.thumbnail((270,380));canvas.paste(im,((280-im.width)//2,15));ImageDraw.Draw(canvas).text((10,392),str(i+1),fill='black');thumbs.append(canvas)
    sheet=Image.new('RGB',(7*280,3*410),'white')
    for i,im in enumerate(thumbs):sheet.paste(im,((i%7)*280,(i//7)*410))
    sheet.save(Q/f'{stem}_contact.png')
(ROOT/'results/visual_20261013_export_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
