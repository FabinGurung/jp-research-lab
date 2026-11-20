"""Additive Fabin experiment route; existing researcher material is retained."""
import shutil,subprocess,sys
from pathlib import Path

def build_fabin_experiment(root:Path,out:Path):
    destination=out/'researchers/fabin-gurung/experiments/four-workflows'
    shutil.copytree(root/'web/fabin-four-workflows',destination,dirs_exist_ok=True)
    subprocess.run([sys.executable,str(root/'experiments/fabin-four-workflows/build_public.py'),str(destination)],check=True)
