# NOTICE: vendored AIPE-Registry capability manifest schema (pinned copy)

Source repository: https://github.com/AIPE-Labs/AIPE-Registry
Upstream release: v0.1.0, commit 96426e9d4f2e097a53b65fd783cb660be65b8a46 (committed 2026-11-27T20:58:49+00:00)
Upstream path: `schema/capability-manifest.schema.json`
Licence: MIT (text reproduced verbatim below from the upstream `LICENSE` file at that commit)

This file is a byte-exact copy of the blob at the upstream release tag `v0.1.0` (LF line
endings, as stored in Git), pinned for **offline validation**.
`aipe_magnetics_design.integrations.aipe_registry.manifest` validates `aipe.yaml`
against this local copy and re-implements the essential loader and semantic rules of the
upstream `scripts/registry.py` (MIT) under attribution; it never fetches schemas or URLs. To
refresh the copy, re-run `git show <tag>:schema/capability-manifest.schema.json` from an
AIPE-Registry checkout and update `VENDORED_SHA256` in `manifest.py`.

| File | SHA-256 of vendored bytes |
| --- | --- |
| `capability-manifest.schema.json` | `2e2ba26420a6d3b0332d2a486bd81b30e77fe69a4e3db5d787c3f89d70a0f6d2` |

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
