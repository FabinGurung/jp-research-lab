# Binay Karki — MAP003 full-municipality wet-season Landsat LST Colab

**Current Google Colab permanent Drive ID:** [1Jf2JZwiIodAHMXn7Xr2XYvOifqnJ8FXv](https://colab.research.google.com/drive/1Jf2JZwiIodAHMXn7Xr2XYvOifqnJ8FXv).

This Git folder contains the exact **replacement .ipynb** (30 clean cells, 14 code + 16 markdown) and the adjacent historical municipal geometry in `../map002/pokhara_metropolitan_historical_RMP_NepalDD_to_WGS84.geojson`. The geometry is derived from Rupesh's historical Pokhara Lekhnath municipality shapefile ZIP, **not a new certified 2026 cadastral/administrative survey**. Its SHA-256 is `b7ed29c435f736d436150ce735692990b320bef1e64b9a77d046fd39736d19f5`; its observed EPSG:32644 area is approximately 465.056 km².

## What the old map means

Earlier MAP002 `20.6%` is **municipal area with usable LST pixels in Binay's old three-site source TIFF** (95.6709 km² / 465.056 km²). The percentage unit is correct, but this *three-site sampling-grid coverage* is not the desired full municipality-wide satellite acquisition.

## What MAP003 will actually do after the owner runs Colab

1. Verify the exact Git-checked municipal polygon by SHA and EPSG:32644 area.
2. Authorize Earth Engine using the same Cloud project recorded in the historic notebook (`just-a-project-5007`); Google can request user authorization.
3. Search 2026-05-31 through 2026-08-12 Landsat 8/9 Collection 2 Level 2 `L2SP` scenes against **the municipality**, not the three-site buffer.
4. Apply the existing Binay V05 QA filters (QA_PIXEL bits 0–5 excluded, QA_RADSAT=0, ST_QA ≤5K, ST_CDIST ≥1km, LST 15–60°C) and save exact product IDs.
5. Report separately: percentage of municipality intersected by a Landsat scene; percentage with base-QA valid thermal pixels; percentage with strict V05-QA valid thermal pixels. All three percentages are area ratios, NOT temperature units. Export median `LST_C`, `N_PRIMARY`, `N_BASE` and `SCENE_FOOTPRINT` as four GeoTIFF bands at a 30 m output grid.
6. After **GEE reports COMPLETED**, fetch the actual TIFF, independently check validity, EPSG, counts, thermal bins and geographic fraction; draw the true 8-bin figure, export full valid source pixel CSV and optional native Google Sheet.
7. Preserve resulting evidence in separate Drive folder [BINAY_MAP003_CITYWIDE_WET_2026_EXPORTS](https://drive.google.com/drive/folders/1PH3JhBcsSnDMxAx4B4-9y_50ZLEbm4fd), without overwriting the MAP002 or GEE V05 research inputs.

The **original finished 97-cell GEE V00–V08 notebook** was duplicated byte-for-byte **before any in-place current replacement** to this PRE snapshot:
[000001_PRE historical Colab original](https://drive.google.com/file/d/1OIqegc2RLGNqgUuO1dyrl2WclrDJAkOe/view)
and [archive folder](https://drive.google.com/drive/folders/1kdoujzwnsjs1Vjd17_kh2Afxmsrvs4R5).
The historical Google Drive revisions and original scientific data folders remain unchanged.

**Execution state:** Source and static `nbformat` / AST validation completed. **GEE has not been executed by ChatGPT** (no interactive signed-in Earth Engine runtime). No project submission, complete-coverage or researcher-scientific-approval claim is made.

## Units and limitations

- LST: degrees Celsius; geographic area: km²; coverage: percent **of a fixed municipal area**.
- Output nominal grid: 30 m; Landsat 8/9 TIRS thermal sensing native resolution: approximately 100 m, resampled to 30 m in the delivered product. [NASA TIRS documentation](https://science.nasa.gov/mission/landsat/tirs/).
- Clouds and QA restrictions can leave masked pixels even in a municipality-wide export. Gray is a data gap, never zero or a cold temperature.
- The available municipality outline is historical and does not certify current ward boundaries.
- Binay's field air temperature and measured ground-surface temperature are not Landsat radiometric LST; 44/186 vs 47/202 field source inclusion remains researcher-scientific review.
- [Google Earth Engine auth](https://developers.google.com/earth-engine/guides/auth) and [export](https://developers.google.com/earth-engine/apidocs/export-image-todrive) require an authorized project.

[Existing live audit](https://docs.google.com/document/d/11EyRADuMW9ql_NhQTuFoop7BrPKFJmbBbJaMXFCt4Z0/edit) owns QA and PRE/POST history; the manuscript PDF and previous GEE science are not changed.
