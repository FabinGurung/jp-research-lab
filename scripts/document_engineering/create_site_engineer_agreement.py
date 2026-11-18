#!/usr/bin/env python3
"""Create a new private Site Engineer employment project with modular LaTeX."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "templates/enterprise/projects/site-engineer-employment"
NEEDED = {
    "employer_name", "employee_name", "employee_address", "designation",
    "agreement_kind", "service_start", "effective_from", "pay_period",
    "duty_station", "salary_components", "gross_pay", "vehicle_servicing"
}
ESC = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}",
       "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
       "_": r"\_", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def tex_escape(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 300:
        raise ValueError("Missing or overlong required employee field")
    if any(c in value for c in "\n\r\x00"):
        raise ValueError("Employee fields must be single-line text")
    return "".join(ESC.get(ch, ch) for ch in value.strip())


def money(amount: int) -> str:
    if type(amount) is not int or amount < 0 or amount > 100_000_000:
        raise ValueError("Salary components must be nonnegative whole NPR amounts")
    return f"{amount:,}"


def validate(data: dict) -> tuple[list[dict], dict]:
    if not isinstance(data, dict) or (set(data) - {"letterhead_pdf"}) != NEEDED:
        raise ValueError("Employee input must match the documented schema exactly")
    if tex_escape(data["designation"]).casefold() != "site engineer":
        raise ValueError("This role-specific contract is only for Site Engineer")
    if data["agreement_kind"] not in ("initial", "revision"):
        raise ValueError("Choose initial or revision agreement")
    for key in NEEDED - {"gross_pay", "salary_components", "vehicle_servicing", "agreement_kind"}:
        tex_escape(data[key])
    rows = data["salary_components"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 12:
        raise ValueError("Give 1-12 itemized salary components")
    names, total = set(), 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"name", "amount"}:
            raise ValueError("Each pay row requires name and amount")
        label = tex_escape(row["name"]).casefold()
        if label in names:
            raise ValueError("Duplicate pay category")
        names.add(label)
        money(row["amount"])
        total += row["amount"]
    if "basic salary" not in names or total <= 0 or total != data["gross_pay"]:
        raise ValueError("Basic salary is mandatory; salary items must sum exactly to gross_pay")
    vehicle = data["vehicle_servicing"]
    if not isinstance(vehicle, dict) or set(vehicle) != {"enabled", "quarterly_cap"}:
        raise ValueError("Vehicle benefit must include enabled and quarterly_cap")
    if type(vehicle["enabled"]) is not bool:
        raise ValueError("Vehicle benefit enabled must be Boolean")
    money(vehicle["quarterly_cap"])
    if vehicle["enabled"] and vehicle["quarterly_cap"] == 0:
        raise ValueError("Vehicle benefit cap must be positive when enabled")
    if "letterhead_pdf" in data:
        source = Path(data["letterhead_pdf"]).expanduser().resolve()
        if not source.is_file() or source.suffix.lower() != ".pdf" or source.read_bytes()[:5] != b"%PDF-":
            raise ValueError("Provide an existing, authorized PDF letterhead")
    return rows, vehicle


def config_from(data: dict, rows: list[dict], vehicle: dict) -> str:
    labels = {
        "EmployerName": data["employer_name"],
        "EmployeeName": data["employee_name"],
        "EmployeeAddress": data["employee_address"],
        "EmployeeRole": data["designation"],
        "ContractSubtitle": "First Month Remuneration" if data["agreement_kind"] == "initial"
                            else "Monthly Remuneration Revision",
        "ServiceStart": data["service_start"],
        "EffectiveDate": data["effective_from"],
        "PayPeriod": data["pay_period"],
        "DutyLocation": data["duty_station"]
    }
    lines = [r"\newcommand{" + "\\" + k + "}{" + tex_escape(v) + "}" for k, v in labels.items()]
    salary_lines = "".join(tex_escape(r["name"]) + " & " + money(r["amount"]) + r"\\" + "\n"
                           for r in rows)
    lines.extend([
        r"\newcommand{\PayRows}{" + "\n" + salary_lines + "}",
        r"\newcommand{\GrossPay}{" + money(data["gross_pay"]) + "}",
        r"\newif\ifvehiclebenefit",
        r"\vehiclebenefittrue" if vehicle["enabled"] else r"\vehiclebenefitfalse",
        r"\newcommand{\VehicleCap}{" + money(vehicle["quarterly_cap"]) + "}",
        r"\newcommand{\VehicleInterval}{three}"
    ])
    return "\n".join(lines) + "\n"


def materialize(data: dict, out: Path, compile_pdf: bool = False) -> Path:
    rows, vehicle = validate(data)
    out = out.resolve()
    if out.is_relative_to(ROOT):
        raise ValueError("Private employee output cannot be inside public Git source")
    if out.exists():
        raise FileExistsError("Refusing to overwrite an existing employee LIVE project")
    shutil.copytree(TEMPLATE, out, ignore=shutil.ignore_patterns("*.aux", "*.log", "*.pdf", "*.fls", "*.fdb_latexmk", "*.synctex.gz"))
    (out / "project_config.tex").write_text(config_from(data, rows, vehicle), encoding="utf-8")
    if "letterhead_pdf" in data:
        (out / "assets").mkdir(exist_ok=True)
        shutil.copy2(Path(data["letterhead_pdf"]), out / "assets/letterhead.pdf")
    if compile_pdf:
        if not shutil.which("latexmk"):
            raise RuntimeError("Missing latexmk / TeX Live compiler")
        run = subprocess.run(["latexmk", "-pdf", "-no-shell-escape",
                              "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                             cwd=out, capture_output=True, text=True, timeout=120)
        if run.returncode or not (out / "main.pdf").is_file():
            raise RuntimeError("Failed to compile main.tex:\n" + run.stdout[-2200:])
    return out


def selftest() -> None:
    sample = json.loads((TEMPLATE / "sample_employee.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        folder = materialize(sample, Path(tmp) / "employee")
        assert (folder / "main.tex").is_file()
        assert len(list((folder / "sections").glob("*.tex"))) == 9
        assert "20,000" in (folder / "project_config.tex").read_text()
        altered = json.loads(json.dumps(sample))
        altered["gross_pay"] += 1
        try:
            materialize(altered, Path(tmp) / "incorrect")
        except ValueError:
            pass
        else:
            raise AssertionError("Mismatched salary component total was accepted")
    print("PASS Site Engineer template, 9 sections, private output and wage arithmetic")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        selftest()
    elif args.data and args.out:
        folder = materialize(json.loads(args.data.read_text(encoding="utf-8")), args.out, args.compile)
        print("Created working project at", folder)
    else:
        parser.error("Supply --data /private/person.json --out /private/project or --self-test")


if __name__ == "__main__":
    main()
