#!/usr/bin/env python3
"""Build a private modular research experiment from verified Doc and Sheet reads."""
import argparse,json
from pathlib import Path

def tex(value):
    replacements={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(replacements.get(c,c) for c in str(value))

def build(academic,results,out):
    out.mkdir(parents=True,exist_ok=True); (out/'chapters').mkdir(exist_ok=True)
    (out/'main.tex').write_text(r'''\documentclass[12pt,a4paper]{report}
\usepackage{pumlsc-shared}
\begin{document}
\input{title}
\PUStartMainBody
\input{chapters/01_objectives}
\input{chapters/02_methodology}
\input{chapters/03_results}
\input{chapters/04_discussion}
\end{document}
''')
    (out/'title.tex').write_text('\\begin{titlepage}\n\\centering\n{\\Large\\bfseries '+tex(academic['title'])+'\\par}\n\\vspace{2cm}\nFabin Gurung\\par\n\\vfill\nFour-workflow research experiment\\par\n\\end{titlepage}\n')
    objectives='\\chapter{Research Objectives}\n\\section{General Objective}\n'+tex(academic['general_objective'])+'\n\\section{Specific Objectives}\n\\begin{enumerate}\n'+''.join('\\item '+tex(x)+'\n' for x in academic['specific_objectives'])+'\\end{enumerate}\n'
    (out/'chapters/01_objectives.tex').write_text(objectives)
    (out/'chapters/02_methodology.tex').write_text('\\chapter{Methodology}\n'+'\n\n'.join(map(tex,academic['methodology']))+'\n')
    r=results;a=r['analysis']; lines=[r'\chapter{Results of the Controlled Example}',
        'The generated example contains four columns, four perimeter beams and one slab. The following values are derived from the same parameter revision.',
        r'\section{Concrete Quantities}',r'\begin{tabular}{lrr}',r'\toprule Element & Volume (m$^3$) & Concrete cost (NPR) \\',r'\midrule']
    for q in r['quantities']:lines.append(tex(q['element'])+' & '+f"{q['quantity']:.3f}"+' & '+f"{q['amount']:,.2f}"+r' \\')
    lines += [r'\midrule',f"Total & {r['concrete_m3']:.3f} & {r['concrete_subtotal_npr']:,.2f}"+r' \\',r'\bottomrule',r'\end{tabular}',
        r'\section{Gravity Response}',f"The applied gravity load including column selfweight is {a['total_load_kN']:.3f} kN. Each column base reaction is {a['base_reaction_each_kN']:.4f} kN under symmetric loading.",
        f"The X-direction beam fixed-end moment magnitude is {a['x']['fixed_end_magnitude_kNm']:.4f} kNm. Moment distribution converges in {a['x']['iterations']} sweeps to beam end moments of {a['x']['beam_I_kNm']:.4f} and {a['x']['beam_J_kNm']:.4f} kNm, with clockwise end actions taken as positive. The corresponding midspan sagging moment is {a['x']['midspan_sagging_kNm']:.4f} kNm.",
        r'\section{Construction Sequence}',f"The illustrative single-crew sequence runs from {tex(r['schedule']['origin_date'])} to {tex(r['schedule']['finish_date'])}. Active work excludes Saturdays and the two curing waits use calendar days. Curing durations are assumptions and do not establish stripping or strength acceptance.",
        r'\section{Cross-workflow Reuse}', 'The same column, beam and slab identifiers appear in the schematic, structural calculations, activity scopes and quantity records. The concrete subtotal excludes reinforcement, formwork, foundations, services, overhead, tax and other building work.']
    (out/'chapters/03_results.tex').write_text('\n\n'.join(lines)+'\n')
    (out/'chapters/04_discussion.tex').write_text('\\chapter{Discussion and Limitations}\n'+'\n\n'.join(map(tex,academic['limitations']))+'\n')
    (out/'README.md').write_text('''# Four-workflow modular experiment

Owner: Fabin Gurung. This is a separate controlled example, not a replacement for the existing thesis.

Compile main.tex only using XeLaTeX. Resolve the one existing shared style through TEXINPUTS:

    TEXINPUTS=/path/to/jp-research-lab/controls/latex/template//: xelatex -halt-on-error main.tex

The shared style is v2.6.4, Git blob 6deb30ec415fd386de104c0b7248eb9ea8b98ece. It is not copied into this folder. Exact Times New Roman is required by that style. If only Tinos is available, an explicitly enabled preview is separate from production formatting acceptance.

Title and objectives were preserved from the live owner source. Narrative is supplied by the experiment Google Doc; numerical results are generated from its companion master Google Sheet. Outputs and review evidence remain separate.
''')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--academic',type=Path,required=True);p.add_argument('--results',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();build(json.loads(a.academic.read_text()),json.loads(a.results.read_text()),a.out)
