#!/usr/bin/env python3
"""Build the four-workflow results for Pages and public Actions artifacts."""
import json
import os
import sys
from pathlib import Path

from engine import compute, digest, export, make_schedule, native_schedule

ROOT = Path(__file__).resolve().parent
PUBLIC_PARAMETERS = (
    "span_x", "span_y", "column_height", "column_width", "beam_width",
    "beam_depth", "slab_thickness", "concrete_density", "elastic_modulus",
    "finish_load", "live_load", "concrete_rate", "column_output",
    "formwork_output", "rebar_output", "pour_output", "skilled_workers",
    "helpers", "shift_hours", "column_cure", "slab_cure", "start_date",
    "saturday_off",
)
PUBLIC_PROVENANCE = (
    "source_mode", "read_at", "source_version_checked", "source_payload_repeat_check",
)


def build(out, kernel_dir=None):
    snapshot = json.loads((ROOT / "source-snapshot.json").read_text())
    parameters = snapshot["parameters"]
    provenance = snapshot["provenance"]
    if provenance.get("input_sha256") != digest(parameters):
        raise ValueError("Source snapshot fingerprint mismatch")

    results = make_schedule(parameters, compute(parameters))
    if kernel_dir:
        results = native_schedule(results, kernel_dir)

    # Keep the full input and its fingerprints in the build workspace.
    public_parameters = {key: parameters[key] for key in PUBLIC_PARAMETERS}
    results["parameters"] = public_parameters
    results["input_sha256"] = digest(public_parameters)
    results["provenance"] = {
        key: provenance[key] for key in PUBLIC_PROVENANCE if key in provenance
    }
    results["provenance"]["public_input_sha256"] = results["input_sha256"]
    results["peer_methods"] = json.loads((ROOT / "peer-methods.json").read_text())["peers"]
    export(results, Path(out))
    return results


if __name__ == "__main__":
    build(sys.argv[1], os.environ.get("FABIN_SCHEDULING_CHECKOUT"))
