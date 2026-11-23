# Binay Karki (RSH-006) — current MSc thesis and editable sources

**R10.4** is the current **technically verified working** thesis (23 November 2026): 73 A4 pages, including seven A4 landscape geospatial figure pages. The shared PU LaTeX style **v2.6.4** remains an inherited external dependency; no private font files or personally identifying field records are committed here.

- **CURRENT thesis PDF — stable ID:** https://drive.google.com/file/d/15xjWCjTAv9L4f-huU9Kkck0kJjsCW-hG/view
- **CURRENT full editable LaTeX ZIP — stable ID:** https://drive.google.com/file/d/1n2dhxKAHZoUvgck1aikPFs9_EG6ScArI/view
- **CURRENT unzipped editable source tree:** https://drive.google.com/drive/folders/1CIYWLLN-wlQ3gtiMveVytDXLrFNpaVzi
- **Added seven figure files:** https://drive.google.com/drive/folders/1u0MGYA4iD5wPGKAHiH8GByceGbosN8vH
- **Plotting code, QA tables, statistics:** https://drive.google.com/drive/folders/17uaNQ3dvB6wsmnLEEo4iaHP8fLe1PfIK
- **Full source register (which original Drive/Sheet/Excel records were and were not used):** https://drive.google.com/file/d/1i3HqxEfbtM_eD-6PSYYa05_KJpN2wAmv/view
- **Governing internal audit:** https://docs.google.com/document/d/11EyRADuMW9ql_NhQTuFoop7BrPKFJmbBbJaMXFCt4Z0/edit
- **GEE-V10 independent decisions:** https://docs.google.com/spreadsheets/d/1S59v06JAAaZLYKCNLsrosmsqBzsGWTFoAHY7HG35EMg/edit

## New academic material

Abstract, Methodology, Results and Discussion, Conclusions, Recommendations and Appendix source description were edited to integrate the actual MAP003 citywide Landsat LST and controlled MAP004 field-versus-satellite illustrations. Seven maps belong in Chapter 4, alongside source-method descriptions in Chapter 3. The old field evidence and original scientific tables remain untouched.

An apparent **0** at the start of a map scale bar is **0 m**. A **0°C difference** in a Ward 16 reference map denotes zero difference from the *observed* mean LST of that ward (31.73°C), not an absolute zero surface temperature; **0°** on SRTM slope means horizontal ground. Satellite **NoData = −9999** stays masked, never converted to zero-temperature observations.

Ward 16 has only **43.71%** valid strict-quality satellite LST coverage. The R8 field study has **44 dates/186 events (31 May–31 July 2026)**, whereas the current Landsat raster spans **31 May–12 August 2026**. The existing broader manuscript source has **47 dates/202 events** and was not merged into R8. Ward 8 and 6 differences to Ward 16 represent *descriptive land-surface-temperature contrasts*, not synchronized air-temperature UHI, validated accuracy or an elevation-controlled effect. The historical KLL/OSM polygons are not certified 2026 municipal boundaries.

## PRESERVED history and QA

| Role | Google Drive ID | SHA-256 (verified from current readback when applicable) |
|---|---|---|
| PRE R10.3 PDF | `1V0lySjyL1JBmPWz4--BYWShHnnwUHdAo` | original R10.3 scientific PDF retained |
| PRE R10.3 LaTeX ZIP | `1Q-MeiIdRsNnJe8eSQe3Lqgsj6sgw0JL-` | original R10.3 complete source retained |
| CURRENT/POST R10.4 PDF | `15xjWCjTAv9L4f-huU9Kkck0kJjsCW-hG` / POST `1E76LOOx8qUs49ma-F3qfp1N23J5zQhpm` | `2e41652f9184247c80630b8321a628b34ebdfb26ce808338e9b5399e76832b46` |
| CURRENT/POST R10.4 LaTeX ZIP | `1n2dhxKAHZoUvgck1aikPFs9_EG6ScArI` / POST `1GvVdP7x78QJa_Tg4gSpdn9LilvLnV_oI` | `9859d9f0ba74665e8fdc3d7cf89df14ab74d10f4d831ae4bd3268b428c6b9311` |

The PDF and source ZIP matched exact SHA-256 between locally compiled bytes and the same-ID provider readback. Compilation used `xelatex → biber → xelatex → xelatex`, shared PU style Git blob `6deb30ec415fd386de104c0b7248eb9ea8b98ece` and authorized private Times New Roman fonts. All seven maps appear as landscape A4 pages. All original Git history remains.

**Science and submission gates remain open:** no final researcher or supervisor sign-off, official-ward boundary certification, field/satellite time-matched validation or GEE-V10 evidence-admission decision was claimed. This is a current working document, not a final university-certified thesis. The Git researcher LaTeX sequence baseline is not verified, so no sequence number is allocated. A7 remains read-only.
