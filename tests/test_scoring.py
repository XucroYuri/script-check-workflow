import unittest
from pathlib import Path

from scripts.contract import load_contract
from scripts.scoring import classify_delivery, compute_score


ROOT = Path(__file__).resolve().parents[1]


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract(ROOT / "contracts/workflow-contract.json")
        self.all_pass = {
            rule_id: {"applicable": 1, "passed": 1}
            for rule_id in self.contract["scoring"]["ruleWeights"]
        }
        self.gates = {
            gate: True for gate in self.contract["scoring"]["hardGates"]
        }

    def test_all_applicable_rules_pass_scores_one_hundred(self):
        self.assertEqual(100.0, compute_score(self.contract, self.all_pass))

    def test_non_applicable_rules_are_renormalized(self):
        results = dict(self.all_pass)
        results["R6.28"] = {"applicable": 0, "passed": 0}
        results["R6.29"] = {"applicable": 0, "passed": 0}
        self.assertEqual(100.0, compute_score(self.contract, results))

    def test_high_risk_gate_blocks_even_with_perfect_score(self):
        gates = dict(self.gates)
        gates["unresolved_high_findings_zero"] = False
        self.assertEqual("BLOCKED", classify_delivery(self.contract, 100.0, gates))

    def test_ready_requires_ninety_and_all_gates(self):
        self.assertEqual("READY", classify_delivery(self.contract, 90.0, self.gates))
        self.assertEqual("CONDITIONAL", classify_delivery(self.contract, 89.9, self.gates))
        self.assertEqual("REWORK", classify_delivery(self.contract, 69.9, self.gates))

    def test_invalid_counts_raise(self):
        results = dict(self.all_pass)
        results["R1.1"] = {"applicable": 1, "passed": 2}
        with self.assertRaises(ValueError):
            compute_score(self.contract, results)

    def test_rule_result_ids_must_exactly_match_contract(self):
        missing = dict(self.all_pass)
        del missing["R1.1"]
        extra = dict(self.all_pass)
        extra["R99.99"] = {"applicable": 1, "passed": 1}

        for name, results in (("missing", missing), ("extra", extra)):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    compute_score(self.contract, results)

    def test_gate_ids_must_exactly_match_contract(self):
        missing = dict(self.gates)
        del missing["input_budget_valid"]
        extra = dict(self.gates)
        extra["unknown_gate"] = True

        for name, gates in (("missing", missing), ("extra", extra)):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    classify_delivery(self.contract, 100.0, gates)

    def test_gate_values_must_be_booleans(self):
        for value in ("false", 0, 1, None):
            with self.subTest(value=value):
                gates = dict(self.gates)
                gates["contract_valid"] = value
                with self.assertRaises(ValueError):
                    classify_delivery(self.contract, 100.0, gates)

    def test_rule_counts_must_be_non_boolean_integers(self):
        for field in ("applicable", "passed"):
            for value in (True, False, 1.0, "1", None):
                with self.subTest(field=field, value=value):
                    results = dict(self.all_pass)
                    results["R1.1"] = {"applicable": 1, "passed": 1}
                    results["R1.1"][field] = value
                    with self.assertRaises(ValueError):
                        compute_score(self.contract, results)

    def test_no_applicable_rules_raise(self):
        results = {
            rule_id: {"applicable": 0, "passed": 0}
            for rule_id in self.contract["scoring"]["ruleWeights"]
        }
        with self.assertRaises(ValueError):
            compute_score(self.contract, results)


if __name__ == "__main__":
    unittest.main()
