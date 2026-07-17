from typing import Any, Dict


RuleResult = Dict[str, int]


def compute_score(
    contract: Dict[str, Any], rule_results: Dict[str, RuleResult]
) -> float:
    weights = contract["scoring"]["ruleWeights"]
    missing = sorted(set(weights) - set(rule_results))
    extra = sorted(set(rule_results) - set(weights))
    if missing or extra:
        raise ValueError("rule result IDs must exactly match scoring rule IDs")

    applicable_weight = 0.0
    earned_weight = 0.0
    for rule_id, weight in weights.items():
        applicable = rule_results[rule_id]["applicable"]
        passed = rule_results[rule_id]["passed"]
        if (
            type(applicable) is not int
            or type(passed) is not int
            or applicable < 0
            or passed < 0
            or passed > applicable
        ):
            raise ValueError("invalid counts for " + rule_id)
        if applicable == 0:
            continue
        applicable_weight += weight
        earned_weight += weight * (passed / applicable)

    if applicable_weight == 0:
        raise ValueError("at least one scoring rule must be applicable")
    return round(100.0 * earned_weight / applicable_weight, 1)


def classify_delivery(
    contract: Dict[str, Any], score: float, gates: Dict[str, bool]
) -> str:
    expected = set(contract["scoring"]["hardGates"])
    if set(gates) != expected:
        raise ValueError("gate IDs must exactly match contract hard gates")
    if any(not isinstance(value, bool) for value in gates.values()):
        raise ValueError("gate values must be booleans")
    if not all(gates.values()):
        return "BLOCKED"
    if score >= 90.0:
        return "READY"
    if score >= 70.0:
        return "CONDITIONAL"
    return "REWORK"
