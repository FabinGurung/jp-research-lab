"""Prepare the thesis's pinned one-bay visualisation from published results."""
import argparse
import json
import math
from pathlib import Path


def frame_views(results, takeoff):
    p = results["parameters"]
    a = results["analysis"]
    L, h = p["span_x"], p["column_height"]
    if L != p["span_y"]:
        raise ValueError("The thesis views require the square baseline")
    half = L / 2
    x = a["x"]
    q, w = x["slab_load_kPa"], x["beam_selfweight_kN_per_m"]
    end_moment, reaction = -x["independent_hogging_kNm"], x["reaction_kN"]
    beam_ei = p["elastic_modulus"] * p["beam_width"] * p["beam_depth"] ** 3 / 12

    # Half of the beam under uniform self-weight and the rising limb of the
    # triangular slab load. Reflect about midspan for the other half.
    def slope_integral(z):
        return end_moment*z + reaction*z**2/2 - w*z**3/6 - q*z**4/24

    def curvature_integral(z):
        return end_moment*z**2/2 + reaction*z**3/6 - w*z**4/24 - q*z**5/120

    samples = []
    for i in range(41):
        station = L * i / 40
        z = min(station, L - station)
        moment = end_moment + reaction*z - w*z**2/2 - q*z**3/6
        shear = (1 if station <= half else -1) * (reaction - w*z - q*z**2/2)
        movement = 1000 * (curvature_integral(z) - z*slope_integral(half)) / beam_ei
        samples.append(dict(x=station, moment=moment, shear=shear, deflection_mm=movement))

    roof = takeoff["roof"]
    assert math.isclose(x["midspan_sagging_kNm"], samples[20]["moment"], abs_tol=1e-8)
    assert math.isclose(samples[20]["shear"], 0, abs_tol=1e-10)
    assert samples[0]["deflection_mm"] == samples[-1]["deflection_mm"] == 0
    assert samples[20]["deflection_mm"] < 0
    # For symmetric gravity the column's grounded end balances its roof
    # axial force plus its weight. No compression shortening is modelled.
    roof_load = a["roof_load_kN"]
    base = a["base_reaction_each_kN"]
    top = roof_load / 4
    assert math.isclose(4 * base, a["total_load_kN"])
    assert math.isclose(base - top, p["concrete_density"] * p["column_width"]**2 * h)
    assert math.isclose(base, roof["axial_base"])
    assert math.isclose(roof["column_shear"] * h, roof["column_top"] + roof["column_base"])

    groups = [bar for bar in takeoff["bars"] if bar["case_id"] == "Bay 4 m"]
    steel_mass = math.fsum(row["mass_kg"] for row in groups)
    assert math.isclose(steel_mass, takeoff["totals"]["Bay 4 m"][0])
    return dict(
        baseline=results["input_sha256"],
        dimensions=dict(span_x=L, span_y=L, height=h, column=p["column_width"],
                        beam_width=p["beam_width"], beam_depth=p["beam_depth"], slab=p["slab_thickness"]),
        columns=[{k: c[k] for k in ("id", "x", "y")} for c in results["columns"]],
        beams=[{k: b[k] for k in ("id", "start_column", "end_column", "axis")} for b in results["beams"]],
        slab=results["slab"], samples=samples,
        actions=dict(axial_roof=top, axial_base=base, column_shear=roof["column_shear"],
                     column_moment_roof=roof["column_top"], column_moment_base=roof["column_base"],
                     total_reaction=a["total_load_kN"], roof_load=roof_load, beam_EI=beam_ei),
        rebar=dict(groups=[{k: bar[k] for k in ("mark", "diameter_mm", "pieces_per_member", "length_per_piece_m")} for bar in groups],
                   mass_kg=steel_mass),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("published_results", type=Path)
    parser.add_argument("thesis_takeoff", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(frame_views(json.loads(args.published_results.read_text()),
                                                  json.loads(args.thesis_takeoff.read_text())), indent=2) + "\n")
