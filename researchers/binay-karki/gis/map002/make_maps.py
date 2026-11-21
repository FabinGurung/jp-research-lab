#!/usr/bin/env python3
"""Binay MAP-002: reproducible, data-driven publication CARTOGRAPHY (not AI art).

Input authority:
 - original R8 ward-joined field GeoJSON (3 ward geometries and 6 metric columns)
 - RMP historical municipality administrative polygon, stored as a transformed
   WGS84 GeoJSON from the untouched NepalDD/Everest shapefile ZIP
 - Binay GEE V05 R02 30 m wet-season median LST GeoTIFF

IMPORTANT: The existing satellite TIFF covers ~20.6% of the municipality.
No extrapolation, padding, fabricated Landsat scene or synthetic thermal pixel is made.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask,shapes
from shapely.geometry import shape,mapping,Polygon,MultiPolygon
from shapely.ops import transform
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.patches import PathPatch,Rectangle,Polygon as MplPolygon, Circle
from matplotlib.path import Path as MplPath
from pyproj import Transformer
from matplotlib.backends.backend_pdf import PdfPages

# Same class order and approximately the same eight HEX swatches as the user image.
PALETTE=['#2B073D','#446FE6','#22C9CD','#50ED67','#D8E83A','#FFA02B','#E04510','#860300']
EDGES=[-np.inf,5,10,15,20,25,30,35,np.inf]
CLASS_NAMES=['≤ 5','5–10','10–15','15–20','20–25','25–30','30–35','> 35']
FIELD_METRICS=[('air15_1400','Air at 1.5 m · 14:00'),('air15_1830','Air at 1.5 m · 18:30'),('gst_1400','Ground surface · 14:00')]
ORIG_IDS={'municipal_zip':'1OofaW0cP7UxvdFE-awBIWEMAvXIg_kjZ','r8_wards':'1xJtgZnG0mcdGEFSWfpqAa7y9YYec_36E','gee_wet':'1djjbRqPqDbZDsIETgVi2zUBFRP5kDZuC','rupesh_git':'https://github.com/FabinGurung/jp-research-lab/blob/main/researchers/rupesh-man-pradhan/gis/RMP_GIS_V02_4_THESIS_WARD_PLATE.py'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def idx(value): return int(np.digitize([float(value)],EDGES[1:-1],right=True)[0])

def as_path(poly:Polygon):
    vs=[];cs=[]
    for ring in [poly.exterior,*poly.interiors]:
        arr=np.asarray(ring.coords)
        if len(arr)<4:continue
        codes=np.full(len(arr),MplPath.LINETO,dtype=np.uint8);codes[0]=MplPath.MOVETO;codes[-1]=MplPath.CLOSEPOLY
        vs.extend(arr); cs.extend(codes)
    return MplPath(np.asarray(vs),np.asarray(cs,dtype=np.uint8))

def geo_patch(ax,geom,face='none',edge='#182B35',lw=.6,z=2,alpha=1):
    if geom is None or geom.is_empty:return
    arr=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom]
    for p in arr:
        if p.geom_type!='Polygon':continue
        pp=PathPatch(as_path(p),facecolor=face,edgecolor=edge,linewidth=lw,zorder=z,alpha=alpha,joinstyle='round',fill=face!='none')
        pp.set_fillrule('evenodd') if hasattr(pp,'set_fillrule') else None
        ax.add_patch(pp)

def north(ax,xy=(.92,.88),size=.06):
    x,y=xy;ax.annotate('N',xy=(x,y+size*.6),xycoords='axes fraction',ha='center',fontsize=10,weight='bold',color='#233545')
    p=np.array([[x,y+size*.6],[x-size*.28,y-size*.5],[x,y-size*.26],[x+size*.28,y-size*.5]])
    ax.add_patch(MplPolygon(p,transform=ax.transAxes,fill=False,edgecolor='#1C2833',lw=1.0,clip_on=False,zorder=20))

def scalebar(ax,xspan=10000):
    xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim(); width=xmax-xmin;height=ymax-ymin
    # Each half 5 km; no invented map metric.
    total=xspan
    x=xmin+width*.10;y=ymin+height*.065;bar_h=height*.012
    for i in [0,1]: ax.add_patch(Rectangle((x+i*total/2,y),total/2,bar_h,facecolor=['#1b2028','white'][i],edgecolor='#1b2028',lw=.8,zorder=15))
    for i,s in enumerate(['0','5','10 km']): ax.text(x+i*total/2,y+bar_h+height*.015,s,fontsize=8,ha='center',color='#1b2833',zorder=15)

def setup_ax(ax,mun,zoom=None,show_north=True):
    b=mun.bounds
    if zoom is None:
        w=b[2]-b[0];h=b[3]-b[1];pad=max(w,h)*.075
        ax.set_xlim(b[0]-pad,b[2]+pad);ax.set_ylim(b[1]-pad,b[3]+pad)
    else:ax.set_xlim(*zoom[:2]);ax.set_ylim(*zoom[2:])
    ax.set_aspect('equal',adjustable='box');ax.set_xticks([]);ax.set_yticks([])
    for spine in ax.spines.values():spine.set_color('#607082');spine.set_linewidth(.5)
    if show_north:north(ax)

def basic_legend(fig,x=.08,y=.075,w=.5,fontsize=9):
    fig.text(x,y+.056,'THERMAL CLASS   /   TEMPERATURE (°C)',fontsize=fontsize+1,weight='bold',color='#233440')
    for i,(lab,col) in enumerate(zip(CLASS_NAMES,PALETTE)):
        xx=x+i*w/8
        fig.patches.append(Rectangle((xx,y+.018),w/8*.68,.023,transform=fig.transFigure,facecolor=col,edgecolor='#57616A',lw=.3,clip_on=False))
        fig.text(xx,y,lab,fontsize=fontsize-1,color='#273B49')

def map_field(mun,wards,output):
    fig=plt.figure(figsize=(16.53,11.69),facecolor='white')
    fig.suptitle('Pokhara  |  field-measured temperatures',x=.055,y=.959,ha='left',fontsize=22,fontweight='bold',color='#172636')
    fig.text(.055,.922,'Manual observations · R8 controlled scope (31 May–31 July 2026) · 44 dates / 186 events · only 3 wards measured',fontsize=11.2,color='#4E5D6B')
    fig.text(.055,.89,'Study-wide frame: Pokhara historical municipality (gray); choropleths apply ONLY to observed wards W06, W08, W16.',fontsize=9.2,color='#607084')
    zoom_geom=wards.geometry.union_all();bb=zoom_geom.bounds
    zoom=(bb[0]-1300,bb[2]+1500,bb[1]-1200,bb[3]+1300)
    for i,(metric,title) in enumerate(FIELD_METRICS):
        # Municipal map above, measured-site zoom underneath.
        ax=fig.add_axes([.055+i*.31,.36,.286,.485])
        setup_ax(ax,mun)
        geo_patch(ax,mun,'#EFF1F3','#738293',.7,z=1)
        for row in wards.itertuples():
            v=getattr(row,metric);geo_patch(ax,row.geometry,PALETTE[idx(v)],'#1A2936',.7,z=4)
        ax.set_title(title,fontsize=11.0,fontweight='bold',color='#17283A',pad=9)
        bx=fig.add_axes([.067+i*.31,.218,.265,.216]);setup_ax(bx,mun,zoom,show_north=False)
        for row in wards.itertuples():
            v=float(getattr(row,metric));geo_patch(bx,row.geometry,PALETTE[idx(v)],'#162B39',.8,z=4)
            pos=row.geometry.representative_point()
            wno=int(row.ward_no)
            shift={6:(-1800,-1300),8:(1500,-1300),16:(0,600)}[wno]
            bx.annotate(f'W{wno:02d}\n{v:.2f}°C',(pos.x,pos.y),xytext=(pos.x+shift[0],pos.y+shift[1]),fontsize=8.3,
                        weight='bold',color='#121C26',ha='center',va='center',zorder=9,
                        arrowprops=dict(arrowstyle='-',lw=.7,color='#243846'),
                        bbox=dict(facecolor='white',alpha=.92,boxstyle='round,pad=.16',edgecolor='#8898A8',linewidth=.25))
        bx.set_title('Measured wards · detail',fontsize=8.3,pad=3,color='#4B5B6A')
        if i==0:scalebar(ax,10000)
    fig.text(.055,.158,'INTERPRETATION',fontsize=10,fontweight='bold',color='#182B3B')
    fig.text(.055,.132,'Colours indicate ward-linked means, NOT uniform temperature everywhere in each ward; unmeasured wards remain gray.',fontsize=8.5,color='#526373')
    basic_legend(fig,x=.055,y=.055,w=.65,fontsize=8)
    fig.text(.748,.077,'SOURCE / GIS',fontsize=8.5,weight='bold',color='#273746')
    fig.text(.748,.055,'Binay R8 ward joined GeoJSON; historical RMP municipal outline\nCRS EPSG:32644 · municipality not independently certified',fontsize=7.3,color='#526575')
    fig.savefig(output,format='pdf',facecolor='white');fig.savefig(str(Path(output).with_suffix('.png')),dpi=150,facecolor='white');plt.close(fig)

def map_satellite(mun,wards,raster_path,output):
    with rasterio.open(raster_path) as ds:
        arr=ds.read(1,masked=True);valid=~np.ma.getmaskarray(arr)
        inside=geometry_mask([mapping(mun)],out_shape=(ds.height,ds.width),transform=ds.transform,invert=True)
        v=valid&inside
        classes=np.digitize(np.asarray(arr.data),EDGES[1:-1],right=True).astype('uint8')
        code=classes+1
        code[~v]=0
        counts=np.bincount(classes[v],minlength=8).tolist()
        geom_polygons=[]
        for geometry,value in shapes(code,mask=code>0,transform=ds.transform):
            i=int(value)-1
            geom_polygons.append((i,shape(geometry)))
        info={'raster_width':ds.width,'raster_height':ds.height,'raster_crs':str(ds.crs),'raster_bounds':list(ds.bounds),'raster_valid_cells_total':int(valid.sum()),'raster_cells_valid_inside_municipality':int(v.sum()),'municipal_area_km2':mun.area/1e6,'valid_cell_area_km2':int(v.sum())*ds.res[0]*ds.res[1]/1e6,'municipal_valid_cell_area_pct_est':int(v.sum())*ds.res[0]*ds.res[1]/mun.area*100,'counts_inside_municipality':counts,'class_names':CLASS_NAMES,'n_vector_polygons':len(geom_polygons),'nodata_preserved':True}
        np.savetxt(str(Path(output).with_suffix('.classes.csv')),np.column_stack((np.arange(1,9),counts)),fmt='%s',delimiter=',',header='class_index,count_inside_municipality',comments='')
    fig=plt.figure(figsize=(16.53,11.69),facecolor='white')
    fig.suptitle('Pokhara  |  wet-season Landsat land-surface temperature',x=.063,y=.957,ha='left',fontsize=21,fontweight='bold',color='#172A39')
    fig.text(.063,.921,'Existing Binay GEE V05 (2026) · 30 m LST median GeoTIFF · exact 8-bin palette requested · no fabricated pixels',fontsize=11,color='#4F6270')
    ax=fig.add_axes([.07,.169,.66,.704]);setup_ax(ax,mun)
    geo_patch(ax,mun,'#E9ECEF','#253E4E',.85,z=1)
    for i,g in geom_polygons:geo_patch(ax,g,PALETTE[i],'none',0,z=2)
    # Observed site boundaries overlay only, not claims of temperature equivalent.
    for row in wards.itertuples():
        geo_patch(ax,row.geometry,'none','#152E42',.8,z=5)
        p=row.geometry.representative_point()
        ax.text(p.x,p.y,f'W{int(row.ward_no):02d}',fontsize=7.8,weight='bold',color='#111B24',ha='center',zorder=6,bbox=dict(facecolor='white',alpha=.75,edgecolor='none',boxstyle='round,pad=.12'))
    scalebar(ax,10000)
    fig.text(.766,.773,'COVERAGE AUDIT',fontsize=12,weight='bold',color='#192C3A')
    fig.text(.766,.732,f"{info['municipal_valid_cell_area_pct_est']:.1f}%",fontsize=31,weight='bold',color='#A33323')
    fig.text(.766,.702,'municipality covered by\nvalid existing satellite pixels',fontsize=10,color='#485A68')
    fig.text(.766,.627,'79.4% not covered',fontsize=10.5,weight='bold',color='#A33323')
    fig.text(.766,.590,'Gray means unavailable\nLST pixels, not a cold\ntemperature class.',fontsize=8.6,color='#455E6E',linespacing=1.35,va='top')
    fig.text(.766,.507,'SCOPE',fontsize=10,weight='bold',color='#172F41')
    fig.text(.766,.480,'The original V05 TIFF\ncovers only the three-site\nstudy grid. No extrapolation\nor synthetic fill.',fontsize=8.5,color='#526474',linespacing=1.40,va='top')
    fig.text(.766,.364,'RELEASE STATE',fontsize=10,weight='bold',color='#172F41')
    fig.text(.766,.333,'Partial-coverage review.\nFull-city export pending GEE\nauthentication and QA.',fontsize=8.5,color='#526474',linespacing=1.40,va='top')
    basic_legend(fig,x=.065,y=.065,w=.65,fontsize=8)
    fig.text(.766,.094,'Source: original GEE V05 R02 TIFF\nMunicipality: historical RMP shapefile',fontsize=8,color='#526474')
    fig.savefig(output,format='pdf',facecolor='white');fig.savefig(str(Path(output).with_suffix('.png')),dpi=150,facecolor='white');plt.close(fig)
    return info

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--wards',required=True);a.add_argument('--municipality',required=True);a.add_argument('--wet-tif',required=True);a.add_argument('--output-dir',required=True)
    p=a.parse_args();od=Path(p.output_dir);od.mkdir(parents=True,exist_ok=True)
    mun_gdf=gpd.read_file(p.municipality).to_crs('EPSG:32644');assert len(mun_gdf)==1
    wards=gpd.read_file(p.wards).to_crs('EPSG:32644')
    assert set(wards.ward_no)=={6,8,16}
    mun=mun_gdf.geometry.iloc[0]
    assert mun.is_valid and 450 < mun.area/1e6 < 480
    assert all(mun.contains(r.geometry.representative_point()) for r in wards.itertuples())
    f=od/'BINAY_MAP002_FIELD_WARDS_A3_VECTOR.pdf';s=od/'BINAY_MAP002_GEE_WET_PARTIAL_CITY_A3_VECTOR.pdf'
    map_field(mun,wards,f);stats=map_satellite(mun,wards,p.wet_tif,s)
    receipt={'map_release':'MAP002_20261121','scientific_status':'TECHNICAL_REVIEW_CANDIDATE_ONLY__CITYWIDE_WET_EXPORT_NOT_COMPLETED','sources':{'r8_wards':{'sha256':sha(p.wards),'drive_id':ORIG_IDS['r8_wards']},'wet_tif':{'sha256':sha(p.wet_tif),'drive_id':ORIG_IDS['gee_wet']},'municipal_boundary_wgs84':{'sha256':sha(p.municipality),'derived_from_original_zip_drive_id':ORIG_IDS['municipal_zip']},'municipal_historical_source':'Pokhara Lekhnath Mahanagarpalika in Rupesh GIS ZIP; NepalDD/Everest 1830 -> WGS84; not certified current municipal survey'},'class_edges':EDGES[1:-1], 'class_names':CLASS_NAMES,'palette_hex':PALETTE,'field_metrics':FIELD_METRICS,'satellite_coverage':stats,'output_hashes':{i.name:sha(i) for i in [f,s]},'non_observed_area_is_not_temperature':True,'notes':['No image-generation model used for these source-derived vector PDFs.','No full-city Landsat raster available or export executed in this run; source V05 is study extent only.','No site results were extrapolated onto unmeasured wards.']}
    (od/'MAP002_source_QA_receipt.json').write_text(json.dumps(receipt,indent=2,default=str),encoding='utf-8')
    print(json.dumps({'output_field':str(f),'output_satellite':str(s),'coverage_pct':stats['municipal_valid_cell_area_pct_est'],'vector_polygons':stats['n_vector_polygons'],'field_sha256':sha(f),'satellite_sha256':sha(s)},indent=2))

if __name__=='__main__':main()
