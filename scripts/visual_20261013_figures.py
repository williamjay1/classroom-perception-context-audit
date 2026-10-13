"""Presentation-only redesign from frozen, audited aggregate estimates.

SciencePlots science/nature styles; overridden only for the manuscript's actual
31-pica page width, fixed output canvas, and a 1200 dpi raster companion.
"""
from pathlib import Path
import os, sys, json, itertools
ROOT = Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR'] = str(ROOT/'temp/visual_20261013_mpl')
os.environ['TEMP'] = str(ROOT/'temp')
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import apply_house_style, audit, mm
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.lines import Line2D

plt = apply_house_style(fontsize=7)
plt.rcParams.update({
    'font.family':'sans-serif', 'font.sans-serif':['Arial','DejaVu Sans'],
    'mathtext.fontset':'dejavusans', 'axes.linewidth':0.5,
    'savefig.bbox':None, 'savefig.pad_inches':0,
    'axes.unicode_minus':True, 'text.color':'#222222',
    'xtick.direction':'out', 'ytick.direction':'out',
    'xtick.minor.visible':False, 'ytick.minor.visible':False,
    'xtick.top':False, 'ytick.right':False,
})
OUT=ROOT/'temp/visual_20261013_candidate/figures'
OUT.mkdir(parents=True,exist_ok=True)
QA=ROOT/'temp/visual_20261013_qa'; QA.mkdir(exist_ok=True)
WIDTH=31*12/72.27*25.4  # exactly 31 TeX picas, as in sn-jnl.cls
COLORS=['#252525','#0072B2','#D55E00','#687986']
MARKERS=['o','s','D']
results=json.loads((ROOT/'results/stats_verified_results.json').read_text(encoding='utf-8'))
records={}

def inspect_text(fig, texts, lines):
    fig.canvas.draw(); renderer=fig.canvas.get_renderer()
    boxes=[(t,t.get_window_extent(renderer)) for t in texts]
    overlaps=[]
    for (ta,a),(tb,b) in itertools.combinations(boxes,2):
        if a.overlaps(b): overlaps.append([ta.get_text(),tb.get_text()])
    outside=[]
    for t,b in boxes:
        if b.x0<0 or b.y0<0 or b.x1>fig.bbox.width or b.y1>fig.bbox.height:
            outside.append(t.get_text())
    collisions=[]
    for t,b in boxes:
        for ln in lines:
            path=ln.get_transform().transform_path(ln.get_path())
            if path.intersects_bbox(b.expanded(1.025,1.12),filled=False):
                collisions.append(t.get_text())
    return {'text_count':len(texts),'text_overlaps':overlaps,
            'text_outside_canvas':outside,'text_line_intersections':collisions,
            'minimum_font_pt':min(t.get_fontsize() for t in texts)}

def export(fig, name, texts, lines, data=None):
    style=audit(fig,max_width_mm=WIDTH,verbose=False)
    geometry=inspect_text(fig,texts,lines)
    assert style['ok'],style
    assert not geometry['text_overlaps'],geometry
    assert not geometry['text_outside_canvas'],geometry
    assert not geometry['text_line_intersections'],geometry
    for ext in ['pdf','svg','png']:
        fig.savefig(OUT/f'{name}.{ext}',dpi=1200,bbox_inches=None,pad_inches=0,
                    facecolor='white',metadata={'Creator':'Matplotlib / SciencePlots'} if ext=='pdf' else None)
    fig.savefig(QA/f'{name}_preview.png',dpi=250,bbox_inches=None,pad_inches=0)
    records[name]={'canvas_mm':[WIDTH,fig.get_figheight()*25.4],
                   'raster_dpi':1200,'style_audit':style,'geometry_audit':geometry,
                   'data':data}
    plt.close(fig)

# Figure 1: four estimands with matching visual grammar and no directional links.
fig=plt.figure(figsize=(mm(WIDTH),mm(91)))
texts=[]; lines=[]
def txt(x,y,s,**kw):
    obj=fig.text(x,y,s,ha='left',va='top',fontsize=7,**kw);texts.append(obj);return obj
panels=[
    ('a','Within class association',r'$\beta_{\mathrm{W}}$ for $X_{ig}-\bar{X}_{g}$',
     'Differences among students\nin the same class',0,0),
    ('b','Between class association',r'$\beta_{\mathrm{B}}$ for $\bar{X}_{g}$',
     'Differences among class means\nconditional on included\nschool terms',1,0),
    ('c','Contextual association\ncontrast',r'$\beta_{\mathrm{B}}-\beta_{\mathrm{W}}$',
     'A difference of outcome associations\ncomputed in the same model',0,1),
    ('d','Conditional classmates\nassociation',r'$c$ in $Y=aX+cC_{-i,g}+\ldots$',
     'Leave one student out sensitivity\nconditional on the focal report',1,1),
]
for idx,(letter,title,formula,note,col,row) in enumerate(panels):
    x=.014+col*.502; y=.524-row*.497; w=.468; h=.447
    box=Rectangle((x,y),w,h,transform=fig.transFigure,facecolor='white',
                  edgecolor='#C4C9CD',linewidth=.5)
    fig.add_artist(box)
    # Short coloured rule identifies the estimand, consistent with Figure 2.
    line=Line2D([x+.023,x+.112],[y+h-.021,y+h-.021],
                transform=fig.transFigure,color=COLORS[idx],lw=1)
    fig.add_artist(line);lines.append(line)
    txt(x+.023,y+h-.048,letter,fontweight='bold').set_fontsize(8)
    txt(x+.063,y+h-.048,title,fontweight='bold',linespacing=1.28).set_fontsize(7.6)
    txt(x+.025,y+.249,formula).set_fontsize(10 if idx!=3 else 8.6)
    txt(x+.025,y+.127,note,linespacing=1.36).set_fontsize(7)
