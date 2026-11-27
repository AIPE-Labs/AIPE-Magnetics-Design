# NOTICE: vendored AIPE-Core schemas (pinned copies)

Source repository: https://github.com/AIPE-Labs/AIPE-Core
Upstream release: v0.1.0, commit a8481c60ddfdced685067227fb16ca534be3eb5b (committed 2026-11-27T20:52:46+00:00)
Upstream paths: `schemas/*.schema.json` and `examples/dab-10kw/engineering-state.json`
Licence: MIT (text reproduced verbatim below from the upstream `LICENSE` file at that commit)

These files are byte-exact copies of the blobs at the upstream release tag `v0.1.0` (LF line
endings, as stored in Git), pinned for **offline validation**. The `$id` URLs they carry
(`https://raw.githubusercontent.com/AIPE-Labs/AIPE-Core/v0.1.0/schemas/...`) are the addresses of
the same files in that release. `aipe_magnetics_design.integrations.aipe_core` resolves every `$id`
to the local copy and never downloads a schema. To refresh the copies, re-run
`git show <tag>:<path>` from an AIPE-Core checkout and update the pinned SHA-256 digests in
`state.py` (`VENDORED_SHA256`); the verification check `integration.core-example-validates` fails
when the copies drift from the pins.

## Reproduced source code (same licence)

In addition to the vendored files, `state.py` in the parent directory reproduces a substantial
portion of the upstream file `scripts/validate.py` at the same commit under this MIT licence:
`validate_engineering_state` is a near-verbatim port of `validate_state` (error wording kept so
that both validators can be compared line by line), together with `_walk`, `_offline_only`,
`state_validator` and the strict JSON loading rules (`load_json`: duplicate keys and non-finite
numbers rejected). `state.py` carries the copyright and licence notice in its header; this file
holds the full licence text. The `__main__.py` command line mirrors the upstream `main()` output
format (`PASS`/`FAIL` lines) but is an independent implementation.

| File | SHA-256 of vendored bytes |
| --- | --- |
| `common.schema.json` | `c5fe8ce5c9788ce7ae18a6ff98fd0487dacc421c46927054ec12975f3083d411` |
| `control.schema.json` | `a664230a34a060e3abb2b1c99ee4e377ca12a726474633996a7604f67f3ec788` |
| `converter.schema.json` | `02187811c201b539d89a73c57f39e758724c25795de5be89430182b571f66bac` |
| `engineering-state.schema.json` | `f85830ec323bd4cbeb75c09a10d27753264410027708709e7ab4d2757fa1dd6c` |
| `evidence.schema.json` | `b50351bd4b7d8dadd89ac8c010b47e677a112241e9214c2c4776fa5ef97c9a0c` |
| `magnetics.schema.json` | `dca7ad8d50ea38922249e672d0385f0aca219c108ada4587fe75969a48f21d74` |
| `operating-point.schema.json` | `dfc1366b39f573a72c7b2ea4cc82b3fd52a53b9b5385d4581fbc3487490b414a` |
| `passive.schema.json` | `ac73e0dea30e0d4475ee88074942a1b70c29c54ed06a30292f8ef49827c911f5` |
| `project.schema.json` | `97ae1d0a582b0fefd00ef29a0c74de306fb3868cc409238480142c093141b581` |
| `requirements.schema.json` | `19491435fab4cb2181d907d3222d3302fdcc3793e93deb92b52d1361eda223b8` |
| `semiconductor.schema.json` | `4bf327be4e093188e2eca067a9902ad8447e2f86c1723c006fe7acebe1a408f4` |
| `simulation.schema.json` | `5b119de5b9520653e20edd0c812970de812e041f1586fc5afb66c5bcd3816d2e` |
| `thermal.schema.json` | `cb0dc6a588aa55a266544c682b4fb675ece5a54365e194a3a0901ffcf9005ae0` |
| `validation.schema.json` | `153accac909e56f15649cd4d2b8a3de5498a3486adf82a3a01715c5d9f5c6f28` |
| `examples/dab-10kw-engineering-state.json` | `0945d3a69727d72c4b47061b8cd52f6f1e422d63838ffe80c3a5a5480e4b15f0` |

## Upstream LICENSE (MIT), copied verbatim

```text
MIT License

Copyright (c) 2026 AIPE contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
