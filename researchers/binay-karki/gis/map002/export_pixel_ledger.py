"""Recover every observed municipality-intersecting LST pixel from original Binay V05 TIFF.
Source values are not interpolated, resampled, or modified; coordinates are
center-of-cell WGS84 approximations from the registered UTM 44N grid.
"""
from pathlib import Path
import csv,hashlib,json
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import mapping
from pyproj import Transformer
root=Path(__file__).resolve().parent
p=Path('/mnt/data/BINAY_GEE_V05_WET_SEASON_LST_MEDIAN_CANDIDATE_NODATA_FIXED_V05_20260918_R02.tif.tiff')
mun=gpd.read_file(root/'pokhara_metropolitan_historical_RMP_NepalDD_to_WGS84.geojson')
with rasterio.open(p) as d:
 m=mun.to_crs(d.crs).geometry.iloc[0]
 mask=geometry_mask([mapping(m)],out_shape=(d.height,d.width),transform=d.transform,invert=True)
 arr=d.read(1,masked=True); good=mask&~np.ma.getmaskarray(arr)
 rr,cc=np.where(good);x,y=rasterio.transform.xy(d.transform,rr,cc,offset='center')
 to_ll=Transformer.from_crs(d.crs,'EPSG:4326',always_xy=True)
 lon,lat=to_ll.transform(x,y)
 v=np.asarray(arr.data[rr,cc]); bins=[5,10,15,20,25,30,35]
 ix=np.digitize(v,bins,right=True)+1
 output=root/'BINAY_MAP002_ALL_VALID_GEE_WET_PIXELS_INSIDE_POKHARA_106301.csv'
 with output.open('w',encoding='utf-8',newline='') as f:
  w=csv.writer(f);w.writerow(['pixel_row_zero_based','pixel_col_zero_based','UTM44N_E_center_m','UTM44N_N_center_m','Longitude_WGS84','Latitude_WGS84','LST_C_original','8class_index','source_version'])
  for row in zip(rr,cc,x,y,lon,lat,v,ix):
   r,c,xx,yy,lo,la,temp,cls=row
   w.writerow([int(r),int(c),f'{xx:.3f}',f'{yy:.3f}',f'{lo:.8f}',f'{la:.8f}',f'{temp:.8f}',int(cls),'GEE_V05_R02_20260918'])
 print('Pixel ledger',output,'rows',len(rr),'sha256',hashlib.sha256(output.read_bytes()).hexdigest(),'bytes',output.stat().st_size)
