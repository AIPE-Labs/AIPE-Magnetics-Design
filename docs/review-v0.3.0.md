# Review before the v0.3.0 release

A review of this repository against the AIPE goals (open, provenance-tracked data; a design flow that
runs end to end; usable by agents and readable by people), made before the first tagged release. It records
what works, what was fixed for the release, and what is left with a proposal. Every statement marked
"run" was executed for this review against `aipe-magnetics-database` v0.3.0.

## What works end to end (run)

- **Database to a designed component.** `demo dab-10kw` reads N87 and five TDK cores from the Database and
  sizes the 10 kW, 800 V : 400 V, 100 kHz DAB transformer: E 65/32/27, 21 : 10 turns, core 21.54 W + copper
  17.68 W = 39.22 W, with every source and assumption in the result. `examples/database_to_design.py` refits
  Steinmetz parameters from the Princeton MagNet N87 measurements in the Database and reproduces the catalogue
  estimate.
- **Waveform-informed design.** Sampled or synthesised converter waveforms give exact RMS and harmonics, flux
  from the voltage integral, iGSE core loss, per-layer Dowell copper loss, ranked integer-turn candidates and an
  AIPE-Core Engineering State that the released Core validator accepts.
- **Agent entry points.** The MCP server lists 13 tools that equal the Python API one to one; the CLI commands
  quoted in the README and `docs/api.md` run; both plugins pass the structural checks.
- **Verification.** 58 checks pass and equal the bundled evidence; every level claimed in `aipe.yaml` is
  backed by a record.
- **Ecosystem contracts.** With AIPE-Core v0.1.0, AIPE-Registry v0.1.0 and the Database v0.3.0 checked out,
  the released validators accept the exported state and this repository's `aipe.yaml`. CI now runs this.

## Fixed for this release

| Problem | Fix |
| --- | --- |
| A result computed outside the validity window of its parameter set (`policy="warn"`, the default of the design and validation functions) was reported as `verified`, `in_verified_range: true`. Example: `validate` at 0.267 T with a parameter set valid to 0.2 T. | The API marks any result that carries an `out_of_domain` warning as `out_of_range` / `in_verified_range: false` and says the value is an extrapolation. Regression test added. |
| `measurement_requests` reported a hard-coded `L1 verified` although no evidence record exists. | It reports what the evidence registry says (`L0`). |
| The Registry external test had never been executed; run for real it failed (`unknown_dependency`). | Test corrected; a CI job runs the four external tests against the released repositories and fails if they skip. |
| Two tests needed a waveform file on one Windows disk. | A generated HDF5 file in the same layout now drives the full import-to-design path. The tests on the executed file read `AIPE_DAB_WAVEFORM_FILE`. |
| The FEA / thermal / CAD workflow layer (about 4,300 lines) was executed by no test. | One smoke test runs the default workflow end to end. |
| Bundled evidence was produced before the repository split and contained an absolute path of the maintainer's machine. | Regenerated here; notes are path-independent. |
| Documentation described the pre-split repository: wrong plugin and marketplace names in `docs/plugins.md`, a `CONTRIBUTING.md` for data records with commands that do not exist, "evidence file missing" narratives, bundled-data claims in `docs/sources.md`, a wrong repository layout. | Corrected. |
| Design imported two private names of the Database package (`database.query._q`, `database.materials._catalog`). | Removed. |
| CI ran every job twice on a pull request. | `push` runs are limited to `main`. |

## Left open, with a proposal

### 1. Design sees 11 materials; the Database holds more than a thousand

Every design function reads `Catalog.default()`, the Database's small curated catalogue: 11 materials (all MnZn
ferrites, one synthetic) and 6 cores, of which five are offered to the designer. The Database's canonical store
(`aipe_magnetics_database.api`, 1164 materials) is used by nothing in `src/`; only
`examples/database_to_design.py` touches it. Bsat and Curie data exist for N87, 3C90 and 3C94 only, so in
practice the automated design chooses among a handful of cores in N87.

This is the largest gap between the goals and the code: the open data exists but the design flow cannot use it.
Proposal (needs a decision shared with AIPE-Magnetics-Database): the Database publishes one documented
"design view" in its public API that returns, for a material, the saturation points and loss parameter sets
with ranges and provenance, built from the canonical store; Design then reads only that view. Until the
Database offers it, widening Design's selection would mean deriving parameters here, which is the duplication
this split was meant to end.

### 2. The data boundary is a convention, not a seam

