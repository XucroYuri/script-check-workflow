import json
import math
from pathlib import Path
import re
from typing import Any, Dict, List, Union


PathLike = Union[str, Path]

STAGE_ORDER = [
    "stage1",
    "stage2",
    "stage3",
    "stage4",
    "stage4_5",
    "stage5",
    "stage6",
    "stage7",
]
WORKFLOW_PHASES = [
    "ingest_untrusted_input",
    "analyze_original",
    "resolve_corrections",
    "synthesize_candidate",
    "review_candidate",
    "evaluate_hard_gates",
    "score_candidate",
    "deliver",
]
REVIEWER_OUTPUT = {
    "components": ["finding", "correction_proposal", "metrics"],
    "invalidStatus": "BLOCKED: INVALID_STAGE_OUTPUT",
}
CORRECTION_POLICY = {
    "maxAutomaticCorrectionCycles": 1,
    "sourceSpanConvention": "one_based_inclusive",
    "sourceHashConvention": "normalized_lf_utf8_sha256",
    "conflictTypes": [
        "overlapping_source_span",
        "identical_location_id",
        "incompatible_asset_state",
    ],
    "stalePatchStatus": "BLOCKED: STALE_PATCH",
    "assetStateChangeCategories": [
        "condition",
        "blood",
        "displacement",
        "occlusion",
        "orientation",
    ],
    "writerDecisionStateCategories": [
        "blood",
        "displacement",
        "occlusion",
        "orientation",
    ],
}
SCORING_RULES = {
    "R1.1", "R1.2", "R1.3", "R1.4",
    "R2.5", "R2.6", "R2.7", "R2.8",
    "R3.9", "R3.10", "R3.11", "R3.12", "R3.13", "R3.14",
    "R4.15", "R4.16", "R4.16.5", "R4.17", "R4.18", "R4.19",
    "R5.20", "R5.21", "R5.22", "R5.23", "R5.24", "R5.25", "R5.26",
    "R6.28", "R6.29", "R6.30", "R6.31",
    "R7.34", "R7.35", "R7.36", "R7.37",
}
NON_SCORING_RULES = {
    "R4.5.1", "R4.5.2", "R4.5.3", "R4.5.4", "R5.27", "R6.32", "R6.33",
}
STAGE_RULE_IDS = {
    "stage1": ["R1.1", "R1.2", "R1.3", "R1.4"],
    "stage2": ["R2.5", "R2.6", "R2.7", "R2.8"],
    "stage3": ["R3.9", "R3.10", "R3.11", "R3.12", "R3.13", "R3.14"],
    "stage4": ["R4.15", "R4.16", "R4.16.5", "R4.17", "R4.18", "R4.19"],
    "stage4_5": ["R4.5.1", "R4.5.2", "R4.5.3", "R4.5.4"],
    "stage5": ["R5.20", "R5.21", "R5.22", "R5.23", "R5.24", "R5.25", "R5.26", "R5.27"],
    "stage6": ["R6.28", "R6.29", "R6.30", "R6.31", "R6.32", "R6.33"],
    "stage7": ["R7.34", "R7.35", "R7.36", "R7.37"],
}
HARD_GATES = {
    "contract_valid",
    "post_synthesis_review_complete",
    "unresolved_high_findings_zero",
    "unresolved_high_writer_confirmations_zero",
    "final_review_red_count_zero",
    "artifact_schema_valid",
    "target_profile_declared",
    "input_budget_valid",
}
SCENE_BOUNDARIES_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "x-fieldOrder": ["start_line", "end_line"],
        "required": ["id", "start_line", "end_line"],
        "properties": {
            "id": {"type": "string", "minLength": 1},
            "start_line": {"type": "integer", "minimum": 1},
            "end_line": {"type": "integer", "minimum": 1},
        },
    },
}
SCENE_SHOT_MAP_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "required": ["scene", "shots"],
        "properties": {
            "scene": {"type": "string", "minLength": 1},
            "shots": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "minItems": 1,
            },
        },
    },
}
KEY_ACTION_EVENTS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "required": ["location", "actor", "action", "affected_asset"],
        "properties": {
            "location": {"type": "string", "minLength": 1},
            "actor": {"type": "string", "minLength": 1},
            "action": {"type": "string", "minLength": 1},
            "affected_asset": {"type": "string", "minLength": 1},
        },
    },
}
TARGET_PROFILE_OBJECT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "provider",
        "model",
        "model_version",
        "mode",
        "clip_duration_seconds",
        "aspect_ratio",
        "reference_assets_available",
    ],
    "properties": {
        "provider": {"type": "string", "minLength": 1},
        "model": {"type": "string", "minLength": 1},
        "model_version": {"type": "string", "minLength": 1},
        "mode": {
            "enum": ["T2V", "I2V", "keyframe-animation", "segmented-generation"]
        },
        "clip_duration_seconds": {"type": "number", "exclusiveMinimum": 0},
        "aspect_ratio": {
            "type": "string",
            "pattern": "^[1-9][0-9]*:[1-9][0-9]*$",
        },
        "reference_assets_available": {"type": "boolean"},
    },
}
TARGET_PROFILE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "oneOf": [
        {"type": "null"},
        TARGET_PROFILE_OBJECT_SCHEMA,
    ],
}
FIELD_SCHEMAS = {
    "scene_boundaries": SCENE_BOUNDARIES_SCHEMA,
    "scene_shot_map": SCENE_SHOT_MAP_SCHEMA,
    "key_action_events": KEY_ACTION_EVENTS_SCHEMA,
    "target_profile": TARGET_PROFILE_SCHEMA,
}


