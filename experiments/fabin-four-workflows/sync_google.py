#!/usr/bin/env python3
"""Read the experiment's already link-readable synthetic Google sources."""
import csv, hashlib, io, json, os, re, urllib.request
from pathlib import Path
from datetime import datetime, timezone
from engine import parse_rows, digest

ROOT=Path(__file__).resolve().parent
HEADINGS=['Title','General objective','Specific objectives','Methodology','Limitations']

def flatten(doc):
    def walk(items):
        for item in items:
            if 'paragraph' in item:
                for e in item['paragraph'].get('elements',[]):
                    if 'textRun' in e: yield e['textRun']['content']
            for row in item.get('table',{}).get('tableRows',[]):
                for cell in row.get('tableCells',[]): yield from walk(cell.get('content',[]))
    tabs=doc.get('tabs',[])
    if len(tabs)!=1 or tabs[0].get('childTabs'): raise ValueError('Academic source must contain exactly one tab')
    tab=tabs[0].get('documentTab',tabs[0])
    return ''.join(walk(tab.get('body',{}).get('content',[])))

def academic_sections(text):
    out={}; current=None
    for line in text.lstrip('\ufeff').splitlines():
        if line.strip() in HEADINGS:
            current=line.strip()
            if current in out: raise ValueError('Duplicate academic heading')
            out[current]=[]
        elif current: out[current].append(line)
    if set(out)!=set(HEADINGS): raise ValueError('Missing required academic headings')
    out={k:'\n'.join(v).strip() for k,v in out.items()}
    if any(not v for v in out.values()): raise ValueError('Empty academic section')
    objectives=[re.sub(r'^\s*\d+[.)]\s*','',x).strip() for x in out['Specific objectives'].splitlines() if x.strip()]
    if len(objectives)!=7: raise ValueError('Expected seven retained specific objectives')
    return {'title':out['Title'],'general_objective':out['General objective'],
        'specific_objectives':objectives,
        'methodology':[x.strip() for x in re.split(r'\n\s*\n',out['Methodology']) if x.strip()],
        'limitations':[x.strip() for x in re.split(r'\n\s*\n',out['Limitations']) if x.strip()]}

def read_export(url,kind):
    if not url.startswith('https://docs.google.com/'): raise ValueError('Only native Google export sources are allowed')
    request=urllib.request.Request(url,headers={'Cache-Control':'no-cache'})
    with urllib.request.urlopen(request,timeout=30) as response:
        payload=response.read(512001)
        if response.status!=200 or len(payload)>512000: raise ValueError('Source export failed or exceeded bounded size')
        if kind not in response.headers.get('Content-Type',''): raise ValueError('Source is not a readable native export')
    return payload

def main():
    config=json.loads((ROOT/'google-sources.json').read_text())
    # These NEW synthetic documents already inherited link-reader access in Drive.
    # No sharing grant, token, credential or permission mutation is performed.
    first=[read_export(config['sheet_csv_url'],'text/csv'),read_export(config['academic_txt_url'],'text/plain')]
    second=[read_export(config['sheet_csv_url'],'text/csv'),read_export(config['academic_txt_url'],'text/plain')]
    if first!=second: raise ValueError('Source exports changed during read; retry the complete refresh')
    rows=list(csv.reader(io.StringIO(first[0].decode('utf-8-sig'))))
    parameters=parse_rows(rows[:28])
    academic=academic_sections(first[1].decode('utf-8-sig'))
    work=Path(os.environ.get('FABIN_PRIVATE_WORK_DIR','/tmp/fabin-experiment-private'));work.mkdir(parents=True,exist_ok=True)
    (work/'academic.json').write_text(json.dumps(academic,ensure_ascii=False,indent=2))
    snapshot={'parameters':parameters,'provenance':{'source_mode':'google_link_read_exports',
        'read_at':datetime.now(timezone.utc).isoformat(),'input_sha256':digest(parameters),
        'academic_sha256':digest(academic),'source_version_checked':False,'source_payload_repeat_check':True,
        'sheet_export_sha256':hashlib.sha256(first[0]).hexdigest(),'academic_export_sha256':hashlib.sha256(first[1]).hexdigest(),
        'note':'Two identical bounded export reads. Native revision identifiers are not available through link-based exports.'}}
    (ROOT/'source-snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n')
    print('GOOGLE_SOURCE_READ_PASS: one native Sheet, one native Doc, repeated payload consistency, typed units and seven objectives. No source writes.')

if __name__=='__main__':main()
