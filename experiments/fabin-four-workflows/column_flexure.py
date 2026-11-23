"""Elastic in-plane column bending only for the pinned no-sway frame.

NOT roof drift, NOT column axial shortening, NOT a 3D/sway analysis.
Baseline is the existing synthetic four-workflow frame, not a code design.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path


def profile(model: dict) -> dict:
    d = model["dimensions"]
    a = model["actions"]
    h = float(d["height"])
    b = float(d["column"])
    # The synthetic analysis uses 25 GPa. Store this input explicitly in model
    # rather than deriving a stiffness from the *beam* EI.
    E = float(model.get("column_elastic_modulus_kN_m2", 25_000_000))
    EI = E * b**4 / 12.0
    mbase = float(a["column_moment_base"])
    mroof = float(a["column_moment_roof"])
    shear = float(a["column_shear"])
    inferred_shear = (mbase + mroof) / h
    if not math.isclose(shear, inferred_shear, abs_tol=1e-7):
        raise ValueError("Column moment-gradient / transverse shear mismatch")

    # With z measured from the fixed base: M(z) = -Mbase + V*z.
    # Integrate EI*u''=M(z), using u(0)=u'(0)=0. The opposite roof
    # translation is constrained to zero by the no-sway idealization.
    def displacement_mm(z: float) -> float:
        return 1000 * (-mbase * z*z/2 + shear*z*z*z/6) / EI
    def slope(z: float) -> float:
        return (-mbase*z + shear*z*z/2) / EI

    if not math.isclose(displacement_mm(h), 0, abs_tol=1e-7):
        raise ValueError("Non-sway column roof displacement does not close")
    if not math.isclose(slope(0), 0, abs_tol=1e-10):
        raise ValueError("Fixed base rotation does not close")

    # Exact interior extremum: u'(z) = 0, z = 2*Mbase/V.
    zpeak = 2*mbase/shear
    if not 0 < zpeak < h:
        raise ValueError("No interior bending-curve extremum")
    p = [{"z_m":h*i/60, "relative_flexure_mm":displacement_mm(h*i/60)} for i in range(61)]
    expected_roof_slope = mroof*h/(4*EI)
    if not math.isclose(slope(h), expected_roof_slope, abs_tol=1e-10):
        raise ValueError("Independent slope-deflection roof rotation mismatch")

    return {
      "status":"DERIVED_FROM_PINNED_NO_SWAY_SYNTHETIC_MODEL",
      "load_case":"Unfactored symmetric gravity, two orthogonal planar frames",
      "scope":"In-plane column flexure relative to fixed-end chord, not building roof drift",
      "axes":"Per planar frame; do not combine into a calibrated global 3D displacement",
      "boundary":"Fixed base rotation/displacement and zero roof translation; roof rotation allowed",
      "column_I_m4":b**4/12,
      "elastic_modulus_kN_m2":E,
      "EI_kN_m2":EI,
      "height_m":h,
      "moment_base_magnitude_kNm":mbase,
      "moment_roof_magnitude_kNm":mroof,
      "shear_kN":shear,
      "roof_translation_mm":0.0,
      "roof_rotation_rad":slope(h),
      "peak_z_m":zpeak,
      "peak_chord_relative_mm":displacement_mm(zpeak),
      "samples":p,
      "excluded":["Global joint movement","Sway/drift","Axial shortening","Slab deflection","Torsion"]
    }


if __name__ == "__main__":
    path=Path(sys.argv[1])
    model=json.loads(path.read_text(encoding="utf-8"))
    model["column_flexure"]=profile(model)
    path.write_text(json.dumps(model,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