def _exact_object(properties: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(properties),
        "properties": properties,
    }


def _nonempty_string() -> Dict[str, Any]:
    return {"type": "string", "minLength": 1}


def _count() -> Dict[str, Any]:
    return {"type": "integer", "minimum": 0}


def _bounded_number(minimum: float, maximum: float) -> Dict[str, Any]:
    return {
        "type": "number",
        "minimum": minimum,
        "maximum": maximum,
    }


def _ratio() -> Dict[str, Any]:
    return _bounded_number(0, 1)


def _array(item_schema: Dict[str, Any], min_items: int = 0) -> Dict[str, Any]:
    schema: Dict[str, Any] = {"type": "array", "items": item_schema}
    if min_items:
        schema["minItems"] = min_items
    return schema


ANCHOR_COUNT_PER_SCENE_SCHEMA = _array(
    _exact_object(
        {
            "scene": _nonempty_string(),
            "anchors": _count(),
            "names": _array(_nonempty_string()),
        }
    )
)
RISK_DISTRIBUTION_SCHEMA = _exact_object(
    {"low": _count(), "medium": _count(), "high": _count()}
)
TRACKED_ASSET_COUNT_SCHEMA = _exact_object(
    {"character": _count(), "scene": _count(), "prop": _count()}
)
CONTINUITY_RISK_COUNT_SCHEMA = _exact_object(
    {"high": _count(), "medium": _count(), "low": _count()}
)
HIGH_RISK_ASSET_JUMPS_SCHEMA = _array(
    _exact_object(
        {
            "asset": _nonempty_string(),
            "from": _nonempty_string(),
            "to": _nonempty_string(),
        }
    )
)
VISUAL_ANCHOR_UPDATES_SCHEMA = _array(
    _exact_object(
        {
            "asset": _nonempty_string(),
            "location": _nonempty_string(),
            "reason": _nonempty_string(),
        }
    )
)
FAILURE_MODE_DISTRIBUTION_SCHEMA = _exact_object(
    {
        "face_swap": _count(),
        "limb_error": _count(),
        "prop_vanish": _count(),
        "lr_drift": _count(),
        "bg_jump": _count(),
        "action_break": _count(),
        "occlusion": _count(),
    }
)
TEAM_HANDOFF_SCORE_SCHEMA = _exact_object(
    {
        "director": _ratio(),
        "storyboard": _ratio(),
        "art": _ratio(),
        "animation": _ratio(),
        "ai_generation": _ratio(),
        "continuity_handoff": _ratio(),
    }
)
METRIC_SCHEMAS = {
    "stage1": _exact_object(
        {
            "scene_count": _count(),
            "scene_boundaries": SCENE_BOUNDARIES_SCHEMA,
            "character_count": _count(),
            "pronoun_density": _ratio(),
            "intent_word_count": _count(),
            "metaphor_count": _count(),
            "six_layer_coverage": _ratio(),
            "stage1_pass_rate": _ratio(),
        }
    ),
    "stage2": _exact_object(
        {
            "scene_boundaries": SCENE_BOUNDARIES_SCHEMA,
            "anchor_count_per_scene": ANCHOR_COUNT_PER_SCENE_SCHEMA,
            "initial_state_completeness": _ratio(),
            "consistency_score": _ratio(),
            "atmosphere_specificity": _ratio(),
            "stage2_pass_rate": _ratio(),
        }
    ),
    "stage3": _exact_object(
        {
            "shot_count": _count(),
            "scene_shot_map": SCENE_SHOT_MAP_SCHEMA,
            "avg_info_layers": _bounded_number(0, 6),
            "format_consistency": _ratio(),
            "risk_distribution": RISK_DISTRIBUTION_SCHEMA,
            "dual_high_conflict_count": _count(),
            "stage3_pass_rate": _ratio(),
        }
    ),
    "stage4": _exact_object(
        {
            "key_action_events": KEY_ACTION_EVENTS_SCHEMA,
            "action_complexity": _bounded_number(1, 10),
            "emotion_leakage_count": _count(),
            "missing_physics_feedback": _count(),
            "action_chain_issues": _count(),
            "overloaded_shots": _count(),
            "interaction_risk_count": _count(),
            "stage4_pass_rate": _ratio(),
        }
    ),
    "stage4_5": _exact_object(
        {
            "tracked_asset_count": TRACKED_ASSET_COUNT_SCHEMA,
            "continuity_risk_count": CONTINUITY_RISK_COUNT_SCHEMA,
            "high_risk_asset_jumps": HIGH_RISK_ASSET_JUMPS_SCHEMA,
            "requires_writer_confirmation_count": _count(),
            "suggested_visual_anchor_updates": VISUAL_ANCHOR_UPDATES_SCHEMA,
            "low_risk_patch_count": _count(),
            "stage4_5_pass_rate": _ratio(),
        }
    ),
    "stage5": _exact_object(
        {
            "target_profile_declared": {"type": "boolean"},
            "generation_risk_score": _bounded_number(1, 10),
            "anchor_coverage": _ratio(),
            "visual_nail_count": _count(),
            "negative_constraint_coverage": _ratio(),
            "high_risk_shots": _count(),
            "failure_mode_distribution": FAILURE_MODE_DISTRIBUTION_SCHEMA,
            "stage5_pass_rate": _ratio(),
        }
    ),
    "stage6": _exact_object(
        {
            "isolation_compliance": _ratio(),
            "ai_taste_score": _bounded_number(1, 10),
            "dialogue_mismatch_count": _count(),
            "natural_speech_score": _ratio(),
            "stage6_pass_rate": _ratio(),
        }
    ),
    "stage7": _exact_object(
        {
            "team_handoff_score": {
                "oneOf": [_ratio(), TEAM_HANDOFF_SCORE_SCHEMA]
            },
            "acceptance_readiness": _ratio(),
            "stage7_pass_rate": _ratio(),
        }
    ),
}
STAGE_FIELDS = {
    "stage1": {
        "requires": ["script_text", "run_metadata"],
        "produces": ["scene_count", "scene_boundaries", "character_count", "pronoun_density", "intent_word_count", "metaphor_count", "six_layer_coverage", "stage1_findings", "stage1_pass_rate"],
    },
    "stage2": {
        "requires": ["script_text", "scene_count", "scene_boundaries"],
        "produces": ["scene_boundaries", "anchor_count_per_scene", "initial_state_completeness", "consistency_score", "atmosphere_specificity", "stage2_findings", "stage2_pass_rate"],
    },
    "stage3": {
        "requires": ["script_text", "scene_boundaries", "anchor_count_per_scene"],
        "produces": ["shot_count", "scene_shot_map", "avg_info_layers", "format_consistency", "risk_distribution", "dual_high_conflict_count", "stage3_findings", "stage3_pass_rate"],
    },
    "stage4": {
        "requires": ["script_text", "shot_count", "risk_distribution"],
        "produces": ["key_action_events", "action_complexity", "emotion_leakage_count", "missing_physics_feedback", "action_chain_issues", "overloaded_shots", "interaction_risk_count", "stage4_findings", "stage4_pass_rate"],
    },
    "stage4_5": {
        "requires": ["script_text", "scene_boundaries", "anchor_count_per_scene", "shot_count", "scene_shot_map", "key_action_events", "interaction_risk_count"],
        "produces": ["tracked_asset_count", "continuity_risk_count", "high_risk_asset_jumps", "requires_writer_confirmation_count", "suggested_visual_anchor_updates", "low_risk_patch_count", "stage4_5_findings", "stage4_5_pass_rate"],
    },
    "stage5": {
        "requires": ["script_text", "target_profile", "action_complexity", "interaction_risk_count", "continuity_risk_count", "suggested_visual_anchor_updates", "shot_count"],
        "produces": ["target_profile_declared", "generation_risk_score", "anchor_coverage", "visual_nail_count", "negative_constraint_coverage", "high_risk_shots", "failure_mode_distribution", "stage5_findings", "stage5_pass_rate"],
    },
    "stage6": {
        "requires": ["script_text", "character_count", "scene_count"],
        "produces": ["isolation_compliance", "ai_taste_score", "dialogue_mismatch_count", "natural_speech_score", "stage6_findings", "stage6_pass_rate"],
    },
    "stage7": {
        "requires": ["script_text", "scene_count", "shot_count", "requires_writer_confirmation_count", "stage1_pass_rate", "stage2_pass_rate", "stage3_pass_rate", "stage4_pass_rate", "stage4_5_pass_rate", "stage5_pass_rate", "stage6_pass_rate"],
        "produces": ["team_handoff_score", "acceptance_readiness", "stage7_findings", "stage7_pass_rate"],
    },
}
REQUIRED_ROOT_KEYS = {
    "contractVersion",
    "stageOrder",
    "workflowPhases",
    "reviewerOutput",
    "correctionPolicy",
    "inputBudget",
    "fieldSchemas",
    "metricSchemas",
    "stages",
    "scoring",
}
CANONICAL_CONTRACT_PATH = (
    Path(__file__).resolve().parents[1] / "contracts" / "workflow-contract.json"
)


