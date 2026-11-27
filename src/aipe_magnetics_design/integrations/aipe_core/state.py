# Portions of this module (``_offline_only``, ``state_validator``, ``_walk``, ``validate_engineering_state``
# and the strict JSON loading rules behind ``load_state``) reproduce ``scripts/validate.py`` of AIPE-Core
# at commit a8481c60ddfdced685067227fb16ca534be3eb5b, https://github.com/AIPE-Labs/AIPE-Core.
# Copyright (c) 2026 AIPE contributors. Licensed under the MIT License; the full licence text and the
# per-file pins are in ``schemas/v0.1.0/NOTICE.md`` next to this module.
"""Offline AIPE-Core Engineering State 0.1.0 schemas and contract validation.

This module makes the pinned AIPE-Core schemas (``schemas/v0.1.0/``; see ``NOTICE.md`` there for
the upstream commit, hashes and MIT licence) usable without network access and reproduces the
semantic contract checks of AIPE-Core ``scripts/validate.py`` (MIT, commit :data:`CORE_COMMIT`;
attribution header above and in ``NOTICE.md``).

The port is deliberately small and follows the upstream function ``validate_state`` step by step
(a substantial portion of that file is reproduced nearly verbatim); comments name the upstream
code each block ports so that a future Core change can be diffed against it. It is a *contract*
validator: it checks structure,
units, formats, unique entity ids, evidence references, provenance cycles and status
consistency. It cannot prove that a cited measurement exists, that an artifact is trustworthy or
that a design is physically adequate, and it never fetches or executes anything named by a state.

Conventions carried over from Core (``docs/metadata.md``):

* every physical scalar is ``{"value": <finite number>, "unit": <canonical SI spelling>}``;
* ids are lowercase with ``.``/``:``/``-`` separators and unique across all entities of a state;
* evidence kinds are ``assumption | analytical | simulation | measurement | source``; analytical
  evidence needs input evidence, simulation/measurement evidence need an artifact and a versioned
  tool attribution, provenance must be acyclic, rejected evidence supports nothing;
* a reported validation status needs a passing check of the matching kind, a passing physical
  check needs evidence of the same kind, any failing check forces the aggregate status ``failed``.
"""

from __future__ import annotations

import copy
import hashlib
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource

from aipe_magnetics_database.common.errors import DataIntegrityError, UnsupportedOperationError
from aipe_magnetics_database.common.jsonio import load as load_json

#: Upstream repository and commit the vendored schemas were copied from (see NOTICE.md).
CORE_REPOSITORY = "https://github.com/AIPE-Labs/AIPE-Core"
CORE_COMMIT = "a8481c60ddfdced685067227fb16ca534be3eb5b"
CORE_SCHEMA_VERSION = "0.1.0"
CORE_SCHEMA_BASE = "https://raw.githubusercontent.com/AIPE-Labs/AIPE-Core/v0.1.0/schemas/"
STATE_SCHEMA_ID = CORE_SCHEMA_BASE + "engineering-state.schema.json"

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas" / f"v{CORE_SCHEMA_VERSION}"
EXAMPLE_PATH = SCHEMA_DIR / "examples" / "dab-10kw-engineering-state.json"

#: SHA-256 of every vendored file (the committed LF blobs at CORE_COMMIT). The verification check
#: ``integration.core-example-validates`` fails if a copy drifts from these pins.
VENDORED_SHA256: dict[str, str] = {
    "common.schema.json": "c5fe8ce5c9788ce7ae18a6ff98fd0487dacc421c46927054ec12975f3083d411",
    "control.schema.json": "a664230a34a060e3abb2b1c99ee4e377ca12a726474633996a7604f67f3ec788",
    "converter.schema.json": "02187811c201b539d89a73c57f39e758724c25795de5be89430182b571f66bac",
    "engineering-state.schema.json": "f85830ec323bd4cbeb75c09a10d27753264410027708709e7ab4d2757fa1dd6c",
    "evidence.schema.json": "b50351bd4b7d8dadd89ac8c010b47e677a112241e9214c2c4776fa5ef97c9a0c",
    "magnetics.schema.json": "dca7ad8d50ea38922249e672d0385f0aca219c108ada4587fe75969a48f21d74",
    "operating-point.schema.json": "dfc1366b39f573a72c7b2ea4cc82b3fd52a53b9b5385d4581fbc3487490b414a",
    "passive.schema.json": "ac73e0dea30e0d4475ee88074942a1b70c29c54ed06a30292f8ef49827c911f5",
    "project.schema.json": "97ae1d0a582b0fefd00ef29a0c74de306fb3868cc409238480142c093141b581",
    "requirements.schema.json": "19491435fab4cb2181d907d3222d3302fdcc3793e93deb92b52d1361eda223b8",
    "semiconductor.schema.json": "4bf327be4e093188e2eca067a9902ad8447e2f86c1723c006fe7acebe1a408f4",
    "simulation.schema.json": "5b119de5b9520653e20edd0c812970de812e041f1586fc5afb66c5bcd3816d2e",
    "thermal.schema.json": "cb0dc6a588aa55a266544c682b4fb675ece5a54365e194a3a0901ffcf9005ae0",
    "validation.schema.json": "153accac909e56f15649cd4d2b8a3de5498a3486adf82a3a01715c5d9f5c6f28",
    "examples/dab-10kw-engineering-state.json": "0945d3a69727d72c4b47061b8cd52f6f1e422d63838ffe80c3a5a5480e4b15f0",
}

