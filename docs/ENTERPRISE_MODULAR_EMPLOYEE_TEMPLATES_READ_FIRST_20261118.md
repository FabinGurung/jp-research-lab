# Enterprise Writing — modular working projects and Site Engineer employment profile

**Scope:** Enterprise Writing, not Academic Writing. These changes affect future **generated working projects** and an optional role-specific Site Engineer profile. They do not rewrite the approved fourteen v3 template assets, their Git blob pins, any academic shared format, or existing employees' Google Drive LIVE IDs.

## Source-of-truth hierarchy

- Canonical generic Enterprise type registry: registry/enterprise-document-types.json (exactly 14 types)
- Semantic control tower: controls/document-engineering/tower.json
- Existing generic types: controls/document-engineering/types/job-contract.json, salary-contract.json, and the other twelve
- Source renderer: scripts/document_engineering/engine_v3.py
- Site Engineer role profile: controls/document-engineering/role-profiles/site-engineer-employment.v1.json
- Reusable working-source prototype: templates/enterprise/projects/site-engineer-employment/
- Input materializer: scripts/document_engineering/create_site_engineer_agreement.py
- Company identity, employment amounts, signatories and original branding: **private employer-approved Google Drive**, not public GitHub

## 14 general document types

The v3 renderer reads the original immutable single-file type asset, validates its typed data, renders the approved wording, then **splits the generated working source into multiple editable files**. It compiles only main.tex (and retains the existing type-named PDF filenames to avoid breaking output references). An ordinary generated project is:

    job-contract/
    ├── README.md
    ├── main.tex
    ├── enterprise-v3.sty
    ├── sections/
    │   ├── 00_opening.tex
    │   ├── 01_section.tex
    │   ├── 02_section.tex
    │   └── ...
    ├── job-contract.pdf
    └── job-contract.qa.json

The QA JSON is an internal build artifact, NOT a reader-facing page, and may be retained separately from a small human working-source delivery. **No ZIP is the sole working representation.** Other registered types receive exactly this same source pattern, including one-file letters with meaningful sections. The v3 source assets are still one-file *inputs to the renderer*, not editable final projects.

Run all fourteen fictional checks:

    python3 scripts/document_engineering/engine_v3.py --self-test
    python3 scripts/document_engineering/engine_v3.py --demo-all --out /tmp/a9-enterprise-v3 --compile

## Site Engineer employee agreements

The role profile is a reusable **specialization** of the existing Employment Agreement and Salary Agreement document families; it is not a fifteenth canonical type and cannot accidentally replace the generic type router.

    site-engineer-employment/
    ├── README.md
    ├── main.tex
    ├── project_config.tex
    ├── sample_employee.json              # fictional, public-safe
    ├── assets/                           # letterhead.pdf, private working copy only
    └── sections/
        ├── 01_parties.tex
        ├── 02_pay.tex
        ├── 03_site_engineer_duties.tex
        ├── 04_work_schedule.tex
        ├── 05_leave_festivals.tex
        ├── 06_health_insurance.tex
        ├── 07_vehicle.tex
        ├── 08_termination_clearance.tex
        └── 09_signatures.tex

Input fields are employer, employee, address, designation Site Engineer, initial/revision agreement kind, service start, remuneration effective date, pay period, duty location, itemized monthly pay rows, exact gross monthly pay, optional vehicle-servicing benefit and optional **verified employer-owned** letterhead PDF filepath.

    python3 scripts/document_engineering/create_site_engineer_agreement.py \
      --data /private/employee_input.json \
      --out /private/employee_working_source --compile

The materializer rejects mismatched salary arithmetic, duplicate pay components, missing basic pay, unsupported roles, invalid file-based letterhead and an attempt to overwrite an existing folder. Employee data is *not* stored in the public repository. Authorized Fishtail Builders branding, if applicable, must be downloaded from its controlled Drive original into the working project's assets/letterhead.pdf.

All employer-issued contractual terms, employee eligibility and statutory pay categories must be checked against the relevant dates and private payroll records. A monthly total alone does not prove legal compliance; the source must not silently absorb statutory dearness/cost-of-living entitlements into unrelated reimbursements. Regulatory evidence, recommended edits, source conflicts and internal QA belong in a **separate native Google Doc**, not in the compiled contract.

## Existing employees and preservation

Existing person-specific LIVE Google Drive file IDs, working LaTeX folders, company-branded PDFs, and PRE/POST archives are **not modified by this repository release**. For an already employed person, preserve old bytes in PRE, update the *same* existing LIVE IDs, check the provider readback, then preserve POST. Create new person folders and new IDs for wholly new employees. Academic/structural/other enterprise projects remain out of scope.

## Technical QA

The workflow .github/workflows/enterprise-modular-delivery.yml runs the 14-type renderer's self-tests, compiles each project from main.tex, checks every source tree, verifies client-facing PDF text, compiles the fictional Site Engineer sample, and keeps a bounded QA artifact. Compiler success is not a signature or legal approval. Keep historical v3 release tags and original private ZIPs intact.
