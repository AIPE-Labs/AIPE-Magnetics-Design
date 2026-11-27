# Current limitations

* `design_transformer` is analytical sizing with the `P / V` square-current approximation; the
  waveform-informed design adds exact waveform RMS / harmonics, 1-D leakage, per-layer Dowell and a
  network / lumped thermal estimate, still without finite-element, insulation or manufacturing analysis
  (the FEA / thermal-FE / CAD workflow layer in `workflows/`, `simulation/` and `geometry/` is experimental: it has
  no CLI, API or MCP entry point, no evidence record and a single smoke test). Results are design
  estimates with explicit assumptions.
* Core-loss models need a parameter set covering the operating temperature, frequency and flux
  density. `estimate_core_loss` and `evaluate_hysteresis` reject a point outside that window by default; the design
  and validation calculations continue with an `out_of_domain` warning and report `out_of_range`. Steinmetz/iGSE ignore DC bias and minor loops (flagged).
* The design functions read the Database's curated catalogue (11 materials, all MnZn ferrites, one of them
  synthetic; 6 cores), not its full canonical store of more than a thousand materials. Bsat / Curie data exist
  for N87, 3C90 and 3C94; the other materials carry MagNet-derived loss parameters only (reported as missing,
  not guessed).
* Jiles-Atherton ships an illustrative parameter set, not a material fit. Data-driven inference is
  demonstrated on a synthetic reference; real challenge models need the optional `magnethub` package.
* Verification checks are L1/L2 (software, numerical and physical consistency). No L3 experimental
  validation is bundled; optional external tests exist for users with the source datasets.

Limitations of the waveform-informed design are listed in
[waveform-informed-design.md](waveform-informed-design.md). The findings of the pre-release review, including
what is not wired up or not tested, are in [review-v0.3.0.md](review-v0.3.0.md).
