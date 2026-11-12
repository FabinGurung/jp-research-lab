#!/usr/bin/env python3
"""Structural preflight for NEW unpacked LaTeX working-project deliveries.

Does not certify official formatting, science, claims, contractual validity or PDF layout.
It intentionally does not rewrite historical ZIPs or existing enterprise v3 template assets.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

INCLUDES = re.compile(r"\\\\(?:input|include|subfile)\\s*(?:\\[[^]]*\\]\\s*)?\\{([^{}]+)\\}")
BIB = re.compile(r"\\\\(?:addbibresource|bibliography)\\s*\\{([^{}]+)\\}")
SOURCE_ARCHIVES = {".zip", ".7z", ".rar"}
GENERATED_NAMES = {".aux", ".log", ".out", ".toc", ".blg", ".bbl", ".fls", ".fdb_latexmk"}
GENERATED_SUFFIXES = (".synctex.gz",)
MAX_TEX_SOURCE_BYTES = 1_000_000


def strip_comments(tex: str) -> str:
    # A literal unescaped % starts a TeX comment. Lines are otherwise preserved.
    return "\n".join(re.split(r"(?<!\\)%", line, maxsplit=1)[0] for line in tex.splitlines())


def check_project(root: Path) -> dict:
    root = root.resolve()
    problems: list[str] = []
    warnings: list[str] = []
    source_files: set[str] = set()
    if not root.is_dir():
        return {"ok": False, "project": str(root), "problems": ["Project is not an unpacked directory"]}
    main = root / "main.tex"
    if not main.is_file():
        problems.append("Missing main.tex compilation entrypoint")
    if not (root / "README.md").is_file():
        problems.append("Missing README.md explaining the real build command and source authority")

    for f in root.rglob("*"):
        if not f.is_file():
            continue
        suffix = f.suffix.lower()
        if suffix in SOURCE_ARCHIVES:
            problems.append(f"Archive inside new working-project delivery: {f.relative_to(root)}; store historical archives separately")
        if suffix in GENERATED_NAMES or f.name.lower().endswith(GENERATED_SUFFIXES):
            warnings.append(f"Generated build by-product is present in source: {f.relative_to(root)}")

    if main.is_file():
        visited: set[Path] = set()
        stack = [main]
        all_includes: set[Path] = set()
        while stack:
            f = stack.pop()
            if f in visited:
                continue
            visited.add(f)
            source_files.add(str(f.relative_to(root)))
            if f.stat().st_size > MAX_TEX_SOURCE_BYTES:
                problems.append(f"Unusually large .tex file (over 1 MB): {f.relative_to(root)}")
                continue
            tex = strip_comments(f.read_text(encoding="utf-8", errors="replace"))
            for value in INCLUDES.findall(tex):
                value = value.strip()
                if "\\" in value or "#" in value:  # macro/dynamic path, cannot resolve statically
                    warnings.append(f"Dynamic include needs compile-time check: {value}")
                    continue
                item = Path(value)
                if item.suffix == "":
                    item = item.with_suffix(".tex")
                # Include paths in LaTeX are normally relative to the compilation directory.
                target = (root / item).resolve()
                if not target.is_relative_to(root):
                    problems.append(f"Include escapes the project folder: {value}")
                elif not target.is_file():
                    problems.append(f"Missing included file: {value} (from {f.relative_to(root)})")
                else:
                    all_includes.add(target)
                    if target.suffix.lower() == ".tex":
                        stack.append(target)
            for group in BIB.findall(tex):
                for raw in group.split(","):
                    value = raw.strip()
                    if not value or "\\" in value:
                        continue
                    target = root / (value if value.lower().endswith(".bib") else value + ".bib")
                    if not target.is_file():
                        warnings.append(f"Bibliography file not in working folder: {value}")
        if not all_includes:
            problems.append("New working project has no external content modules: keep content in separate .tex files, called from main.tex")
        if main.stat().st_size > 12_000:
            warnings.append("main.tex is long; check that substantive content belongs in chapters/ or sections/")

    return {
        "ok": not problems,
        "project": str(root),
        "source_files": sorted(source_files),
        "problems": sorted(set(problems)),
        "warnings": sorted(set(warnings)),
        "scope": "Structural source completeness only; compile and visual/provider review remain required",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Path to new unzipped LaTeX working folder")
    args = parser.parse_args()
    result = check_project(args.project)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
