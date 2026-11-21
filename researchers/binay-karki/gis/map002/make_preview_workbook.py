#!/usr/bin/env python3
"""Create Google Sheets-ready native-convertible MAP-002 workbook with artifact_tool."""
from __future__ import annotations
import csv, json, hashlib, math
from pathlib import Path
from artifact_tool import Workbook,SpreadsheetFile
root=Path(__file__).resolve().parent
out=root/'BINAY_MAP002_DATA_PREVIEW_FIELD_GEE_AND_V10.xlsx'
wb=Workbook.create()
NAVY='#20384E'; TEAL='#167D87'; SILVER='#E9EEF3'; WHITE='#FFFFFF'; RED='#B23E36'

def add(name,rows,widths=None):
    s=wb.worksheets.add(name)
    if not rows:return s
    w=max(map(len,rows)); rr=[list(row)+[None]*(w-len(row)) for row in rows]
    s.get_range_by_indexes(0,0,len(rr),w).values=rr
    s.get_range_by_indexes(0,0,1,w).format={'fill':NAVY,'font':{'bold':True,'color':WHITE},'row_height':28,'vertical_alignment':'center'}
    s.freeze_panes.freeze_rows(1)
    for col,ww in enumerate(widths or []):
        s.get_range_by_indexes(0,col,len(rr),1).format.column_width=ww
    # muted banding to ease scanning; skip thousands of cell edits
    return s

pclasses=json.loads((root/'MAP002_source_QA_receipt.json').read_text())
stats=pclasses['satellite_coverage']
sources=[
 ('manual_obs','SOURCE_LIVE_DATA_EXPORT_20260825_PRE_DATA.csv','1PGo2M4RM4HzKx5dWaZGfHzhER6tbEh6C','47 dates, 202 observation rows','2026','Raw 202 dates/times, not all used in R8 field MAP002'),
 ('mapped_field','r8_wards_joined_temperature_metrics.geojson','1xJtgZnG0mcdGEFSWfpqAa7y9YYec_36E','3 ward-level R8 means','2026','MAP002 field figure exact source; controlled 44 date / 186 event scope'),
 ('municipality','Pokhara Lekhnath NepalDD source shapefile ZIP','1OofaW0cP7UxvdFE-awBIWEMAvXIg_kjZ',f"{stats['municipal_area_km2']:.3f} km² transformed","historical","Rupesh project source, not certified current boundary"),
 ('satellite_wet','BINAY_GEE_V05_WET_SEASON_LST_MEDIAN_CANDIDATE_NODATA_FIXED_V05_20260918_R02.tif','1djjbRqPqDbZDsIETgVi2zUBFRP5kDZuC','30m grid / 106301 valid cells inside municipal polygon','2026','20.57% citywide municipality coverage, not full city'),
 ('all_valid_pixels_csv','BINAY_MAP002_ALL_VALID_GEE_WET_PIXELS_INSIDE_POKHARA_106301.csv','1aS96z9FkASa7PE5jMG5DWDx1ziQimt8g','106301 valid observed pixel records','2026','Complete pixel ledger inside city boundary, not a satellite replacement'),
 ('GEE_V10_matrix','BINAY_GEE_V10_RESEARCHER_REVIEW_AND_EVIDENCE_ADMISSION_MATRIX__LIVE_v1.0','1S59v06JAAaZLYKCNLsrosmsqBzsGWTFoAHY7HG35EMg','15 claims and 7 figure review entries','2026','AI dispositions in audit only; researcher matrix left unchanged')
]
rows=[['MAP002 - preview guide','Meaning / status','Link / action'],
 ['Version','MAP002_20261121 — real GIS, not image-generation output',''],
 ['Field map','Measured W6,W8,W16 ward means, R8 44 dates / 186 events',''],
 ['Satellite map','GEE V05 preserved wet median, 106301 valid municipal pixels, 30 m',''],
 ['Citywide coverage',f"{stats['municipal_valid_cell_area_pct_est']:.2f}% of historical municipality has valid original GEE TIFF pixels",'NO CITYWIDE EXPORT HAS RUN'],
 ['Municipality polygon','Rupesh historical Pokhara Lekhnath shapefile transformed to EPSG:32644','Not certified official 2026 ward boundaries'],
 ['All-pixel ledger','The complete 106301 pixel rows are in an external CSV, not a limited spreadsheet sample','https://drive.google.com/file/d/1aS96z9FkASa7PE5jMG5DWDx1ziQimt8g/view'],
 ['Raw observations','Field_Raw_202 tab preserves all 202 nonempty source event rows',''],
 ['Mapped values','Field_R8_Mapped contains all 6 metrics for 3 wards, including unplotted fields',''],
 ['Pixel sample','Wet_Pixel_Sample contains 600 deterministic evenly-spaced pixels (full ledger separate)',''],
 ['8-colour classes','GEE_Class_Counts reports exact bins from the satellite LST GeoTIFF',''],
 ['V10 evidence','V10_AI_Dispositions contains 22 independent AI appraisals; no false author sign-off',''],
 ['Full city GEE export','New Landsat 8/9 collection export script is prepared; requires authenticated GEE project',''],
 ['Scientific status','Technical review, not final submission or approved V10',''],
]
add('START_HERE',rows,[28,68,80])