`data_access.py` is described as the single seam to the Database, but 83 source files import the Database
package directly. Most of that is shared vocabulary (errors, `Quantity`, result envelopes) and is harmless.
The real bypasses are: `Catalog` read directly in seven modules (four identical private helpers), record classes
from `data.records` in nine modules, two source adapters, and Database tooling re-exposed by the Design CLI
(`schema validate|migrate|export`, `import json`, `materials list|get`).

Proposal: re-export `default_catalog()`, the five record classes and the two adapters from `data_access`, replace
the direct imports, and add a test that fails on any `aipe_magnetics_database.data.*` or `.database.*` import
outside `data_access.py`. Roughly a day of mechanical work; left out of this release because it touches about
twenty modules.

### 3. Database checks live in the Design verification suite

`verification/checks/check_data.py` and `check_sources.py` (781 lines, 2 of the 14 capability groups) test the
Database package from inside Design. Two of their records pass vacuously here because the files they compare
are in the Database repository (`mirror_compared: false`, `repository_examples: 0`). Proposal: move both
modules to AIPE-Magnetics-Database and regenerate the evidence in both repositories. Not done now because it
changes the Database's release content.

### 4. Hard-coded values that the Database already holds

Bobbin and insulation thermal conductivity (0.3 and 0.12 W/m/K, three places), copper density (8933 kg/m3) and
an air conductivity default of 0.03 W/m/K that disagrees with the Database's 0.0263. Proposal: read them
through `physical_property`; the air value changes thermal results slightly, so the evidence must be
regenerated with it.

### 5. Code without an entry point

- `workflows/dab_transformer.run_dab_workflow` and what only it reaches (`design/transformers/candidate.py`,
  `optimisation/`, `simulation/`, `geometry/export.py`, `visualisation/`, `state/`): runs, selects E 65/32/27
  20 : 10, writes mesh, field and thermal artifacts, but has no CLI, API or MCP entry, no evidence record, and
  its numbers are compared with no reference. It is labelled experimental in `docs/limitations.md`. Note that it
  selects 20 : 10 turns while the public demo and the waveform-informed design select 21 : 10: three design paths
  for the same converter. Proposal: decide which path AIPE-Workflows calls and retire or merge the others.
- `design/inductors/gapped.py` (370 lines) and `InductorSpec` are imported by nothing; the API uses
  `engineering/inductor.py`. Proposal: delete or wire up.
- `models/datadriven/` (2,700 lines) is reachable only through the Python adapter and the verification checks,
  and its bundled model is a synthetic surrogate. Real inference needs `magnethub` or `torch`, which no recorded
  run exercises. It is honest about this in `docs/models.md`; it is simply not part of the design flow yet.
- A dozen public functions are referenced nowhere (`formulas.field_strength`, `saturation.screening_to_json`,
  `winding.winding_to_json`, ...). Proposal: remove in the boundary clean-up of item 2.
- `verification/evidence/v0.2.0.json` and `docs/*-v0.2.0.md` are records of the pre-split package; they still
  ship and contain paths of the machine that produced them. Proposal: remove them from the package after the
  owner agrees (they stay in the Git history).

### 6. Optional tools are untested

`gmsh`, `cadquery`, `matplotlib` and `torch` paths are executed by no test and no CI job; only the "not
installed" branches are. Proposal: one CI job that installs `[viz,mesh,cad]` and runs the workflow smoke test.

### 7. The executed converter waveforms are not available here

`docs/waveform-informed-design.md` reports numbers from an ngspice run whose file is not in this repository.
The generated-input test reproduces the design to about 0.1 W, but not the file's own numbers. What is
needed: AIPE-Workflows publishes that `waveforms.h5` (with its SHA-256) as a release asset or example file;
the two external tests then run in CI by setting `AIPE_DAB_WAVEFORM_FILE`.

### 8. Names from before the split

The CLI help and `info` print `aipe-magnetics`, the MCP server identifies itself as `aipe-magnetics`, the
capability ids are `aipe.magnetics.*` and several documents use the old command name (the alias works). The
manifest shares three capability names with the Database manifest (`magnetics-material-lookup`,
`magnetics-mcp-server`, `magnetics-agent-plugin`); the Registry reports them as warnings. Renaming any of
these changes what agents and AIPE-Workflows address, so it is a cross-repository decision, not a clean-up.

## The `aipe_magnetics` import name

`aipe_magnetics` is kept in this release as a deprecation shim: `import aipe_magnetics.<module>` resolves to the
same module object in `aipe_magnetics_design` (or `aipe_magnetics_database` for data modules) and emits a
`DeprecationWarning` naming the new path. It will be removed in 0.5. New code imports
**`aipe_magnetics_design.api`**; the shim is installed by the `aipe-magnetics-design` distribution, not by the
Database.