export(fig,'Figure_1',texts,lines)

# Figure 2: independent forest panels; all number labels live outside the plot.
cp=next(m for m in results['CEPS']['models'] if m['label']=='primary_joint')
ep=next(m for m in results['ECLS']['models'] if m['label']==results['ECLS']['primary_model_label'])
fp=next(m for m in results['TIMSS']['FIN']['models'] if m['label']=='support_BSBGSSB')
def values(m,w,b,domain):
    return [m['terms'][w],m['terms'][b],m['contextual_associations'][domain]]
series=[
    ('CEPS','Negative affect',values(cp,'class_within','class_mean','class_support'),
     'Affect points per perception point',(-.35,.30),[-.3,0,.3]),
    ('ECLS K Grade 8','Internalizing problems',values(ep,'support_within','support_mean','support'),
     'Internalizing points per support point',(-.16,.16),[-.15,0,.15]),
    ('TIMSS Finland','School belonging',values(fp,'support_within','support_mean','support'),
     'Belonging scale points per instruction point',(-1,1.5),[-1,0,1]),
]
fig=plt.figure(figsize=(mm(WIDTH),mm(129)))
texts=[];lines=[];plot_records=[]
def sf(v): return f'{v:.3f}'.replace('-','−')
for i,(survey,outcome,vals,unit,xlim,ticks) in enumerate(series):
    top=.977-i*.326
    txt(.015,top,'abc'[i],fontweight='bold').set_fontsize(8)
    txt(.054,top,survey,fontweight='bold').set_fontsize(8)
    txt(.054,top-.027,outcome).set_fontsize(7)
    txt(.701,top-.037,'Estimate [95% CI]',fontweight='bold').set_fontsize(6.7)
    ax=fig.add_axes([.262,top-.239,.407,.165])
    ax.set_xlim(*xlim);ax.set_ylim(-.43,2.43)
    ax.set_yticks([]);ax.set_xticks(ticks)
    ax.set_xticklabels([('0' if t==0 else f'{t:g}'.replace('-','−')) for t in ticks])
    ax.tick_params(axis='x',labelsize=6.7,length=2.5,width=.5,pad=2.0,bottom=True,top=False)
    ax.spines[['left','right','top']].set_visible(False)
    ax.spines['bottom'].set_color('#6C7177');ax.spines['bottom'].set_linewidth(.5)
    zero=ax.axvline(0,color='#9CA4AA',lw=.5,ls=(0,(2.5,2.5)),zorder=1);lines.append(zero)
    for j,(label,v,color,marker) in enumerate(zip(['Within class','Between class','Between − within'],vals,COLORS,MARKERS)):
        y=2-j
        estimate,lo,hi=[v[k] for k in ['estimate','ci95_low','ci95_high']]
        eb=ax.errorbar(estimate,y,xerr=[[estimate-lo],[hi-estimate]],fmt=marker,
                      color=color,markersize=3.8,markeredgewidth=.5,
                      elinewidth=.85,capsize=2,capthick=.7,zorder=3)
        lines.extend(list(eb.lines[1]))
        # Check the horizontal interval explicitly along with all text bounds.
        checkline=Line2D([lo,hi],[y,y],transform=ax.transData)
        lines.append(checkline)
        fy=(top-.239)+.165*(y+.43)/2.86
        tt=fig.text(.015,fy,label,ha='left',va='center',fontsize=7);texts.append(tt)
        tt=fig.text(.701,fy,f'{sf(estimate)} [{sf(lo)}, {sf(hi)}]',ha='left',va='center',fontsize=6.8);texts.append(tt)
        plot_records.append({'survey':survey,'estimand':label,'estimate':estimate,'lower':lo,'upper':hi})
    ax.set_xlabel(unit,fontsize=6.8,labelpad=5)
    fig.canvas.draw()
    texts.extend(ax.get_xticklabels());texts.append(ax.xaxis.label)
    lines.append(ax.spines['bottom'])
    if i<2:
        sep=Line2D([.015,.985],[top-.307,top-.307],transform=fig.transFigure,color='#D9DDE0',lw=.5)
        fig.add_artist(sep);lines.append(sep)
export(fig,'Figure_2',texts,lines,plot_records)
(ROOT/'results/visual_20261013_figure_audit.json').write_text(json.dumps(records,indent=2,default=lambda x:x.item()),encoding='utf-8')
print(json.dumps({'output':str(OUT),'figures':{k:{'size_mm':v['canvas_mm'],'geometry':v['geometry_audit']} for k,v in records.items()}},indent=2))
