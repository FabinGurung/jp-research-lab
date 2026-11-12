# Modest, readable LaTeX starter (fictional and public-safe)

This is only a packaging demonstrator. It is **not** one of the fourteen approved enterprise v3 document layouts, nor a replacement for the shared academic university style.

Files:
- `main.tex`: compile entrypoint / imports / order only.
- `sections/body.tex`: actual content in a separate file.

From this folder, run `pdflatex -interaction=nonstopmode -halt-on-error main.tex`. For new real projects, use the correct existing v3 renderer / shared thesis style and source-owned build profile, then inspect the resulting PDF before any issue.

Verify with `python ../../../scripts/latex/check_modular_project.py .` from this folder (relative path from the repository root actually is `../../../scripts/latex/check_modular_project.py`). Keep working delivery **uncompressed**, and add only real optional asset folders. Official PDFs and private evidence belong in their authorized Drive destinations.
