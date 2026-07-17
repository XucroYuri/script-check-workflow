"""Fail-closed policy helpers for the post-synthesis workflow."""

from copy import deepcopy
from hashlib import sha256
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from scripts.contract import (
    CORRECTION_POLICY,
    REVIEWER_OUTPUT,
    STAGE_FIELDS,
    TARGET_PROFILE_OBJECT_SCHEMA,
)


INVALID_STAGE_OUTPUT = "BLOCKED: INVALID_STAGE_OUTPUT"
CONTRACT_ERROR = "BLOCKED: CONTRACT_ERROR"
MAX_AUTOMATIC_CORRECTION_CYCLES = CORRECTION_POLICY[
    "maxAutomaticCorrectionCycles"
]
WRITER_DECISION_CONTINUITY_STATES = frozenset(
    CORRECTION_POLICY["writerDecisionContinuityStates"]
)

FINDING_FIELDS = frozenset(
    {
        "finding_id",
        "stage_id",
        "location_id",
        "source_span",
        "source_text_sha256",
        "rule_id",
        "severity",
        "description",
        "original",
        "corrected",
        "correction_basis",
        "confidence",
        "writer_decision_needed",
    }
)
PROPOSAL_FIELDS = frozenset(
    {
        "proposal_id",
        "finding_ids",
        "location_id",
        "source_span",
        "expected_source_sha256",
        "replacement",
        "affected_assets",
        "requires_writer_decision",
    }
)
OPTIONAL_PROPOSAL_FIELDS = frozenset({"asset_state_changes"})
OUTPUT_COMPONENTS = frozenset(REVIEWER_OUTPUT["components"])
HASH_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
ASPECT_RATIO_PATTERN = re.compile(r"[1-9][0-9]*:[1-9][0-9]*\Z")
TARGET_PROFILE_FIELDS = frozenset(TARGET_PROFILE_OBJECT_SCHEMA["required"])
TARGET_PROFILE_MODES = frozenset(
    TARGET_PROFILE_OBJECT_SCHEMA["properties"]["mode"]["enum"]
)


