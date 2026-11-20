# One input, four workflows

Separate synthetic Fabin Gurung experiment. Google Docs and Google Sheets are the human backend; GitHub Actions generates the outputs and GitHub Pages presents them. No SQL service is used. The existing thesis, manuscript pins, old source packages, existing pages and peer repositories are preserved.

## Human editing

Edit the companion Google Sheet's **Inputs!B2:B28** values. Keep the parameter names and units intact. The other four tabs contain formula-based review views. The companion Google Doc supplies the unchanged title, general objective, seven specific objectives, methodology and limitations.

The two NEW synthetic sources are identified in `google-sources.json`. They inherited the existing parent folder's link-reader permission. The setup neither changed sharing nor requested new credentials. The published experiment has an **Open inputs** link.

## Refresh and reproduce

Run **Deploy JP R&D control portal** on `main` to read both current Google exports, calculate and deploy. No recurring schedule was added. Editing a source does not instantly change Pages; a successful refresh/build is required.

The source reader fetches each export twice, requires identical bounded payloads, validates parameter names, numeric types, units and the seven objective paragraphs, and records semantic/input and export hashes. Link-based exports do not expose native revision IDs; the provenance explicitly records that limit. A failed read or validation blocks deployment without silently claiming an older snapshot is fresh. The reader never edits the Google sources.

Python 3.12 and Node 22 or later:

    python experiments/fabin-four-workflows/sync_google.py
    python -m unittest discover -s experiments/fabin-four-workflows -p test_engine.py -v
    FABIN_SCHEDULING_CHECKOUT=/path/to/pinned-scheduling-checkout python experiments/fabin-four-workflows/build_public.py /tmp/fabin-public
    python experiments/fabin-four-workflows/latex.py --academic /tmp/fabin-experiment-private/academic.json --results /tmp/fabin-public/results.json --out /tmp/fabin-experiment-private/latex
    python scripts/latex/check_modular_project.py /tmp/fabin-experiment-private/latex
    python scripts/build_site.py --out dist

Pin the scheduling checkout to `49f69e76a85eec9737f704691cc69c88aad62818`. The peer methods and exact contract/source pins are in `peer-methods.json`. Only native CPM is executed from a peer repository. CAD, structural and concrete QTO are bounded R&D adapters following the peer methodology; full CAD/OpenSees/cost engines are not presented as integrated runtimes.

The numerical seed remains available for offline source tests. The Pages publishing workflow explicitly performs a fresh Google read before generation.

## Modular LaTeX

`latex.py` assembles the actual Google Doc narrative and numerical results into `main.tex`, `title.tex` and four chapter modules. It references the existing canonical academic style, v2.6.4 / blob `6deb30ec415fd386de104c0b7248eb9ea8b98ece`, without copying or changing it. The initial populated, browsable source is saved in the experiment's dedicated Drive folder.

Actions also regenerates and structurally checks the modular source in its temporary working directory. It does not overwrite the preserved Drive source or the current thesis automatically. New Drive output publication is a separate controlled write. No thesis sequence or production CURRENT is allocated or changed. No PDF compilation or university-format certification is inferred from structural source lint.

## Scope

Four columns, four perimeter beams, one slab; symmetric unfactored gravity, linear-elastic no-sway portal frames and fixed bases. The 45-degree slab tributary partition and clear-face/downstand quantity convention are explicit. Beam stiffness uses the gross full rectangular section; rigid offsets, slab T-action, cracked stiffness and physical shell behavior are omitted. MDM is checked against independent closed-form slope-deflection.

One sequential crew, Saturday-off active work and calendar-day curing waits. Programme durations, rates and geometry are synthetic assumptions. Concrete subtotal only; BBS/steel, formwork, foundations, full cost and surveyed GIS remain unavailable. Retained wider SQL-specific thesis objectives are deferred rather than declared complete. This is not an approved building design or construction programme.

Only the allowlisted synthetic parameter/result projection reaches Pages. Raw Google Doc text is not uploaded as a public Actions artifact. The browser views inspect a dated result; they are not a second input authority.