#: JSON Schema formats the Core validator relies on (Core: ``state_validator`` required_formats).
REQUIRED_FORMATS = frozenset({"date-time", "uri", "uri-reference"})


def _offline_only(uri: str) -> Resource:
    """Core ``_offline_only``: unknown ``$ref`` targets are errors, never downloads."""
    raise NoSuchResource(ref=uri)


def vendored_files() -> list[Path]:
    """The vendored schema files and example, in deterministic order."""
    return [SCHEMA_DIR / name for name in sorted(VENDORED_SHA256)]


def verify_vendored_integrity() -> dict[str, str]:
    """Return ``{relative name: sha256}`` of the vendored files; raise if any pin is violated."""
    digests: dict[str, str] = {}
    for name, expected in sorted(VENDORED_SHA256.items()):
        path = SCHEMA_DIR / name
        if not path.is_file():
            raise DataIntegrityError(f"vendored AIPE-Core file missing: {name}", details={"path": str(path)})
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise DataIntegrityError(f"vendored AIPE-Core file {name} differs from the pinned upstream blob",
                                     details={"expected_sha256": expected, "actual_sha256": actual})
        digests[name] = actual
    return digests


@lru_cache(maxsize=1)
def _schemas() -> tuple[dict[str, Any], ...]:
    """Load and check every vendored ``*.schema.json`` (Core ``state_validator``, first lines)."""
    schemas = tuple(load_json(path) for path in sorted(SCHEMA_DIR.glob("*.schema.json")))
    if len(schemas) != 14:
        raise DataIntegrityError(f"expected 14 vendored AIPE-Core schemas, found {len(schemas)}",
                                 details={"schema_dir": str(SCHEMA_DIR)})
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
    return schemas


def core_schema_ids() -> list[str]:
    return [schema["$id"] for schema in _schemas()]


def load_core_schemas() -> Registry:
    """Registry mapping each logical ``$id`` to the vendored resource; unknown ids raise NoSuchResource."""
    # Core: Registry(retrieve=_offline_only).with_resources(($id, Resource.from_contents(schema)) ...)
    return Registry(retrieve=_offline_only).with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in _schemas())


@lru_cache(maxsize=1)
def state_validator() -> Draft202012Validator:
    """Core ``state_validator``: engineering-state schema bound to the offline registry and format checker."""
    schemas = _schemas()
    state = next(schema for schema in schemas if schema["$id"].endswith("/engineering-state.schema.json"))
    checker = FormatChecker()
    if not REQUIRED_FORMATS.issubset(checker.checkers):
        missing = sorted(REQUIRED_FORMATS - set(checker.checkers))
        raise UnsupportedOperationError(
            "JSON Schema format validators are unavailable: " + ", ".join(missing) + "; install jsonschema[format]",
            details={"missing_formats": missing})
    return Draft202012Validator(state, registry=load_core_schemas(), format_checker=checker)