geodata=json.loads(Path('/mnt/data/r8_wards_joined_temperature_metrics.geojson').read_text())
wd=[['Ward','Location','Air_1p5m_14_C','Air_1p5m_18p30_C','GST_14_C','Air_0p1m_14_C','Air_0p1m_18p30_C','GST_18p30_C','Cooling_metric','Source_scope','Source_GeoJSON']]
loc={6:'Lakeside',8:'New Road',16:'Armala'}
for f in sorted(geodata['features'],key=lambda f:f['properties']['ward_no']):
 p=f['properties'];i=p['ward_no'];wd.append([i,loc[i]]+[round(float(p[k]),6) for k in ['air15_1400','air15_1830','gst_1400','air01_1400','air01_1830','gst_1830','cool15']]+['R8 44 dates / 186 events','https://drive.google.com/file/d/1xJtgZnG0mcdGEFSWfpqAa7y9YYec_36E/view'])
add('Field_R8_Mapped',wd,[9,18,19,19,17,20,20,17,17,29,72])

raw_path=Path('/mnt/data/SOURCE_LIVE_DATA_EXPORT_20260825_PRE_DATA.csv')
with raw_path.open(newline='',encoding='utf-8-sig') as fp: raw=list(csv.reader(fp))
headers=['Original_source_row','Date_literal','Time_literal','W16_GST_C','W16_Air0p1_C','W16_Air1p5_C','W06_GST_C','W06_Air0p1_C','W06_Air1p5_C','W08_GST_C','W08_Air0p1_C','W08_Air1p5_C']
rawrows=[headers]
for source_row,row in enumerate(raw[2:],start=3):
 if not row or not row[0].strip():continue
 line=[source_row, row[0].strip(),row[1].strip()]
 for k in range(2,11):
  cell=row[k].strip() if k<len(row) else ''
  if cell:
   try:line.append(float(cell))
   except:line.append(cell)
  else:line.append(None)
 rawrows.append(line)
assert len(rawrows)==203,(len(rawrows),rawrows[:3])
add('Field_Raw_202',rawrows,[19,16,18]+[16]*9)

colors=pclasses['palette_hex']; edges=['≤5','>5 to ≤10','>10 to ≤15','>15 to ≤20','>20 to ≤25','>25 to ≤30','>30 to ≤35','>35']
nvalid=stats['raster_cells_valid_inside_municipality']
cls=[['Class_index','Temperature_interval_C','HEX','Valid_Pixels_inside_city','Pct_of_valid_pixels','Area_km2_30m_cell_est','Source_info']]
for i,(nm,hx,n) in enumerate(zip(edges,colors,stats['counts_inside_municipality']),start=1):
 cls.append([i,nm,hx,int(n),round(n/nvalid*100,3),round(n*.0009,4),'GEE V05 median | valid inside municipality only'])
cls.append(['TOTAL','all valid classes','',nvalid,100,round(nvalid*.0009,4),'Municipal area ≈465.056 km²; valid pixel ≈20.572%'])
add('GEE_Class_Counts',cls,[17,26,17,25,23,26,63])

