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
REQUIRED_ROOT_KEYS = {
    "contractVersion",
    "stageOrder",
    "workflowPhases",
    "inputBudget",
    "fieldSchemas",
    "stages",
    "scoring",
}


def load_contract(path: PathLike) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
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

    input_budget = contract.get("inputBudget")
    if not isinstance(input_budget, dict):
        errors.append("inputBudget must be an object")
    elif input_budget.get("maxScriptUnicodeCodePoints") != 60000:
        errors.append("inputBudget.maxScriptUnicodeCodePoints must equal 60000")

    field_schemas = contract.get("fieldSchemas")
    if not isinstance(field_schemas, dict):
        errors.append("fieldSchemas must be an object")
    elif field_schemas.get("scene_boundaries") != SCENE_BOUNDARIES_SCHEMA:
        errors.append("scene_boundaries must use the canonical field schema")

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