class WorkflowBlocked(ValueError):
    """A fail-closed workflow policy result."""


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _is_span(value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != {"start_line", "end_line"}:
        return False
    start = value.get("start_line")
    end = value.get("end_line")
    return (
        isinstance(start, int)
        and not isinstance(start, bool)
        and isinstance(end, int)
        and not isinstance(end, bool)
        and 1 <= start <= end
    )


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and HASH_PATTERN.fullmatch(value) is not None


def target_profile_declared_gate(target_profile: Any) -> bool:
    """Derive the target-profile hard gate without coercing invalid input."""

    if not isinstance(target_profile, dict) or set(target_profile) != TARGET_PROFILE_FIELDS:
        return False
    duration = target_profile.get("clip_duration_seconds")
    mode = target_profile.get("mode")
    return all(
        (
            _is_nonempty_string(target_profile.get("provider")),
            _is_nonempty_string(target_profile.get("model")),
            _is_nonempty_string(target_profile.get("model_version")),
            isinstance(mode, str) and mode in TARGET_PROFILE_MODES,
            isinstance(duration, (int, float))
            and not isinstance(duration, bool)
            and duration > 0,
            isinstance(target_profile.get("aspect_ratio"), str)
            and ASPECT_RATIO_PATTERN.fullmatch(target_profile["aspect_ratio"])
            is not None,
            isinstance(target_profile.get("reference_assets_available"), bool),
        )
    )


def validate_target_profile_input(target_profile: Any) -> bool:
    """Accept canonical null or a valid profile; reject malformed non-null data."""

    if target_profile is None:
        return False
    declared = target_profile_declared_gate(target_profile)
    if not declared:
        raise WorkflowBlocked(CONTRACT_ERROR)
    return True


def _normalized_source_lines(script: str) -> List[str]:
    normalized_script = script.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized_script.split("\n")
    if normalized_script.endswith("\n"):
        lines.pop()
    return lines


def source_fragment(script: str, start_line: int, end_line: int) -> str:
    """Return a 1-based inclusive line span normalized to LF."""

    span = {"start_line": start_line, "end_line": end_line}
    if not isinstance(script, str) or not _is_span(span):
        raise ValueError("invalid source span")
    lines = _normalized_source_lines(script)
    if end_line > len(lines):
        raise ValueError("source span exceeds script line count")
    return "\n".join(lines[start_line - 1 : end_line])


def source_fragment_sha256(script: str, start_line: int, end_line: int) -> str:
    fragment = source_fragment(script, start_line, end_line)
    return sha256(fragment.encode("utf-8")).hexdigest()


def assign_finding_ids(findings: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Sort findings canonically and assign unique run-local IDs."""

    indexed = list(enumerate(findings))
    indexed.sort(
        key=lambda item: (
            item[1]["source_span"]["start_line"],
            item[1]["source_span"]["end_line"],
            item[1]["rule_id"],
            item[0],
        )
    )
    assigned: List[Dict[str, Any]] = []
    for occurrence, (_, finding) in enumerate(indexed, start=1):
        record = deepcopy(dict(finding))
        record["finding_id"] = "F-{}-{}-{}-{:03d}".format(
            record["stage_id"],
            record["rule_id"],
            record["location_id"],
            occurrence,
        )
        assigned.append(record)
    return assigned


def proposal_id_for_finding_id(finding_id: str) -> str:
    if not isinstance(finding_id, str) or not finding_id.startswith("F-"):
        raise ValueError("finding_id must start with F-")
    return "P-" + finding_id[2:]


def can_start_automatic_correction_cycle(completed_cycles: int) -> bool:
    return (
        isinstance(completed_cycles, int)
        and not isinstance(completed_cycles, bool)
        and 0 <= completed_cycles < MAX_AUTOMATIC_CORRECTION_CYCLES
    )


def require_automatic_correction_cycle(completed_cycles: int) -> None:
    if not can_start_automatic_correction_cycle(completed_cycles):
        raise WorkflowBlocked("BLOCKED: CORRECTION_CYCLE_LIMIT")


def conflict_reasons(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> Tuple[str, ...]:
    reasons: List[str] = []
    left_span = left["source_span"]
    right_span = right["source_span"]
    if max(left_span["start_line"], right_span["start_line"]) <= min(
        left_span["end_line"], right_span["end_line"]
    ):
        reasons.append("overlapping_source_span")
    if left["location_id"] == right["location_id"]:
        reasons.append("identical_location_id")

    shared_assets = set(left.get("affected_assets", [])) & set(
        right.get("affected_assets", [])
    )
    left_states = left.get("asset_state_changes", {})
    right_states = right.get("asset_state_changes", {})
    if any(
        asset in left_states
        and asset in right_states
        and left_states[asset] != right_states[asset]
        for asset in shared_assets
    ):
        reasons.append("incompatible_asset_state")
    return tuple(reasons)


def _proposal_conflicts(proposals: Sequence[Mapping[str, Any]]) -> bool:
    for index, left in enumerate(proposals):
        for right in proposals[index + 1 :]:
            if conflict_reasons(left, right):
                return True
    return False


def _proposal_has_protected_state(proposal: Mapping[str, Any]) -> bool:
    state_changes = proposal.get("asset_state_changes", {})
    return isinstance(state_changes, dict) and any(
        isinstance(state, str) and state in WRITER_DECISION_CONTINUITY_STATES
        for state in state_changes.values()
    )


def _validate_proposals_against_snapshot(
    script: str, proposals: Sequence[Mapping[str, Any]]
) -> None:
    stale = False
    for item in proposals:
        try:
            span = item["source_span"]
            actual = source_fragment_sha256(
                script, span["start_line"], span["end_line"]
            )
            if actual != item["expected_source_sha256"]:
                stale = True
        except (KeyError, TypeError, ValueError):
            stale = True
    if stale:
        raise WorkflowBlocked("BLOCKED: STALE_PATCH")


def apply_correction_proposals(
    script: str, proposals: Sequence[Mapping[str, Any]]
) -> str:
    """Validate all proposals against one source snapshot, then apply bottom-up."""

    _validate_proposals_against_snapshot(script, proposals)

    if any(
        item.get("requires_writer_decision") is True
        or _proposal_has_protected_state(item)
        for item in proposals
    ):
        raise WorkflowBlocked("BLOCKED: WRITER_DECISION_REQUIRED")
    if _proposal_conflicts(proposals):
        raise WorkflowBlocked("BLOCKED: PATCH_CONFLICT")

    lines = _normalized_source_lines(script)
    ordered = sorted(
        proposals,
        key=lambda item: (
            item["source_span"]["start_line"],
            item["source_span"]["end_line"],
        ),
        reverse=True,
    )
    for item in ordered:
        span = item["source_span"]
        replacement_lines = (
            []
            if item["replacement"] == ""
            else _normalized_source_lines(item["replacement"])
        )
        lines[span["start_line"] - 1 : span["end_line"]] = replacement_lines
    return "\n".join(lines)


def select_delivery_artifacts(delivery_status: str) -> Tuple[str, str, str]:
    if delivery_status in {"READY", "CONDITIONAL"}:
        script_artifact = "standardized-script"
    elif delivery_status in {"REWORK", "BLOCKED"}:
        script_artifact = "candidate-script"
    else:
        raise ValueError("unknown delivery status")
    return script_artifact, "diagnostics-record", "asset-continuity-ledger"


def continuity_state_requires_writer_decision(state: str) -> bool:
    return state in WRITER_DECISION_CONTINUITY_STATES


def _valid_finding(record: Any, stage_id: str) -> bool:
    if not isinstance(record, dict) or set(record) != FINDING_FIELDS:
        return False
    confidence = record.get("confidence")
    return all(
        (
            _is_nonempty_string(record.get("finding_id")),
            record.get("stage_id") == stage_id,
            _is_nonempty_string(record.get("location_id")),
            _is_span(record.get("source_span")),
            _is_sha256(record.get("source_text_sha256")),
            _is_nonempty_string(record.get("rule_id")),
            record.get("severity") in {"high", "medium", "low"},
            isinstance(record.get("description"), str),
            isinstance(record.get("original"), str),
            isinstance(record.get("corrected"), str),
            isinstance(record.get("correction_basis"), str),
            isinstance(confidence, (int, float))
            and not isinstance(confidence, bool)
            and 0 <= confidence <= 1,
            isinstance(record.get("writer_decision_needed"), bool),
        )
    )


def _valid_proposal(record: Any, finding_ids: Iterable[str]) -> bool:
    if not isinstance(record, dict):
        return False
    fields = set(record)
    if not PROPOSAL_FIELDS <= fields or not fields <= (
        PROPOSAL_FIELDS | OPTIONAL_PROPOSAL_FIELDS
    ):
        return False
    linked_findings = record.get("finding_ids")
    assets = record.get("affected_assets")
    state_changes = record.get("asset_state_changes", {})
    if (
        not isinstance(linked_findings, list)
        or not linked_findings
        or not all(item in finding_ids for item in linked_findings)
    ):
        return False
    if (
        not _is_nonempty_string(record.get("proposal_id"))
        or record["proposal_id"] != proposal_id_for_finding_id(linked_findings[0])
    ):
        return False
    if (
        not isinstance(assets, list)
        or not all(_is_nonempty_string(asset) for asset in assets)
        or len(assets) != len(set(assets))
    ):
        return False
    if (
        not isinstance(state_changes, dict)
        or not set(state_changes) <= set(assets)
        or not all(_is_nonempty_string(state) for state in state_changes.values())
    ):
        return False
    return all(
        (
            _is_nonempty_string(record.get("location_id")),
            _is_span(record.get("source_span")),
            _is_sha256(record.get("expected_source_sha256")),
            isinstance(record.get("replacement"), str),
            isinstance(record.get("requires_writer_decision"), bool),
        )
    )


def parse_stage_output(
    payload: Any,
    stage_id: str,
    prerequisites: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Validate the three reviewer output components or fail closed."""

    derived_target_profile_declared = None
    if stage_id == "stage5":
        if not isinstance(prerequisites, Mapping) or "target_profile" not in prerequisites:
            raise WorkflowBlocked(CONTRACT_ERROR)
        derived_target_profile_declared = validate_target_profile_input(
            prerequisites["target_profile"]
        )

    try:
        if not isinstance(payload, dict) or set(payload) != OUTPUT_COMPONENTS:
            raise ValueError
        findings = payload["finding"]
        proposals = payload["correction_proposal"]
        metrics = payload["metrics"]
        if not isinstance(findings, list) or not all(
            _valid_finding(record, stage_id) for record in findings
        ):
            raise ValueError
        finding_ids = [record["finding_id"] for record in findings]
        if len(finding_ids) != len(set(finding_ids)):
            raise ValueError
        finding_bases = [
            {key: value for key, value in record.items() if key != "finding_id"}
            for record in findings
        ]
        expected_ids = [
            record["finding_id"] for record in assign_finding_ids(finding_bases)
        ]
        if finding_ids != expected_ids:
            raise ValueError
        if not isinstance(proposals, list) or not all(
            _valid_proposal(record, finding_ids) for record in proposals
        ):
            raise ValueError
        proposal_ids = [record["proposal_id"] for record in proposals]
        if len(proposal_ids) != len(set(proposal_ids)):
            raise ValueError
        expected_metrics = {
            field
            for field in STAGE_FIELDS[stage_id]["produces"]
            if not field.endswith("_findings")
        }
        if not isinstance(metrics, dict) or set(metrics) != expected_metrics:
            raise ValueError
        if stage_id == "stage5" and not isinstance(
            metrics.get("target_profile_declared"), bool
        ):
            raise ValueError
        if (
            stage_id == "stage5"
            and metrics["target_profile_declared"]
            is not derived_target_profile_declared
        ):
            raise ValueError
    except (KeyError, TypeError, ValueError):
        raise WorkflowBlocked(INVALID_STAGE_OUTPUT)
    return payload
