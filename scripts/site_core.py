#!/usr/bin/env python3
"""
Shared static-site primitives. Stable links/escapes/shell are centralized.
This module must remain read-only: never mutate Drive/scientific sources.
"""
from __future__ import annotations
import argparse, html, json, shutil
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
REPO_URL="https://github.com/FabinGurung/jp-research-lab"
SITE_URL="https://fabingurung.github.io/jp-research-lab/"

def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
def esc(v): return html.escape("" if v is None else str(v))
def branch_url(branch): return f"{REPO_URL}/tree/{quote(branch, safe='/')}"
def drive_url(file_id):
    return f"https://drive.google.com/open?id={file_id}" if file_id else None

def evidence_html(debt):
    parts=[]
    for e in debt.get("evidence",[]):
        u=drive_url(e.get("drive_id")) if e.get("drive_id") else e.get("url")
        if not u or not str(u).startswith("https://"):
            continue
        parts.append(f'<li>{esc(e.get("role"))}: <a href="{esc(u)}">Open evidence</a></li>')
    return "".join(parts) or "<li>No external evidence pointer required.</li>"

def shell(title, body, depth=0):
    prefix="../"*depth
    if title == "Fabin Gurung" and '<main' in body:
        import re
        body = re.sub(r'(<main[^>]*>)', lambda match: match.group(1) + "<section class=\"gallery-feature\" aria-label=\"Fabin structural thesis and interactive frame\"><div class=\"eyebrow\">Structural Engineering · MSc thesis · current working v0.16</div><h2>Explore the one-bay structural frame</h2><p>See seven linked views of the four columns, four beams and one slab, with signed beam moments and shear, compression, reactions and declared analysis boundaries. The frame is a separate schematic experiment from the original two-span database benchmark.</p><div class=\"gallery-feature-links\"><a href=\"experiments/four-workflows/frame.html\">Open interactive frame viewer →</a><a href=\"experiments/four-workflows/index.html\">Explore four workflows →</a><a href=\"https://drive.google.com/file/d/1LBt3R4u35BxhKjOGoX8YflP7zFJutxBk/view\">Current working thesis PDF →</a></div></section>", body, count=1)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · JP R&D</title><link rel="stylesheet" href="{prefix}assets/styles.css"><link rel="stylesheet" href="{prefix}assets/arc-gallery.css"><script defer src="{prefix}assets/theme.js"></script><script defer src="{prefix}assets/motion.js"></script><script defer src="{prefix}assets/prompt-copy.js"></script><script defer src="{prefix}assets/menu.js"></script><script defer src="{prefix}assets/arc-gallery.js"></script></head><body><header class="topbar"><div class="wrap nav"><strong>JP R&D</strong><button class="mobile-menu-toggle" type="button" data-mobile-menu aria-controls="site-nav-links" aria-expanded="false">☰ Menu</button><nav class="navlinks" id="site-nav-links" aria-label="Document families"><a href="{prefix}index.html">Home</a><a href="{prefix}enterprise-documents/index.html">Enterprise Documents</a><a href="{prefix}academic-writing/index.html">Academic Writing</a><a href="{prefix}researchers/fabin-gurung/experiments/four-workflows/frame.html">Frame viewer</a><button type="button" class="theme-switch" data-theme-toggle aria-label="Switch to mauve dusk">☾ Dusk palette</button></nav></div></header>{body}<footer class="wrap footer">JP Research & Development · code + controls + pointers · working artifacts remain in Google Drive.</footer></body></html>"""

def write(out, rel, content):
    p=out/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding="utf-8")

