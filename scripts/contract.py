import json
from pathlib import Path
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
    "writerDecisionContinuityStates": [
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
        "required": ["id", "start_line", "end_line"],
        "properties": {
            "id": {"type": "string"},
            "start_line": {"type": "integer", "minimum": 1},
            "end_line": {"type": "integer", "minimum": 1},
        },
    },
}
SCENE_SHOT_MAP_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["scene", "shots"],
        "properties": {
            "scene": {"type": "string"},
            "shots": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
            },
        },
    },
}
KEY_ACTION_EVENTS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["location", "actor", "action", "affected_asset"],
        "properties": {
            "location": {"type": "string"},
            "actor": {"type": "string"},
            "action": {"type": "string"},
            "affected_asset": {"type": "string"},
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
            if field_schemas.get(field_name) != schema:
                errors.append(field_name + " must use the canonical field schema")

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
            if not _is_list_of_strings(requires):
                errors.append(stage_id + " requires must be a list of strings")
                requires = []
            if not _is_list_of_strings(produces):
                errors.append(stage_id + " produces must be a list of strings")
                produces = []
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
