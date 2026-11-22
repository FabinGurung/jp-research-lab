# Binay Karki — MAP003 full-municipality wet-season Landsat LST Colab

**Current Google Colab permanent Drive ID:** [1Jf2JZwiIodAHMXn7Xr2XYvOifqnJ8FXv](https://colab.research.google.com/drive/1Jf2JZwiIodAHMXn7Xr2XYvOifqnJ8FXv).

This Git folder contains the exact **current extraction-only .ipynb** (MAP003 V03: 17 clean cells, 8 code + 9 markdown) and the adjacent historical municipal geometry in `../map002/pokhara_metropolitan_historical_RMP_NepalDD_to_WGS84.geojson`. The geometry is derived from Rupesh's historical Pokhara Lekhnath municipality shapefile ZIP, **not a new certified 2026 cadastral/administrative survey**. Its SHA-256 is `b7ed29c435f736d436150ce735692990b320bef1e64b9a77d046fd39736d19f5`; its observed EPSG:32644 area is approximately 465.056 km².

## What the old map means

Earlier MAP002 `20.6%` is **municipal area with usable LST pixels in Binay's old three-site source TIFF** (95.6709 km² / 465.056 km²). The percentage unit is correct, but this *three-site sampling-grid coverage* is not the desired full municipality-wide satellite acquisition.

## What MAP003 will actually do after the owner runs Colab

1. Verify the exact Git-checked municipal polygon by SHA and EPSG:32644 area.
2. Authorize Earth Engine using the same Cloud project recorded in the historic notebook (`just-a-project-5007`); Google can request user authorization.
3. Search 2026-05-31 through 2026-08-12 Landsat 8/9 Collection 2 Level 2 `L2SP` scenes against **the municipality**, not the three-site buffer.
4. Apply the existing Binay V05 QA filters (QA_PIXEL bits 0–5 excluded, QA_RADSAT=0, ST_QA ≤5K, ST_CDIST ≥1km, LST 15–60°C) and save exact product IDs.
5. Report separately: percentage of municipality intersected by a Landsat scene; percentage with base-QA valid thermal pixels; percentage with strict V05-QA valid thermal pixels. All three percentages are area ratios, NOT temperature units. Export median `LST_C`, `N_PRIMARY`, `N_BASE` and `SCENE_FOOTPRINT` as four GeoTIFF bands at a 30 m output grid.
6. Once **GEE reports COMPLETED**, verify the actual GeoTIFF separately in ChatGPT Python. Independently check EPSG, raster validity, counts, thermal bins and coverage before plotting; this Colab does **not** render maps or export a native pixel Sheet.
7. Export genuine GeoTIFF to the existing Drive folder [BINAY_MAP003_CITYWIDE_WET_2026_EXPORTS](https://drive.google.com/drive/folders/1PH3JhBcsSnDMxAx4B4-9y_50ZLEbm4fd). The final notebook cell also attempts to save small source/coverage/task metadata files to that folder; metadata-upload permission problems are reported, not treated as evidence that an asynchronous EE export failed.

The **original finished 97-cell GEE V00–V08 notebook** was duplicated byte-for-byte **before any in-place current replacement** to this PRE snapshot:
[000001_PRE historical Colab original](https://drive.google.com/file/d/1OIqegc2RLGNqgUuO1dyrl2WclrDJAkOe/view)
and [archive folder](https://drive.google.com/drive/folders/1kdoujzwnsjs1Vjd17_kh2Afxmsrvs4R5).
The historical Google Drive revisions and original scientific data folders remain unchanged.

**Execution state:** Source and static `nbformat` / AST validation completed. **GEE has not been executed by ChatGPT** (no interactive signed-in Earth Engine runtime). No project submission, complete-coverage or researcher-scientific-approval claim is made.


## MAP003 V02 — 22 November 2026 / Drive archive ordinal 000002

The latest saved Colab run (30 cells, old V01) has the real Earth Engine error `EEException: Request had insufficient authentication scopes` at **Section 7** when `ee.batch.Task.list()` called `listOperations`. Sections 1–6 had run, listing **11 Landsat 8/9 scenes**, and computing **100% scene footprint, 97.043% base-QA LST, 82.141% strict-V05-QA LST** (municipal projected 30-m grid; not independently raster-verified). An export was **not started** by the failing cell because the task-list request failed before `task.start()`.

Exact saved failed notebook copied **before repair** to [000002_PRE with outputs and traceback](https://drive.google.com/file/d/1ypOJEqEhaMLjxRHfBM9Pqs5NcIeCLcaI/view), original source SHA-256 `f0cf540ef713225c8ce316443efa860c516b3a0b53978100f322a4489e8168cc`. New source V02 SHA-256 `c34874e2a1d2874120b0969e7c7b491c8dbd8ea52776e44e4556246454ebe553` and Git blob `acaacf28a6e4274101672acfc476f7362ee8893c`. V02 has 30 notebook cells, 14 Python code cells, Python AST validated; prior outputs were intentionally removed from the current source so they cannot be confused with successful V02 execution.

**Fix:** Section 3 now explicitly requests fresh Colab Earth Engine authentication and checks the exact task-list/operations endpoint. If its default scopes are still insufficient, change `EE_AUTH_MODE` to `gcloud` in Section 1 and rerun Section 3 with Google authorization. Section 7 stops before export unless the batch preflight passed; duplicate tasks by `RUN_KEY` are not silently created, even if an earlier task has failed or completed. Section 8 can recover the existing task after a runtime restart.

**Important:** The temporary authenticated browser consent must occur in the researcher's Colab runtime. V02 is a **source-code repair**, not a completed GEE raster or final scientific release. A7 remains a read-only catalogue; the `000002` archive enumeration is scoped to Binay's Colab PRE/POST, not a new A7-SEQ or an R&D researcher LaTeX sequence. See [version ledger](version-ledger.json).

## MAP003 V03 — extraction-only, same permanent Drive ID / local event 000003 (22 November 2026)

At user instruction, MAP003 is now an **8-code-cell, 17-total-cell Run All extractor**. It retains exact V02 EE auth, Landsat scene-selection, scientific QA, coverage and export cells, but removes old Sections 9–15 (Colab raster readback, plotting, PNG/PDF production, pixel CSV, and native Google Sheets). The final Section 8 reports the asynchronous export state and saves small verified/source metadata to the existing Drive folder where permissions allow. **Run All does not wait for GEE export completion;** task `COMPLETED` plus independent actual GeoTIFF readback is the downstream science gate. A separate ChatGPT Python session can iterate maps and figures from those source data without rerunning Colab.

Drive **000003_PRE V02** [original notebook SHA-copied](https://drive.google.com/file/d/1zwjsMAN2KYLI1nerW2WSawonMbklJlNC/view), SHA-256 `c34874e2a1d2874120b0969e7c7b491c8dbd8ea52776e44e4556246454ebe553` (48,404 bytes). **000003_POST V03** [new same-ID content snapshot](https://drive.google.com/file/d/1VtVk_K9ikQI0w7gbUuhIB43Rpkki7vRo/view), SHA-256 `6d9ead2c0d0148608f308d0a280ffad9bf3c31c7fb99c2f79fd93ed13a22bbba` (26,269 bytes). **Same original Colab ID and filename**. Git V03 blob SHA `d9d57068285e70e912993818d599ef24b2b2bd17`; source validation (nbformat, 8 Python AST cells, preserved original science/export cells) PASSED. The runtime is *not* proven executed and no new export completion is claimed.

**Local event 000003 is distinct from** A7 global sequence numbers, R&D LaTeX researcher sequences, formal research checkpoints and scientific approval. A7 is a read-only catalogue; the authoritative notebook/current provenance and archive live in GitHub/Drive as described in the [version ledger](version-ledger.json).

## Units and limitations

- LST: degrees Celsius; geographic area: km²; coverage: percent **of a fixed municipal area**.
- Output nominal grid: 30 m; Landsat 8/9 TIRS thermal sensing native resolution: approximately 100 m, resampled to 30 m in the delivered product. [NASA TIRS documentation](https://science.nasa.gov/mission/landsat/tirs/).
- Clouds and QA restrictions can leave masked pixels even in a municipality-wide export. Gray is a data gap, never zero or a cold temperature.
- The available municipality outline is historical and does not certify current ward boundaries.
- Binay's field air temperature and measured ground-surface temperature are not Landsat radiometric LST; 44/186 vs 47/202 field source inclusion remains researcher-scientific review.
- [Google Earth Engine auth](https://developers.google.com/earth-engine/guides/auth) and [export](https://developers.google.com/earth-engine/apidocs/export-image-todrive) require an authorized project.

[Existing live audit](https://docs.google.com/document/d/11EyRADuMW9ql_NhQTuFoop7BrPKFJmbBbJaMXFCt4Z0/edit) owns QA and PRE/POST history; the manuscript PDF and previous GEE science are not changed.
