"""The DAB workflow records only what it executed: caller-supplied timestamps and verification levels that follow from the checks."""

from __future__ import annotations

import pytest

from aipe_magnetics_database.common.errors import InvalidInputError
from aipe_magnetics_design.workflows.dab_transformer import WorkflowOptions, build_verification_record, run_dab_workflow

PASSING = [{"kind": "detailed_constraints", "id": "detailed-constraints", "status": "pass", "violations": []},
           {"kind": "energy_balance", "id": "thermal-energy-balance", "status": "pass", "value": 1e-9},
           {"kind": "reference_comparison", "id": "fea-vs-analytical", "status": "recorded", "comparisons": {}}]


def _level(record, name: str):
    return next(lvl for lvl in record.levels if lvl.level == name)


def test_software_schema_level_follows_the_executed_validation():
    pending = build_verification_record(PASSING, schema_validated=None)
    assert _level(pending, "software_schema").status == "partial"
    passed = build_verification_record(PASSING, schema_validated=True)
    assert _level(passed, "software_schema").status == "passed" and "in this run" in _level(passed, "software_schema").statement
    failed = build_verification_record(PASSING, schema_validated=False)
    assert _level(failed, "software_schema").status == "failed"
    for record in (pending, passed, failed):
        assert "release-verification-v0.3.0" not in " ".join(lvl.statement for lvl in record.levels)


def test_numerical_level_is_never_claimed_passed_from_self_checks():
    record = build_verification_record(PASSING, schema_validated=True)
    numerical = _level(record, "numerical_physical")
    assert numerical.status == "partial" and "own checks" in numerical.statement
    failing = build_verification_record(PASSING + [{"kind": "electrothermal", "id": "x", "status": "fail"}], schema_validated=True)
    assert _level(failing, "numerical_physical").status == "failed"
    assert _level(record, "experimental").status == "not_performed" and record.manufacturing_readiness == "preliminary_design"


def test_workflow_requires_a_caller_supplied_timestamp(tmp_path):
    assert WorkflowOptions().created_at is None
    with pytest.raises(InvalidInputError, match="created_at"):
        run_dab_workflow(tmp_path, options=WorkflowOptions())


def test_default_dab_workflow_runs_end_to_end_without_optional_tools(tmp_path):
    """Smoke test of the experimental FEA / thermal / CAD workflow layer: the only test that executes it.

    It shows that the default 10 kW DAB specification runs from the database selection to a selected candidate and
    written artifacts with the built-in structured mesher (no gmsh, cadquery or matplotlib). It does not check the
    field or thermal numbers against any reference.
    """
    result = run_dab_workflow(tmp_path, options=WorkflowOptions(created_at="2026-11-27T00:00:00Z"))
    # "ok_with_warnings" when an optional tool (e.g. matplotlib for the plots) is not installed; nothing else may be reported
    assert result.status in ("ok", "ok_with_warnings"), result.errors
    assert all("is not installed" in message for message in result.errors), result.errors
    assert result.summary["feasible"] is True and result.summary["params"]["core"] == "core.tdk-e65-32-27"
    written = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert any(p.name == "spec.json" for p in written) and any(p.name == "database-selection.json" for p in written)
    assert len(written) > 10
