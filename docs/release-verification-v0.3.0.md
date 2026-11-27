# Release verification record - AIPE Magnetics Design 0.3.0

Run on 2026-11-27 for the tagged release, on the release branch of `AIPE-Labs/AIPE-Magnetics-Design`.
Host: Linux x86-64, Python 3.13.18, numpy 2.5.3, scipy 1.18.1, pydantic 2.13.5, jsonschema 4.26.0, h5py 3.16.0.
Dependencies at tagged releases: `aipe-magnetics-database` v0.3.0, AIPE-Core v0.1.0
(`a8481c60ddfdced685067227fb16ca534be3eb5b`), AIPE-Registry v0.1.0 (`96426e9d4f2e097a53b65fd783cb660be65b8a46`).
This record lists what was **actually executed**; anything under "Not executed" is not claimed. It replaces the
record of 2026-11-02 made on the migration branch before the repository moved.

## Executed

| Command | Result |
| --- | --- |
| `python -m pytest -q` | **760 passed, 7 skipped**. Skips: executed converter waveform file not supplied (2, `AIPE_DAB_WAVEFORM_FILE`), `AIPE_ECOSYSTEM_CHECKOUTS` not set (4, run separately in the next row), `magnethub` not installed (1). |
| `AIPE_ECOSYSTEM_CHECKOUTS=<dir> python -m pytest -q -m external tests/integrations` | **4 passed**: AIPE-Core's `scripts/validate.py` accepts the exported Engineering State; AIPE-Registry's `scripts/validate.py` accepts `aipe.yaml` together with the Core and Database manifests; the pinned schema copies equal the release files. |
| AIPE-Registry `scripts/validate.py` on Core + Database + this `aipe.yaml` | exit 0, no errors; 3 `duplicate_capability` warnings (names shared with the Database manifest, see `docs/review-v0.3.0.md`) |
| `aipe-magnetics-design verify --output <dir> --update-bundled` | **58 checks, 58 passed**, stable after re-run; bundled evidence `src/aipe_magnetics_design/verification/evidence/v0.3.0.json`, Markdown twin `docs/verification-report-v0.3.0.md` |
| `aipe-magnetics-design verify --check-bundled` | `bundled evidence matches this run` |
| `aipe-magnetics-design demo dab-10kw --output <dir>` | 10 kW / 100 kHz DAB transformer in N87, E 65/32/27, **21 : 10 turns, core 21.54 W + copper 17.68 W = 39.22 W**; the report is committed as `docs/demo-dab-10kw-report.md` |
| `python examples/database_to_design.py` | reads the Princeton MagNet N87 measurements from the Database; the refitted Steinmetz set reproduces the catalogue estimate (77,304.6 W/m^3 at 100 kHz / 100 mT) |
| `python -m aipe_magnetics_design.mcp.server --self-test` | 13 tools listed |
| `python tools/sync_plugin_skills.py --check` | skills in sync |
| `python -m build --wheel` | wheel builds (148 files, about 1.9 MiB unpacked); contains `LICENSE` and the `aipe_magnetics` shim |
| GitHub Actions, pull requests of this release | Linux, Windows and macOS with Python 3.10 and 3.12, the ecosystem job and the plugin job: see the run linked from the release commit |

## Not executed

- `claude plugin validate` and a Codex plugin installation: neither host CLI was available. Only the structural
  plugin checks in `tests/plugins` ran.
- The two tests on the executed ngspice converter waveform file: the file is not in this repository.
- Real `magnethub` or `torch` inference, `gmsh` meshing, `cadquery` export and `matplotlib` plots: the optional
  packages were not installed; only their "not installed" branches ran.
- No hardware was built or measured. All design numbers are analytical estimates.
