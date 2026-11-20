#!/usr/bin/env python3
"""Publish only the bounded synthetic parameter/result projection."""
import json,os,sys
from pathlib import Path
from engine import compute,make_schedule,native_schedule,export,digest
ROOT=Path(__file__).resolve().parent

def build(out,kernel_dir=None):
    snap=json.loads((ROOT/'source-snapshot.json').read_text())
    if snap['provenance'].get('input_sha256')!=digest(snap['parameters']):
        raise ValueError('Source snapshot fingerprint mismatch')
    r=make_schedule(snap['parameters'],compute(snap['parameters']))
    if kernel_dir:r=native_schedule(r,kernel_dir)
    r['provenance']=snap['provenance']
    r['peer_methods']=json.loads((ROOT/'peer-methods.json').read_text())['peers']
    out=Path(out);export(r,out)
    return r

if __name__=='__main__':build(sys.argv[1],os.environ.get('FABIN_SCHEDULING_CHECKOUT'))
