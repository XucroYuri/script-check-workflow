from copy import deepcopy
from hashlib import sha256
import unittest
from pathlib import Path

from scripts.contract import load_contract, validate_contract

try:
    from scripts import workflow_policy as policy
except ImportError:
    policy = None


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PHASES = [
    "ingest_untrusted_input",
    "analyze_original",
    "resolve_corrections",
    "synthesize_candidate",
    "review_candidate",
    "evaluate_hard_gates",
    "score_candidate",
    "deliver",
]


def proposal(
    *,
    proposal_id="P-stage1-R1.1-S01-SH001-001",
    finding_id="F-stage1-R1.1-S01-SH001-001",
    location_id="S01-SH001",
    start_line=1,
    end_line=1,
    expected_hash=None,
    replacement="replacement",
    assets=None,
    states=None,
    writer_decision=False,
):
    assets = ["prop"] if assets is None else assets
    states = {"prop": "broken"} if states is None else states
    return {
        "proposal_id": proposal_id,
        "finding_ids": [finding_id],
        "location_id": location_id,
        "source_span": {"start_line": start_line, "end_line": end_line},
        "expected_source_sha256": expected_hash or ("0" * 64),
        "replacement": replacement,
        "affected_assets": assets,
        "asset_state_changes": states,
        "requires_writer_decision": writer_decision,
    }


def finding(**overrides):
    record = {
        "finding_id": "F-stage7-R7.34-S01-SH001-001",
        "stage_id": "stage7",
        "location_id": "S01-SH001",
        "source_span": {"start_line": 1, "end_line": 1},
        "source_text_sha256": "0" * 64,
        "rule_id": "R7.34",
        "severity": "low",
        "description": "description",
        "original": "original",
        "corrected": "corrected",
        "correction_basis": "basis",
        "confidence": 0.9,
        "writer_decision_needed": False,
    }
    record.update(overrides)
    return record


class WorkflowOrderTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract(ROOT / "contracts/workflow-contract.json")
        self.assertIsNotNone(policy, "scripts.workflow_policy must exist")

    def test_workflow_uses_the_full_exact_phase_order(self):
        self.assertEqual(EXPECTED_PHASES, self.contract["workflowPhases"])

    def test_contract_declares_the_machine_correction_policy(self):
        self.assertEqual(
            ["finding", "correction_proposal", "metrics"],
            self.contract["reviewerOutput"]["components"],
        )
        correction = self.contract["correctionPolicy"]
        self.assertEqual(1, correction["maxAutomaticCorrectionCycles"])
        self.assertEqual("one_based_inclusive", correction["sourceSpanConvention"])
        self.assertEqual("normalized_lf_utf8_sha256", correction["sourceHashConvention"])
        self.assertEqual(
            ["blood", "displacement", "occlusion", "orientation"],
            correction["writerDecisionContinuityStates"],
        )

        mutated = deepcopy(self.contract)
        mutated["correctionPolicy"]["maxAutomaticCorrectionCycles"] = 2
        self.assertIn(
            "correctionPolicy must use the canonical closed-loop policy",
            validate_contract(mutated),
        )

    def test_only_one_automatic_correction_cycle_is_allowed(self):
        self.assertTrue(policy.can_start_automatic_correction_cycle(0))
        self.assertFalse(policy.can_start_automatic_correction_cycle(1))
        with self.assertRaisesRegex(
            policy.WorkflowBlocked, "BLOCKED: CORRECTION_CYCLE_LIMIT"
        ):
            policy.require_automatic_correction_cycle(1)

    def test_overlapping_inclusive_spans_conflict(self):
        left = proposal(start_line=3, end_line=5)
        right = proposal(
            proposal_id="P-stage2-R2.5-S02-SH001-001",
            finding_id="F-stage2-R2.5-S02-SH001-001",
            location_id="S02-SH001",
            start_line=5,
            end_line=7,
            assets=["other"],
            states={"other": "clean"},
        )
        self.assertIn("overlapping_source_span", policy.conflict_reasons(left, right))

    def test_identical_location_ids_conflict(self):
        left = proposal(start_line=1, end_line=1)
        right = proposal(
            proposal_id="P-stage2-R2.5-S01-SH001-001",
            finding_id="F-stage2-R2.5-S01-SH001-001",
            start_line=3,
            end_line=3,
            assets=["other"],
            states={"other": "clean"},
        )
        self.assertIn("identical_location_id", policy.conflict_reasons(left, right))

    def test_incompatible_shared_asset_states_conflict(self):
        left = proposal(start_line=1, end_line=1)
        right = proposal(
            proposal_id="P-stage2-R2.5-S02-SH001-001",
            finding_id="F-stage2-R2.5-S02-SH001-001",
            location_id="S02-SH001",
            start_line=3,
            end_line=3,
            states={"prop": "intact"},
        )
        self.assertIn(
            "incompatible_asset_state", policy.conflict_reasons(left, right)
        )

    def test_stale_hash_fails_closed(self):
        stale = proposal(expected_hash="f" * 64)
        with self.assertRaisesRegex(policy.WorkflowBlocked, "BLOCKED: STALE_PATCH"):
            policy.apply_correction_proposals("original", [stale])

    def test_hash_matched_proposal_applies_to_the_inclusive_span(self):
        script = "first\r\nsecond\r\nthird"
        current_hash = policy.source_fragment_sha256(script, 2, 2)
        patch = proposal(
            start_line=2,
            end_line=2,
            expected_hash=current_hash,
            replacement="changed",
        )
        self.assertEqual(
            "first\nchanged\nthird",
            policy.apply_correction_proposals(script, [patch]),
        )

    def test_writer_decision_proposal_cannot_auto_apply(self):
        source_hash = policy.source_fragment_sha256("original", 1, 1)
        protected = proposal(expected_hash=source_hash, writer_decision=True)
        with self.assertRaisesRegex(
            policy.WorkflowBlocked, "BLOCKED: WRITER_DECISION_REQUIRED"
        ):
            policy.apply_correction_proposals("original", [protected])

    def test_blocked_delivery_selects_candidate_and_never_standardized(self):
        artifacts = policy.select_delivery_artifacts("BLOCKED")
        self.assertIn("candidate-script", artifacts)
        self.assertNotIn("standardized-script", artifacts)

    def test_inferred_continuity_states_require_writer_decision(self):
        for state in ("blood", "displacement", "occlusion", "orientation"):
            with self.subTest(state=state):
                self.assertTrue(policy.continuity_state_requires_writer_decision(state))
        self.assertFalse(
            policy.continuity_state_requires_writer_decision("confirmed_broken")
        )

    def test_source_fragment_hash_normalizes_lf_and_has_no_terminal_newline(self):
        script = "alpha\r\nbeta\r\ngamma\r\n"
        self.assertEqual("beta\ngamma", policy.source_fragment(script, 2, 3))
        self.assertEqual(
            sha256("beta\ngamma".encode("utf-8")).hexdigest(),
            policy.source_fragment_sha256(script, 2, 3),
        )
        self.assertEqual("alpha", policy.source_fragment("alpha\r\n\r\n", 1, 2))

    def test_finding_and_proposal_ids_are_deterministic_and_unique(self):
        records = [
            {"stage_id": "stage2", "rule_id": "R2.5", "location_id": "S02", "source_span": {"start_line": 8, "end_line": 8}},
            {"stage_id": "stage1", "rule_id": "R1.2", "location_id": "S01", "source_span": {"start_line": 2, "end_line": 3}},
            {"stage_id": "stage1", "rule_id": "R1.1", "location_id": "S01", "source_span": {"start_line": 2, "end_line": 3}},
        ]
        assigned = policy.assign_finding_ids(records)
        self.assertEqual(["R1.1", "R1.2", "R2.5"], [item["rule_id"] for item in assigned])
        ids = [item["finding_id"] for item in assigned]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            [identifier.replace("F-", "P-", 1) for identifier in ids],
            [policy.proposal_id_for_finding_id(identifier) for identifier in ids],
        )

    def test_stage_output_parser_validates_all_three_components(self):
        payload = {
            "finding": [finding()],
            "correction_proposal": [
                proposal(
                    proposal_id="P-stage7-R7.34-S01-SH001-001",
                    finding_id="F-stage7-R7.34-S01-SH001-001",
                    expected_hash="0" * 64,
                )
            ],
            "metrics": {
                "team_handoff_score": 0.9,
                "acceptance_readiness": 0.9,
                "stage7_pass_rate": 0.9,
            },
        }
        self.assertEqual(payload, policy.parse_stage_output(payload, "stage7"))
        for component in ("finding", "correction_proposal", "metrics"):
            with self.subTest(component=component):
                invalid = dict(payload)
                del invalid[component]
                with self.assertRaisesRegex(
                    policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
                ):
                    policy.parse_stage_output(invalid, "stage7")

        invalid_finding = dict(payload)
        invalid_finding["finding"] = [finding(severity="critical")]
        with self.assertRaisesRegex(
            policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
        ):
            policy.parse_stage_output(invalid_finding, "stage7")

        invalid_proposal = deepcopy(payload)
        invalid_proposal["correction_proposal"][0]["proposal_id"] = "P-wrong"
        with self.assertRaisesRegex(
            policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
        ):
            policy.parse_stage_output(invalid_proposal, "stage7")

        invalid_metrics = deepcopy(payload)
        del invalid_metrics["metrics"]["stage7_pass_rate"]
        with self.assertRaisesRegex(
            policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
        ):
            policy.parse_stage_output(invalid_metrics, "stage7")

    def test_documented_stage45_example_uses_canonical_separate_records(self):
        continuity = (ROOT / "references/stage4-5-asset-continuity.md").read_text(
            encoding="utf-8"
        )
        example = continuity.split("## Finding 输出Schema", 1)[1].split(
            "## Ledger 输出Schema", 1
        )[0]
        self.assertIn("finding_id:", example)
        self.assertIn("source_text_sha256:", example)
        self.assertIn("correction_proposal:", example)
        self.assertIn("expected_source_sha256:", example)
        self.assertIn("地面上的断刀保持断裂状态。角色B从断刀旁跨过。", example)
        self.assertIn("corrected:", example)

    def test_security_policy_permits_only_the_three_output_components(self):
        security = (ROOT / "references/security-model.md").read_text(encoding="utf-8")
        self.assertIn("finding、correction_proposal 和 metrics", security)
        self.assertIn("BLOCKED: INVALID_STAGE_OUTPUT", security)


if __name__ == "__main__":
    unittest.main()
