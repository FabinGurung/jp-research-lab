# Site Engineer — reusable modular employment and salary agreement

This is the Enterprise Writing role-specific source profile for future site-engineer employees, not an academic thesis template. It preserves the historical fourteen-type v3 authority and does not replace their original pinned TeX sources.

Each working document is an ordinary unzipped folder with ONE compilation entrypoint: main.tex. Employer and employee variables are in project_config.tex. Human-facing clauses are separately editable under sections/. When available, use an authorized company letterhead PDF at assets/letterhead.pdf; it is repeated on every page. Company-owned branding and real employee identities belong only in restricted Drive, never public Git.

For a new employee, use the private-source materializer:
  python3 scripts/document_engineering/create_site_engineer_agreement.py --data /private/employee.json --out /private/new-employee --compile

The public sample_employee.json contains fictional names and data solely to test the source layout; it is not an employer payroll policy. Run python3 scripts/document_engineering/create_site_engineer_agreement.py --self-test for basic structure and arithmetic validation. The owner chooses whether the contract is an initial employment agreement or a subsequent remuneration revision using agreement_kind.

The script creates NEW working folders and refuses to overwrite existing output. For a future revision to an existing person's working documents, preserve canonical Google Drive LIVE file IDs and PRE/POST snapshots rather than issuing new LIVE IDs. Keep research, statutory comparisons, inconsistencies, user suggestions and QA in a separate native Google Doc; do not insert internal workflow language, signatures or source metadata into the employee-facing PDF.

Statutory wage components and later minimum-wage changes require validation against the applicable time period and payroll source. A correct total does not in itself prove that a proposed basic/allowance classification meets every Nepal labour-law requirement.