def _walk(value: Any, path: str = "$") -> Iterator[tuple[str, Any]]:
    """Core ``_walk``: every node with its JSON path; extension payloads are not interpreted."""
    yield path, value
    if isinstance(value, dict):
        for key, item in value.items():
            if key != "extensions":
                yield from _walk(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk(item, f"{path}[{index}]")


def validate_engineering_state(state: Any) -> list[str]:
    """Return Core contract errors for ``state`` (``[]`` means structurally valid; no physical claim).

    Port of AIPE-Core ``scripts/validate.py::validate_state`` at :data:`CORE_COMMIT`. Error strings
    keep the upstream wording so the two validators can be compared line by line.
    """
    validator = state_validator()
    errors = [f"{error.json_path}: {error.message}"
              for error in sorted(validator.iter_errors(state), key=lambda e: e.json_path)]
    if errors:
        return errors

    # Core: nested ``finite`` - JSON Schema treats host-language infinities as numbers; catch them too.
    def finite(value: Any, path: str = "$") -> None:
        if isinstance(value, float) and not math.isfinite(value):
            errors.append(f"{path}: number must be finite")
        elif isinstance(value, dict):
            for key, item in value.items():
                finite(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                finite(item, f"{path}[{index}]")
    finite(state)

    # Core: entity id uniqueness across state, project, converter, operating points, constraints,
    # components, runs, checks and evidence.
    entities = [state, state["project"], state["converter"],
                *state["requirements"].get("operating_points", []),
                *state["requirements"].get("constraints", []),
                *state["semiconductors"], *state["magnetics"], *state["passives"],
                *state["simulation"]["runs"], *state["validation"]["checks"],
                *state["evidence"]]
    seen: set[str] = set()
    for entity in entities:
        identifier = entity["id"]
        if identifier in seen:
            errors.append(f"Duplicate entity id: {identifier}")
        seen.add(identifier)

    # Core: evidence reference resolution, rejected evidence, physical quantities need evidence_refs.
    evidence = {item["id"]: item for item in state["evidence"]}
    for path, value in _walk(state):
        if not isinstance(value, dict):
            continue
        references = value.get("evidence_refs", [])
        if path.endswith(".provenance"):
            references = value["inputs"]
        for reference in references:
            if reference not in evidence:
                errors.append(f"{path}: unknown evidence reference {reference}")
            elif evidence[reference]["review_status"] == "rejected":
                errors.append(f"{path}: rejected evidence {reference}")
        # At least the enclosing domain object must trace physical quantities.
        physical = any(isinstance(item, dict) and set(item) == {"value", "unit"} for item in value.values())
        if physical and not references:
            # Semiconductor ratings inherit their component's evidence_refs.
            if not path.endswith(".ratings"):
                errors.append(f"{path}: physical quantities require evidence_refs")
    for index, component in enumerate(state["semiconductors"]):
        if component.get("ratings") and not component["evidence_refs"]:
            errors.append(f"$.semiconductors[{index}]: ratings require evidence_refs")

    # Core: provenance acyclicity (depth-first search over evidence provenance inputs).
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in visiting:
            errors.append(f"Cyclic evidence provenance at {identifier}")
            return
        if identifier in visited or identifier not in evidence:
            return
        visiting.add(identifier)
        for dependency in evidence[identifier]["provenance"]["inputs"]:
            visit(dependency)
        visiting.remove(identifier)
        visited.add(identifier)
    for identifier in evidence:
        visit(identifier)

    def has_kind(references: list[str], kind: str) -> bool:
        return any(reference in evidence and evidence[reference]["kind"] == kind for reference in references)

    # Core: validation status / check consistency.
    validation = state["validation"]
    physical_kinds = {"analytical", "simulation", "measurement"}
    for check in validation["checks"]:
        if (check["status"] == "pass" and check["kind"] in physical_kinds
                and not has_kind(check["evidence_refs"], check["kind"])):
            errors.append(f"{check['id']}: passing {check['kind']} check needs matching evidence")
    required_kind = {"schema_validated": "schema", "analytically_checked": "analytical",
                     "simulated": "simulation", "measured": "measurement",
                     "reviewed": "review"}.get(validation["status"])
    if required_kind and not any(check["status"] == "pass" and check["kind"] == required_kind
                                 for check in validation["checks"]):
        errors.append(f"Validation status {validation['status']} needs a passing {required_kind} check")
    if any(check["status"] == "fail" for check in validation["checks"]) and validation["status"] != "failed":
        errors.append("Failed checks require overall validation status failed")

    # Core: simulation status rules.
    operating_points = {point["id"] for point in state["requirements"].get("operating_points", [])}
    runs = state["simulation"]["runs"]
    for run in runs:
        if run.get("operating_point_ref") and run["operating_point_ref"] not in operating_points:
            errors.append(f"{run['id']}: unknown operating point {run['operating_point_ref']}")
        if run["status"] == "completed" and (not run["outputs"] or not has_kind(run["evidence_refs"], "simulation")):
            errors.append(f"{run['id']}: completed simulation requires outputs and simulation evidence")
    status = state["simulation"]["status"]
    if status == "not_run" and runs:
        errors.append("Simulation status not_run requires no runs")
    if status in {"completed", "failed", "configured"} and not any(run["status"] == status for run in runs):
        errors.append(f"Simulation status {status} requires a matching run")
    return errors


def load_state(path: str | Path) -> Any:
    """Load a state file the way Core does: duplicate keys and NaN/Infinity are rejected."""
    return load_json(path)


@lru_cache(maxsize=1)
def _example() -> dict[str, Any]:
    return load_json(EXAMPLE_PATH)


def load_core_example() -> dict[str, Any]:
    """A fresh deep copy of the vendored synthetic 10 kW DAB example state (``aipe.example.dab-10kw``)."""
    return copy.deepcopy(_example())


__all__ = [
    "CORE_COMMIT", "CORE_REPOSITORY", "CORE_SCHEMA_BASE", "CORE_SCHEMA_VERSION", "EXAMPLE_PATH", "REQUIRED_FORMATS",
    "SCHEMA_DIR", "STATE_SCHEMA_ID", "VENDORED_SHA256", "core_schema_ids", "load_core_example", "load_core_schemas",
    "load_state", "state_validator", "validate_engineering_state", "vendored_files", "verify_vendored_integrity",
]
