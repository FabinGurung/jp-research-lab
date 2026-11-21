#!/usr/bin/env python3
"""Authenticated Earth Engine export for a *NEW* Pokhara municipality-wide wet-season 2026 LST raster.

THIS SOURCE FILE HAS NOT BEEN EXECUTED in the ChatGPT environment; a signed-in
Earth Engine-enabled Google Cloud project is required. It does NOT claim to
reproduce the earlier 3-site GEE V05 raster, whose scene/window admission
process is separately governed. Run in Colab after scientific acquisition review.

Prerequisites: pip install earthengine-api ; upload the sibling municipal
WGS84 GeoJSON; user must supply GEE_PROJECT ID with Earth Engine enabled.
Source material: Landsat 8/9 Collection 2 Level 2 Tier 1, L2SP only, ST_B10.
References:
 https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2
 https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2
 https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands
 https://developers.google.com/earth-engine/apidocs/export-image-todrive
"""
import os,json,argparse
from pathlib import Path

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--gee-project',default=os.getenv('GEE_PROJECT'))
    a.add_argument('--geometry',default=str(Path(__file__).with_name('pokhara_metropolitan_historical_RMP_NepalDD_to_WGS84.geojson')))
    a.add_argument('--start',default='2026-05-31')
    a.add_argument('--end-exclusive',default='2026-08-01')
    a.add_argument('--drive-folder-name',default='BINAY_MAP002_CITYWIDE_EXPORTS')
    a.add_argument('--dry-run-metadata-only',action='store_true')
    args=a.parse_args()
    if not args.gee_project:raise SystemExit('No Earth Engine cloud project; pass --gee-project or GEE_PROJECT. Nothing exported.')
    from ee import Geometry,Feature,ImageCollection,Image
    import ee
    try:ee.Initialize(project=args.gee_project)
    except Exception:
        print('No valid Earth Engine session; opening interactive authorization.')
        ee.Authenticate()
        ee.Initialize(project=args.gee_project)
    geodata=json.loads(Path(args.geometry).read_text(encoding='utf-8'))
    geom=geodata['features'][0]['geometry']
    # Avoid opaque shapefile CRS errors: this sibling GeoJSON has already been
    # transformed and QA-checked from RMP's NepalDD municipality polygon.
    municipal=ee.Geometry(geom,proj='EPSG:4326',geodesic=False)
    def process(im):
        qa=im.select('QA_PIXEL')
        # Exclude: fill (0), dilated cloud (1), cirrus (2), cloud (3),
        # cloud shadow (4), snow (5). Retain water, but report it explicitly
        # if water exclusion is requested in later scientific reviews.
        accept=qa.bitwiseAnd(63).eq(0)
        return (im.select('ST_B10').multiply(0.00341802)
                  .add(149.0).subtract(273.15).rename('LST_C')
                  .updateMask(accept)
                  .copyProperties(im,['system:time_start','LANDSAT_PRODUCT_ID','SPACECRAFT_ID']))
    ls8=ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    ls9=ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
    scenes=(ls8.merge(ls9).filterBounds(municipal)
            .filterDate(args.start,args.end_exclusive)
            .filter(ee.Filter.eq('PROCESSING_LEVEL','L2SP')))
    count=scenes.size().getInfo()
    print('Municipality intersecting source scenes:',count)
    print('Source scene product IDs:',scenes.aggregate_array('LANDSAT_PRODUCT_ID').getInfo())
    print('Acquisition window:',args.start,'to',args.end_exclusive,'exclusive')
    if count==0:raise SystemExit('Zero scenes: no export; inspect filters/time window and source. Do not fabricate')
    if args.dry_run_metadata_only:
        print('DRY RUN - scene metadata only; no raster exported')
        return
    # A per-pixel median of accepted, cloud-screened Landsat observations.
    # LST median does not imply same-day comparison with 14:00 field GST/air.
    median=scenes.map(process).median().clip(municipal)
    nodata=-9999.0
    img=median.unmask(nodata,sameFootprint=False).toFloat()
    description='BINAY_MAP002_POKHARA_CITYWIDE_WET_LST_2026_MEDIAN'
    task=ee.batch.Export.image.toDrive(image=img,description=description,folder=args.drive_folder_name,
                 fileNamePrefix=description,region=municipal,crs='EPSG:32644',scale=30,
                 maxPixels=1e10,fileFormat='GeoTIFF',formatOptions={'cloudOptimized':True,'noData':nodata})
    task.start()
    print('Export STARTED; task ID:',task.id)
    print('Do not call it completed until task status COMPLETED and raster passes independent QA.')
    print('After Drive output appears, rerun make_maps.py with --wet-tif set to the downloaded raster.')

if __name__=='__main__':main()