def load_contract(path: PathLike) -> Dict[str, Any]:
    requested_path = Path(path).resolve()
    if requested_path != CANONICAL_CONTRACT_PATH:
        raise ValueError("load_contract only accepts the canonical workflow contract path")
    with requested_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _is_list_of_strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


SCHEMA_KEYWORDS = {
    "$schema",
    "type",
    "oneOf",
    "enum",
    "additionalProperties",
    "required",
    "properties",
    "items",
    "minItems",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "minLength",
    "pattern",
    "x-fieldOrder",
}


def _schema_keywords_well_typed(schema: Any) -> bool:
    if not isinstance(schema, dict) or not set(schema) <= SCHEMA_KEYWORDS:
        return False
    if "$schema" in schema and not isinstance(schema["$schema"], str):
        return False
    if "type" in schema:
        schema_type = schema["type"]
        if not isinstance(schema_type, str) or schema_type not in {
            "null",
            "boolean",
            "integer",
            "number",
            "string",
            "array",
            "object",
        }:
            return False
    if "additionalProperties" in schema and type(
        schema["additionalProperties"]
    ) is not bool:
        return False
    if "oneOf" in schema:
        one_of = schema["oneOf"]
        if not isinstance(one_of, list) or not one_of:
            return False
        if not all(_schema_keywords_well_typed(option) for option in one_of):
            return False
    if "enum" in schema and not isinstance(schema["enum"], list):
        return False
    if "required" in schema and not _is_list_of_strings(schema["required"]):
        return False
    if "properties" in schema:
        properties = schema["properties"]
        if not isinstance(properties, dict) or not all(
            isinstance(name, str) and _schema_keywords_well_typed(subschema)
            for name, subschema in properties.items()
        ):
            return False
    if "items" in schema and not _schema_keywords_well_typed(schema["items"]):
        return False
    if "minItems" in schema and (
        type(schema["minItems"]) is not int or schema["minItems"] < 0
    ):
        return False
    for keyword in ("minimum", "maximum", "exclusiveMinimum"):
        boundary = schema.get(keyword)
        if keyword in schema and (
            not isinstance(boundary, (int, float))
            or isinstance(boundary, bool)
            or (isinstance(boundary, float) and not math.isfinite(boundary))
        ):
            return False
    if "minLength" in schema and (
        type(schema["minLength"]) is not int or schema["minLength"] < 0
    ):
        return False
    if "pattern" in schema and not isinstance(schema["pattern"], str):
        return False
    if "x-fieldOrder" in schema and not _is_list_of_strings(
        schema["x-fieldOrder"]
    ):
        return False
    return True


