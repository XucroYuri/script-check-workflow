import json
from pathlib import Path
from typing import Any, Dict, List, Union


PathLike = Union[str, Path]


def load_contract(path: PathLike) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_contract(contract: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    order = contract.get("stageOrder", [])
    stages = contract.get("stages", {})

    if order != list(stages):
        errors.append("stageOrder must exactly match stages insertion order")

    available = {"script_text", "run_metadata", "target_profile"}
    for stage_id in order:
        stage = stages.get(stage_id, {})
        missing = sorted(set(stage.get("requires", [])) - available)
        if missing:
            errors.append(
                "{} requires fields without an earlier producer: {}".format(
                    stage_id, ", ".join(missing)
                )
            )
        available.update(stage.get("produces", []))

    scoring = contract.get("scoring", {})
    weights = scoring.get("ruleWeights", {})
    non_scoring = scoring.get("nonScoringRules", [])
    if round(sum(weights.values()), 6) != 100.0:
        errors.append("scoring rule weights must total 100.0")
    overlap = sorted(set(weights) & set(non_scoring))
    if overlap:
        errors.append("rules cannot be both scoring and non-scoring: " + ", ".join(overlap))

    required_gates = set(scoring.get("hardGates", []))
    if len(required_gates) != len(scoring.get("hardGates", [])):
        errors.append("hard gate names must be unique")

    return errors
