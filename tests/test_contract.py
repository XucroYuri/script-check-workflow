from copy import deepcopy
import json
import unittest
from pathlib import Path

from scripts.contract import load_contract, validate_contract


ROOT = Path(__file__).resolve().parents[1]


class WorkflowContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract(ROOT / "contracts/workflow-contract.json")

    def test_contract_has_no_validation_errors(self):
        self.assertEqual([], validate_contract(self.contract))

    def test_continuity_inputs_have_explicit_producers(self):
        stages = self.contract["stages"]
        self.assertIn("scene_boundaries", stages["stage2"]["produces"])
        self.assertIn("scene_shot_map", stages["stage3"]["produces"])
        self.assertIn("key_action_events", stages["stage4"]["produces"])

    def test_scoring_weights_total_one_hundred(self):
        total = sum(self.contract["scoring"]["ruleWeights"].values())
        self.assertEqual(100.0, total)

    def test_every_rule_is_scoring_or_explicitly_non_scoring(self):
        scoring = set(self.contract["scoring"]["ruleWeights"])
        non_scoring = set(self.contract["scoring"]["nonScoringRules"])
        self.assertTrue(scoring.isdisjoint(non_scoring))
        self.assertEqual(42, len(scoring | non_scoring))

    def test_contract_declares_canonical_scene_boundary_schema(self):
        schema = self.contract["fieldSchemas"]["scene_boundaries"]
        self.assertEqual("array", schema["type"])
        self.assertEqual(
            ["id", "start_line", "end_line"], schema["items"]["required"]
        )

    def test_contract_declares_continuity_handoff_schemas(self):
        schemas = self.contract["fieldSchemas"]
        self.assertEqual(
            ["scene", "shots"], schemas["scene_shot_map"]["items"]["required"]
        )
        self.assertEqual(
            ["location", "actor", "action", "affected_asset"],
            schemas["key_action_events"]["items"]["required"],
        )

    def test_contract_declares_full_run_unicode_code_point_limit(self):
        self.assertEqual(
            60000, self.contract["inputBudget"]["maxScriptUnicodeCodePoints"]
        )

    def test_missing_required_root_key_is_invalid(self):
        contract = deepcopy(self.contract)
        del contract["stages"]
        self.assertIn(
            "missing required root key: stages", validate_contract(contract)
        )

    def test_noncanonical_contract_path_is_rejected_before_read(self):
        with self.assertRaisesRegex(ValueError, "canonical workflow contract"):
            load_contract(ROOT / "tests" / "untrusted-contract.json")

    def test_non_list_stage_requires_is_invalid(self):
        contract = deepcopy(self.contract)
        contract["stages"]["stage2"]["requires"] = "scene_count"
        self.assertIn(
            "stage2 requires must be a list of strings", validate_contract(contract)
        )

    def test_non_list_stage_produces_is_invalid(self):
        contract = deepcopy(self.contract)
        contract["stages"]["stage2"]["produces"] = "scene_boundaries"
        self.assertIn(
            "stage2 produces must be a list of strings", validate_contract(contract)
        )

    def test_deleted_stage_prerequisite_is_invalid(self):
        contract = deepcopy(self.contract)
        contract["stages"]["stage3"]["requires"].remove("scene_boundaries")
        self.assertIn(
            "stage3 requires must contain the exact canonical field set",
            validate_contract(contract),
        )

    def test_deleted_stage_output_is_invalid(self):
        contract = deepcopy(self.contract)
        contract["stages"]["stage7"]["produces"].remove("acceptance_readiness")
        self.assertIn(
            "stage7 produces must contain the exact canonical field set",
            validate_contract(contract),
        )

    def test_wrong_unicode_code_point_limit_is_invalid(self):
        contract = deepcopy(self.contract)
        contract["inputBudget"]["maxScriptUnicodeCodePoints"] = 59999
        self.assertIn(
            "inputBudget.maxScriptUnicodeCodePoints must equal 60000",
            validate_contract(contract),
        )

    def test_mutated_continuity_field_schema_is_invalid(self):
        contract = deepcopy(self.contract)
        contract["fieldSchemas"]["scene_shot_map"]["items"]["properties"][
            "shots"
        ]["type"] = "integer"
        self.assertIn(
            "scene_shot_map must use the canonical field schema",
            validate_contract(contract),
        )

    def test_mutated_action_event_schema_is_invalid(self):
        contract = deepcopy(self.contract)
        contract["fieldSchemas"]["key_action_events"]["items"]["required"].pop()
        self.assertIn(
            "key_action_events must use the canonical field schema",
            validate_contract(contract),
        )

    def test_incomplete_scoring_rule_set_is_invalid(self):
        contract = deepcopy(self.contract)
        del contract["scoring"]["ruleWeights"]["R1.1"]
        self.assertIn(
            "ruleWeights must contain the exact scoring rule set",
            validate_contract(contract),
        )

    def test_wrong_non_scoring_rules_and_hard_gates_are_invalid(self):
        contract = deepcopy(self.contract)
        contract["scoring"]["nonScoringRules"].pop()
        contract["scoring"]["hardGates"].pop()
        errors = validate_contract(contract)
        self.assertIn(
            "nonScoringRules must contain the exact non-scoring rule set", errors
        )
        self.assertIn("hardGates must contain the exact hard gate set", errors)

    def test_eval_manifest_covers_required_adversarial_risks(self):
        manifest_path = ROOT / "evals/manifest.json"
        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        case_ids = {case["id"] for case in manifest["cases"]}
        self.assertEqual(
            {
                "prompt-injection",
                "continuity-ambiguous",
                "high-severity-low-weight"
            },
            case_ids,
        )
        self.assertEqual(3, manifest["runsPerHost"])


if __name__ == "__main__":
    unittest.main()
