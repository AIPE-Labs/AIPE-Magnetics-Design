# Contributing

AIPE-Magnetics-Design holds models, design calculations and their verification. It stores **no magnetic
data**: materials, cores and measurements belong in
[AIPE-Magnetics-Database](https://github.com/AIPE-Labs/AIPE-Magnetics-Database) and are read here only
through that package (`aipe_magnetics_design.data_access`).

## Before opening a pull request

```sh
pip install -r requirements.txt && pip install -e ".[dev]"
python -m pytest -q
python -m aipe_magnetics_design.cli.main verify --output reports/verification --check-bundled
python tools/sync_plugin_skills.py --check
```

- A new model or design relation needs a declared validity domain, dimensional and invalid-input tests and a
  verification check (`src/aipe_magnetics_design/verification/checks/`) that states its level honestly. If
  the check set changes, a maintainer regenerates the bundled evidence with `verify --update-bundled`.
- Do not fabricate material properties, loss curves or measurements, and do not hard-code material data in
  this repository. Illustrative parameter sets must be labelled synthetic.
- Results must keep their envelope: values with units, assumptions, model identity, sources, verification
  status, warnings and limitations. Extrapolation is rejected or flagged, never silent.
- Documentation must not claim more than the code and the evidence support. Say what was executed and what
  was not.
- Optional third-party tools (gmsh, cadquery, torch, magnethub) stay optional imports; do not vendor them.

Changes are reviewed; contributions are accepted under the MIT licence of this repository
([LICENSE](LICENSE)).