def validate_schema_instance(value: Any, schema: Any) -> bool:
    """Validate the canonical contract's small JSON-Schema vocabulary."""

    if not _schema_keywords_well_typed(schema):
        return False

    one_of = schema.get("oneOf")
    if one_of is not None:
        if not isinstance(one_of, list) or not one_of:
            return False
        if sum(validate_schema_instance(value, option) for option in one_of) != 1:
            return False

    enum = schema.get("enum")
    if enum is not None:
        if not isinstance(enum, list) or value not in enum:
            return False

    expected_type = schema.get("type")
    if expected_type == "null":
        if value is not None:
            return False
    elif expected_type == "boolean":
        if not isinstance(value, bool):
            return False
    elif expected_type == "integer":
        if type(value) is not int:
            return False
    elif expected_type == "number":
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or (isinstance(value, float) and not math.isfinite(value))
        ):
            return False
    elif expected_type == "string":
        if not isinstance(value, str):
            return False
    elif expected_type == "array":
        if not isinstance(value, list):
            return False
    elif expected_type == "object":
        if not isinstance(value, dict):
            return False
    elif expected_type is not None:
        return False

    if expected_type in {"integer", "number"}:
        if "minimum" in schema and value < schema["minimum"]:
            return False
        if "maximum" in schema and value > schema["maximum"]:
            return False
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            return False

    if expected_type == "string":
        if "minLength" in schema and len(value) < schema["minLength"]:
            return False
        if "pattern" in schema:
            try:
                if re.search(schema["pattern"], value) is None:
                    return False
            except (re.error, TypeError):
                return False

    if expected_type == "array":
        if "minItems" in schema and len(value) < schema["minItems"]:
            return False
        item_schema = schema.get("items")
        if not isinstance(item_schema, dict):
            return False
        if not all(validate_schema_instance(item, item_schema) for item in value):
            return False

    if expected_type == "object":
        properties = schema.get("properties")
        required = schema.get("required")
        if not isinstance(properties, dict) or not _is_list_of_strings(required):
            return False
        if not set(required) <= set(value):
            return False
        extras = set(value) - set(properties)
        additional = schema.get("additionalProperties", True)
        if type(additional) is not bool:
            return False
        if additional is False and extras:
            return False
        if not all(
            validate_schema_instance(item, properties[name])
            for name, item in value.items()
            if name in properties
        ):
            return False
        field_order = schema.get("x-fieldOrder")
        if field_order is not None:
            if not _is_list_of_strings(field_order) or len(field_order) != 2:
                return False
            first, second = field_order
            if first not in value or second not in value:
                return False
            try:
                if value[first] > value[second]:
                    return False
            except TypeError:
                return False

    return True