pixels=root/'BINAY_MAP002_ALL_VALID_GEE_WET_PIXELS_INSIDE_POKHARA_106301.csv'
with pixels.open(newline='',encoding='utf-8') as fp: rr=list(csv.reader(fp))
sample=[rr[0]]
# evenly spaced by row in fixed coordinate scan order (NOT a random statistical sample)
for i in range(0,len(rr)-1,max(1,(len(rr)-1)//600)):
 row=rr[i+1]
 sample.append([int(row[0]),int(row[1]),*map(float,row[2:7]),int(row[7]),row[8]])
 if len(sample)==601:break
add('Wet_Pixel_Sample',sample,[24,24,22,22,21,21,20,18,32])

sp=[['Type','Exact_source_label','Google_Drive_ID','Scope','Year','Caution','Link']]
for role,name,id,scope,yr,caveat in sources:
 link=('https://docs.google.com/spreadsheets/d/'+id+'/edit') if role=='GEE_V10_matrix' else 'https://drive.google.com/file/d/'+id+'/view'
 sp.append([role,name,id,scope,yr,caveat,link])
sp.append(['Rupesh code','RMP_GIS_V02_4_THESIS_WARD_PLATE.py','GitHub SHA 3348903030a1e7d112350a839b3245383f15de3b','Cartesian map framing / historical context','2026','Source controlled, reuse style not Rupesh survey values','https://github.com/FabinGurung/jp-research-lab/blob/main/researchers/rupesh-man-pradhan/gis/RMP_GIS_V02_4_THESIS_WARD_PLATE.py'])
sp.append(['USGS','Landsat Collection 2 Surface Temperature','Public reference','ST_B10 physical meaning and conversion','public','LST ≠ air','https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature'])
add('Source_Provenance',sp,[24,64,62,48,14,66,84])

review=json.loads((root/'V10_22_AI_EVIDENCE_DISPOSITIONS.json').read_text())
ref=review['external_references']
a=[['V10_ID','AI_EVIDENCE_DISPOSITION','Methodological_reason_and_limit','External_reference','Official_researcher_review_state']]
for d in review['decisions']:
 a.append([d['id'],d['disposition'],d['reason'],ref[d['ref']],'PENDING_RESEARCHER_REVIEW — no impersonation'])
add('V10_AI_Dispositions',a,[15,23,98,90,55])

gate=[['Check','Actual_result','Status','Responsible_record'],
      ['Current municipality boundary',f"Historical RMP admin polygon, {stats['municipal_area_km2']:.3f} km²",'VERIFIED AS HISTORICAL; NOT OFFICIAL 2026','Rupesh original shapefile ZIP'],
      ['Existing wet raster','30 m; 278 rows × 411 columns; EPSG:32644','EXISTS',sources[3][2]],
      ['Valid municipal pixels',str(nvalid),'EXISTS','Full pixel CSV'],
      ['Valid municipal coverage',f"{stats['municipal_valid_cell_area_pct_est']:.3f}% of municipality",'INCOMPLETE','Geometric mask with historical municipal polygon'],
      ['Genuinely full citywide wet raster','No authenticated GEE runtime available in this run','NOT GENERATED','export_full_city_wet_GEE_AUTH_REQUIRED.py'],
      ['GEE scene selection','Landsat8/9 C02 L2SP, 2026-05-31 to 2026-08-01 exclusive is a newly proposed acquisition rule','NEEDS SCIENTIFIC COMPARABILITY REVIEW','USGS + GEE catalog'],
      ['Class indexing','<=5,5–10,10–15,15–20,20–25,25–30,30–35,>35; original color order','IMPLEMENTED','Map script + original user sample'],
      ['Field observation source','R8 ward aggregated metrics reflect 44 dates / 186 events','IMPLEMENTED','Field_R8_Mapped tab'],
      ['Full broad manual CSV','47 dates / 202 event rows, not auto-admitted as R8','PRESERVED','Field_Raw_202 tab'],
      ['22 claim/figure appraisals','All 22 AI outcomes classified, official V10 untouched','AI EVIDENCE REVIEW COMPLETE; RESEARCHER SIGNOFF OPEN','V10_AI_Dispositions tab']]
add('Export_and_QA_Gate',gate,[32,72,42,77])

print('Sheets ready',len(rawrows)-1,len(sample)-1,len(a)-1)
try:
 print('Preview',wb.inspect({'kind':'table','range':'GEE_Class_Counts!A1:G9','include':'values','table_max_rows':10,'table_max_cols':7}).ndjson[:1000])
except Exception as e:print('Preview inspect issue',str(e)[:250])
SpreadsheetFile.export_xlsx(wb).save(str(out))
print('EXPORTED',out,'bytes',out.stat().st_size,'sha256',hashlib.sha256(out.read_bytes()).hexdigest())
