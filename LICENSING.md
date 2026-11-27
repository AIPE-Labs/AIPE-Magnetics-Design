# Licensing and data rights

## This repository

The code, documentation, schemas, skills and plugin files of AIPE-Magnetics-Design are released
under the **MIT License** ([LICENSE](LICENSE), Copyright (c) 2026 AIPE contributors). The same
identifier is declared in `pyproject.toml`, `aipe.yaml` and both plugin manifests.

The MIT licence covers this repository only. It does not relicense magnetic data, which this
repository does not store: every record read from `aipe-magnetics-database` keeps the licence of
its source, and results carry those sources in their envelope.

## Third-party components

| Component | Licence | How it is used |
| --- | --- | --- |
| AIPE-Core schemas, release v0.1.0 (pinned copy in `src/aipe_magnetics_design/integrations/aipe_core/schemas/`) and the contract checks of Core's `scripts/validate.py` re-implemented in `integrations/aipe_core/state.py` | MIT | offline compatibility validation; NOTICE file and the `state.py` header carry the copyright, release commit and attribution |
| AIPE-Registry manifest schema, release v0.1.0 (pinned copy in `src/aipe_magnetics_design/integrations/aipe_registry/schema/`) | MIT | offline manifest validation; NOTICE file carries the copyright and commit |
| numpy, scipy, h5py | BSD-3-Clause | runtime |
| pydantic, jsonschema, referencing, PyYAML, mcp | MIT | runtime / optional |
| torch (optional) | BSD-3-Clause | optional data-driven backend (`[torch]`) |
| matplotlib (optional) | Matplotlib licence (PSF-based, BSD-compatible) | optional plots (`[viz]`) |
| cadquery (optional) | Apache-2.0 | optional CAD export (`[cad]`); imported only when the user installs it |
| gmsh (optional) | GPL-2.0-or-later | optional meshing (`[mesh]`); never bundled, imported only when the user installs it |
| Princeton MagNet (`PrincetonUniversity/magnet`) | MIT | measurements and the derived Steinmetz fits are read from `aipe-magnetics-database`; nothing from it is stored here (see `docs/sources.md`) |
| Paderborn `mag-net-hub` | MIT | optional model backend through the `magnethub` package; no weights vendored |
| Paderborn `materialdatabase` | GPL-3.0 | **no code copied, no data bundled**; adapter reads a user checkout; records produced from it carry `license: GPL-3.0` |
| MagNet Challenge 2 (`minjiechen/magnetchallenge-2`) | none published | reference and user-supplied import only |
| Magnetic data (MAS, Princeton MagNet, Paderborn LEA, HEFMAG, ...) | per source | **not stored here**: read from the separate `aipe-magnetics-database` package, which records each source licence ([AIPE-Magnetics-Database/LICENSING.md](https://github.com/AIPE-Labs/AIPE-Magnetics-Database/blob/main/LICENSING.md)) |
| TDK / EPCOS datasheets | manufacturer copyright | individual typical values transcribed with page/table locators as evidence; documents are referenced, never copied |

Each source evidence record declares its known licence, or `NOASSERTION` when the source publishes none
(this marks third-party material such as datasheets and papers, never this repository's own code). Public availability is
not redistribution permission. Preserve manufacturer notices and measurement partner terms;
reference restricted source documents instead of copying them.