def validate_contract(contract: Dict[str, Any]) -> List[str]:
    if not isinstance(contract, dict):
        return ["contract root must be an object"]

    errors: List[str] = []
    for key in sorted(REQUIRED_ROOT_KEYS - set(contract)):
        errors.append("missing required root key: " + key)

    if contract.get("contractVersion") != "3.2.0":
        errors.append("contractVersion must equal 3.2.0")

    order = contract.get("stageOrder")
    if not _is_list_of_strings(order) or order != STAGE_ORDER:
        errors.append("stageOrder must equal the exact eight-stage order")

    workflow_phases = contract.get("workflowPhases")
    if not _is_list_of_strings(workflow_phases) or workflow_phases != WORKFLOW_PHASES:
        errors.append("workflowPhases must equal the exact eight workflow phases")

    if contract.get("reviewerOutput") != REVIEWER_OUTPUT:
        errors.append("reviewerOutput must use the canonical three-component schema")

    if contract.get("correctionPolicy") != CORRECTION_POLICY:
        errors.append("correctionPolicy must use the canonical closed-loop policy")

    input_budget = contract.get("inputBudget")
    if not isinstance(input_budget, dict):
        errors.append("inputBudget must be an object")
    elif input_budget.get("maxScriptUnicodeCodePoints") != 60000:
        errors.append("inputBudget.maxScriptUnicodeCodePoints must equal 60000")

    field_schemas = contract.get("fieldSchemas")
    if not isinstance(field_schemas, dict):
        errors.append("fieldSchemas must be an object")
    else:
        for field_name, schema in FIELD_SCHEMAS.items():
            actual_schema = field_schemas.get(field_name)
            if (
                not _schema_keywords_well_typed(actual_schema)
                or actual_schema != schema
            ):
                errors.append(field_name + " must use the canonical field schema")

    metric_schemas = contract.get("metricSchemas")
    if not isinstance(metric_schemas, dict) or set(metric_schemas) != set(STAGE_ORDER):
        errors.append("metricSchemas must contain the exact eight Stage schemas")
        metric_schemas = {} if not isinstance(metric_schemas, dict) else metric_schemas
    for stage_id in STAGE_ORDER:
        actual_schema = metric_schemas.get(stage_id)
        if (
            not _schema_keywords_well_typed(actual_schema)
            or actual_schema != METRIC_SCHEMAS[stage_id]
        ):
            errors.append(stage_id + " metrics must use the canonical metric schema")

    stages = contract.get("stages")
    valid_stages = isinstance(stages, dict)
    if not valid_stages:
        errors.append("stages must be an object")
        stages = {}
    elif list(stages) != STAGE_ORDER:
        errors.append("stages must contain the exact eight stages in stage order")

    available = {"script_text", "run_metadata", "target_profile"}
    if valid_stages:
        for stage_id in STAGE_ORDER:
            stage = stages.get(stage_id)
            if not isinstance(stage, dict):
                errors.append(stage_id + " must be an object")
                continue
            requires = stage.get("requires")
            produces = stage.get("produces")
            allowed_rule_ids = stage.get("allowedRuleIds")
            if not _is_list_of_strings(requires):
                errors.append(stage_id + " requires must be a list of strings")
                requires = []
            if not _is_list_of_strings(produces):
                errors.append(stage_id + " produces must be a list of strings")
                produces = []
            if allowed_rule_ids != STAGE_RULE_IDS[stage_id]:
                errors.append(
                    stage_id
                    + " allowedRuleIds must contain the exact canonical rule set"
                )
            expected = STAGE_FIELDS[stage_id]
            if set(requires) != set(expected["requires"]) or len(requires) != len(expected["requires"]):
                errors.append(stage_id + " requires must contain the exact canonical field set")
            if set(produces) != set(expected["produces"]) or len(produces) != len(expected["produces"]):
                errors.append(stage_id + " produces must contain the exact canonical field set")
            missing = sorted(set(requires) - available)
            if missing:
                errors.append(
                    "{} requires fields without an earlier producer: {}".format(
                        stage_id, ", ".join(missing)
                    )
                )
            available.update(produces)

    scoring = contract.get("scoring")
    if not isinstance(scoring, dict):
        errors.append("scoring must be an object")
        return errors

    weights = scoring.get("ruleWeights")
    if not isinstance(weights, dict):
        errors.append("ruleWeights must be an object")
    else:
        if set(weights) != SCORING_RULES:
            errors.append("ruleWeights must contain the exact scoring rule set")
        if not all(isinstance(weight, (int, float)) and not isinstance(weight, bool)
                   for weight in weights.values()):
            errors.append("ruleWeights values must be numbers")
        elif round(sum(weights.values()), 6) != 100.0:
            errors.append("scoring rule weights must total 100.0")

    non_scoring = scoring.get("nonScoringRules")
    if not _is_list_of_strings(non_scoring):
        errors.append("nonScoringRules must be a list of strings")
    else:
        if set(non_scoring) != NON_SCORING_RULES or len(non_scoring) != len(NON_SCORING_RULES):
            errors.append("nonScoringRules must contain the exact non-scoring rule set")
        if isinstance(weights, dict):
            overlap = sorted(set(weights) & set(non_scoring))
            if overlap:
                errors.append(
                    "rules cannot be both scoring and non-scoring: " + ", ".join(overlap)
                )

    hard_gates = scoring.get("hardGates")
    if not _is_list_of_strings(hard_gates):
        errors.append("hardGates must be a list of strings")
    elif set(hard_gates) != HARD_GATES or len(hard_gates) != len(HARD_GATES):
        errors.append("hardGates must contain the exact hard gate set")

    return errors
