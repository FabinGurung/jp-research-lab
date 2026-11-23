"""Additive Fabin experiment route; existing researcher material is retained."""
import shutil,subprocess,sys
from pathlib import Path

def build_fabin_experiment(root:Path,out:Path):
    destination=out/'researchers/fabin-gurung/experiments/four-workflows'
    shutil.copytree(root/'web/fabin-four-workflows',destination,dirs_exist_ok=True)
    subprocess.run([sys.executable,str(root/'experiments/fabin-four-workflows/build_public.py'),str(destination)],check=True)
    # Preserve the pinned source snapshot; publish the separately checked
    # column in-plane bending derivation only in the generated Pages JSON.
    subprocess.run([sys.executable,str(root/'experiments/fabin-four-workflows/column_flexure.py'),
                    str(destination/'frame-results.json')],check=True)
    # Both shared assets are copied into the existing portal asset directory.
    (out/'assets').mkdir(exist_ok=True)
    for filename in ('arc-gallery.css','arc-gallery.js'):
        shutil.copy2(root/'web'/filename, out/'assets'/filename)
    # Bundle EXACT pinned official Three.js modules into Pages. No runtime CDN
    # or external-host dependency for structural geometry.
    vendor=destination/'vendor'
    vendor.mkdir(exist_ok=True)
    upstream=root/'node_modules'/'three'
    for src,dst in (
        (upstream/'build/three.module.js',vendor/'three.module.js'),
        (upstream/'examples/jsm/controls/OrbitControls.js',vendor/'OrbitControls.js'),
    ):
        if not src.exists():
            raise FileNotFoundError('Run npm install --no-save --no-package-lock --ignore-scripts three@0.164.1 before building Pages: '+str(src))
        shutil.copy2(src,dst)
    # The published experiment previously hid its frame link in the Structure tab.
    # This visible link is additive; the original route and all five tabs remain.
    landing=destination/'index.html'
    html=landing.read_text(encoding='utf-8')
    needle='<div class="source" id="source-state"'
    callout='<section class="scope" aria-label="Interactive structural frame"><h2>Seven interactive structural frame views</h2><p>Explore bending moments, shear forces, axial compression, torsion boundaries, relative beam deflection, illustrative reinforcement and support reactions. Numeric results include the derived in-plane column flexure with its no-sway assumptions.</p><p><a href="frame.html"><strong>Open frame forces and deflection curves →</strong></a> · <a href="detail.html"><strong>Open beam, column, slab 3D and section explorer →</strong></a></p></section>'
    if needle not in html:
        raise ValueError('Experiment landing insertion point missing')
    landing.write_text(html.replace(needle,callout+needle,1),encoding='utf-8')
