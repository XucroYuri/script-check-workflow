import unittest
from pathlib import Path

from scripts.contract import load_contract


ROOT = Path(__file__).resolve().parents[1]


class WorkflowOrderTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract(ROOT / "contracts/workflow-contract.json")
        self.phases = self.contract["workflowPhases"]

    def test_candidate_is_reviewed_before_gates_and_scoring(self):
        self.assertLess(
            self.phases.index("synthesize_candidate"),
            self.phases.index("review_candidate"),
        )
        self.assertLess(
            self.phases.index("review_candidate"),
            self.phases.index("evaluate_hard_gates"),
        )
        self.assertLess(
            self.phases.index("evaluate_hard_gates"),
            self.phases.index("score_candidate"),
        )

    def test_skill_does_not_score_original_as_final(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("候选稿完整复审", skill)
        self.assertIn("只对候选稿评分", skill)
        self.assertIn("BLOCKED 时不得输出 standardized-script", skill)

    def test_continuity_example_does_not_autopatch_inferred_blood(self):
        continuity = (ROOT / "references/stage4-5-asset-continuity.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("血迹属于推断，不得进入 low_risk_patch", continuity)

    def test_handoff_uses_stable_finding_and_patch_records(self):
        handoff = (ROOT / "references/handoff-protocol.md").read_text(
            encoding="utf-8"
        )
        for field in (
            "finding_id:",
            "stage_id:",
            "location_id:",
            "source_span:",
            "source_text_sha256:",
            "correction_proposal:",
            "proposal_id:",
            "expected_source_sha256:",
            "affected_assets:",
            "requires_writer_decision:",
        ):
            self.assertIn(field, handoff)
        self.assertIn("BLOCKED: STALE_PATCH", handoff)

    def test_workflow_limits_correction_to_one_cycle(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("自动纠正循环上限严格为 1", skill)
        self.assertIn("不得启动第二轮", skill)

    def test_candidate_metrics_are_the_only_delivery_evidence(self):
        stage7 = (ROOT / "references/stage7-industrial.md").read_text(
            encoding="utf-8"
        )
        output = (ROOT / "references/output-artifacts.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("候选稿", stage7)
        self.assertIn("原稿 metrics 不得作为最终验收证据", stage7)
        self.assertIn("original_baseline", output)
        self.assertIn("candidate_final", output)
        self.assertIn("只有 `candidate_final` 控制交付状态", output)


if __name__ == "__main__":
    unittest.main()
