# Modular, readable LaTeX source deliveries — A9 R&D policy (2026-11-12)

**Status:** New-delivery source contract; approval and incorporation follow the repository's protected-main PR process. Applies to **new delivered LaTeX working projects** in both Academic Writing and Enterprise Documents. It is a packaging/source-navigation rule, **not** a new shared formatting tower and **not** permission to rewrite prior approved manuscripts.

## Human-facing default

1. **The primary working deliverable is a normal, uncompressed, navigable folder** in the owner's appropriate private Google Drive location (and corresponding public-safe Git source when authorized). Do not make a ZIP/7z/RAR the **only** browsable source. Provide a direct link to the folder. Files remain independently inspectable and editable.
2. **Keep `main.tex` short and declarative.** It selects the class, imports the existing authoritative shared style, arranges front matter/chapters/sections and bibliography, and is the entry point for PDF compilation. Substantive content belongs in one or more separate `*.tex` files referenced by `\\input{...}` or `\\include{...}` (or a source-equivalent supported module instruction).
3. **Use a meaningful content split.** Theses and long reports normally use `frontmatter/`, `chapters/chapter01_*.tex`, `chapters/chapter02_*.tex`, `appendices/`. One-page letters and contracts use `sections/parties.tex` or `content/body.tex` rather than inventing five artificial chapters. A single large body stuffed in `main.tex` is not an acceptable new source package.
4. **Support files live alongside the project** in relevant subfolders: `figures/`, `tables/`, `data/`, `notebooks/`, `scripts/`, `attachments/`, `appendices/`, `references.bib`, and `project_config.tex`. Create them **only as needed**, not as mandatory empty boilerplate. Source Excel/CSV, images, notebook files and code must be cited/traced by provenance; personal/sensitive binary originals stay in authorized private Drive.
5. A concise `README.md` states source owner, current draft/release status, `main.tex` build command (XeLaTeX/Biber, pdfLaTeX/BibTeX etc as actually configured), shared style identifier/pin, required tools and asset locations. Keep a small `source_manifest.json` only when there are external/private assets or source links, with exact provider IDs and hashes when verified.
6. **Compiling is separate from publication.** Execute the project main entry point and check the build logs, included file resolution, bibliography, page rendering, QA evidence and permission to release. A successful PDF build does not validate legal, structural, medical or academic claims.
7. Do not routinely include `*.aux`, `*.log`, `*.out`, `*.toc`, `*.bbl`, `*.blg`, `*.synctex.gz` or temporary figures in source deliveries unless an exact provenance/reproduction reason is documented. Generated `PDFs` live as separately versioned artifacts under the owning Drive authority.
8. **Historical ZIPs remain immutable.** Preserve the original complete Nabin, Saugat and prior enterprise source archives and existing stable LIVE ID/version relationships. If they are currently the registered release artifact, keep them; publish the unpacked browsable project alongside them and change release manifests only under each owner's approved migration. Never delete, silently convert, rename or replace existing sources to comply retroactively.
9. **Never place private identities, citizenship scans, PAN numbers, personal contact details, licensed font binaries, private signed forms or medical information in public GitHub.** Use restricted Drive originals and a public-safe manifest/pointer only when permitted.
10. **Existing canonical enterprise v3 template files remain unchanged.** Their one-file `templates/enterprise/v3/<type>.tex` modules are renderer source assets with verified blob pins. This policy governs newly rendered **per-document working project folders**, not a silent rewrite of those 14 approved layouts or the private renderer's contractual issue gates.
11. Keep the existing academic single `controls/latex/template/pumlsc-shared.sty` authority and each researcher's pinned version. No copied shared format `.sty` inside the researcher project merely to make a folder look self-contained.
12. Validate newly prepared source deliveries with `python scripts/latex/check_modular_project.py <project-folder>` before publishing or classifying a source package as **complete**. This structural lint is not a scientific or legal approval.

## Recommended concise human tree

```text
Project_Name/
├── README.md
├── main.tex                 # sole compilation entrypoint
├── project_config.tex       # optional, metadata/config only
├── frontmatter/             # thesis/report if needed
├── chapters/                # long form: one file per chapter
├── sections/                # short form: one file per logical section
├── appendices/              # only if used
├── figures/                 # drawings, image files when releasable
├── tables/                  # table TeX/CSV sources as applicable
├── data/                    # datasets / spreadsheets only when authorized
├── notebooks/               # Colab/ipynb when used
├── scripts/                 # Python/analysis source when used
├── attachments/             # external PDFs and records (private if sensitive)
├── references.bib           # if bibliography used
└── source_manifest.json     # when assets live outside this folder
```

Use **one of `chapters/` or `sections/` according to the document length**, not both unless the document actually needs both. A folder tree is a helpful convention; only referenced assets and essential source are build requirements.

## Non-goals and compatibility

This policy changes no active researcher's scientific wording, no template-pinned SHA, no Drive CURRENT IDs, no official source ZIP and no v3 enterprise renderer. Git commits/PRs are code history; Drive holds physical source originals and the released PDF. Each project retains its own source-admission, versioning and approval process. Any actual automatic enforcement integration into a CI release pipeline must be separately tested against the owning source formats.

## Rationale

A normal working folder lets a human open `chapters/chapter4_results_discussion.tex` or `sections/terms.tex` immediately without unzipping. `main.tex` is intentionally a small orchestration file. Neither LaTeX nor the compiler requires the extra QA JSONs/markdown historical records shown in some older distribution archives; those are internal provenance aids and should be stored outside the smallest necessary publication bundle when not needed for reproducibility.

## Professional reader-facing output vs Google Doc review (owner instruction, 2026-11-12)

- Treat the LaTeX source and compiled PDF as the **actual human professional deliverable**. The owner determines when to submit and when further edits are needed. Do **not** insert workflow-completion labels, editorial/technical status legends, or an automated “draft”, “candidate”, “unsigned”, or “unissued” banner merely because the source, signatures or evidence has not been separately checked. Do not assert a signature, official approval, statutory compliance or completed engineering verification unless it exists.
- The visible PDF and content-level `.tex` files must use normal professional terminology. Omit internal user identifiers, canonical-reference labels, model/AI or database descriptions, QA/provenance arguments, review prompts, migration notes, version-control commentary and developer tool names that serve no reader-facing business purpose.
- Put **all reviewer questions, source citations, factual discrepancies, statutory concerns, release-gate evidence, suggested edits and future task lists** into a separate **native Google Doc** in the person/project's owning Drive location. A concise technical README may describe how to compile and the file layout, not reproduce private review material or submit status declarations.
- Keep each existing source file and compiled PDF at its stable LIVE Drive **file ID** for future updates. For a meaningful change, make verified PRE copies of the prior source/PDF under the subject's version-history folder, update the same LIVE IDs, verify content and placement, then make POST copies under the matching ordinal. Original historical ZIP/source archives and native Git revisions remain preserved; do not overwrite a previous release snapshot with a replacement. Existing project control may specify a different governed history plan; read it before changing provider identities.
- The preceding layout rule is a professional publishing convention. It does **not** silently approve an unsigned contract, confer engineering authority, or remove real legally necessary employee rights/obligations. Safety/contractual substance must remain in the document; the private Google Doc preserves uncertainties and comparison evidence.

This paragraph complements the A7 public-safe Memory Wall; the owning R&D repository remains authority for its template source and builds.
