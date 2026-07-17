from copy import deepcopy
from hashlib import sha256
import json
import math
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
STAGE_DOCUMENTS = {
    "stage1": "references/stage1-principles.md",
    "stage2": "references/stage2-scene.md",
    "stage3": "references/stage3-shot.md",
    "stage4": "references/stage4-action.md",
    "stage4_5": "references/stage4-5-asset-continuity.md",
    "stage5": "references/stage5-ai-adapt.md",
    "stage6": "references/stage6-dialogue.md",
    "stage7": "references/stage7-industrial.md",
}


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
    states = (
        {"prop": {"category": "condition", "value": "broken"}}
        if states is None
        else states
    )
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


def valid_target_profile(**overrides):
    profile = {
        "provider": "OpenAI",
        "model": "Sora",
        "model_version": "2026-07",
        "mode": "T2V",
        "clip_duration_seconds": 8,
        "aspect_ratio": "16:9",
        "reference_assets_available": False,
    }
    profile.update(overrides)
    return profile


def stage5_payload(target_profile_declared):
    stage5_finding = finding(
        finding_id="F-stage5-R5.20-S01-SH001-001",
        stage_id="stage5",
        rule_id="R5.20",
    )
    stage5_proposal = proposal(
        proposal_id="P-stage5-R5.20-S01-SH001-001",
        finding_id="F-stage5-R5.20-S01-SH001-001",
    )
    return {
        "finding": [stage5_finding],
        "correction_proposal": [stage5_proposal],
        "metrics": {
            "target_profile_declared": target_profile_declared,
            "generation_risk_score": 2.0,
            "anchor_coverage": 1.0,
            "visual_nail_count": 1,
            "negative_constraint_coverage": 1.0,
            "high_risk_shots": 0,
            "failure_mode_distribution": {
                "face_swap": 0,
                "limb_error": 0,
                "prop_vanish": 0,
                "lr_drift": 0,
                "bg_jump": 0,
                "action_break": 0,
                "occlusion": 0,
            },
            "stage5_pass_rate": 1.0,
        },
    }


def documented_metric_example(relative_path, stage_id):
    text = (ROOT / relative_path).read_text(encoding="utf-8")
    marker = "<!-- canonical-metrics:{} -->".format(stage_id)
    if marker not in text:
        raise AssertionError("{} is missing {}".format(relative_path, marker))
    block = text.split(marker, 1)[1].split("```json", 1)[1].split("```", 1)[0]
    return json.loads(block)


def valid_metrics(stage_id):
    examples = {
        "stage1": {
            "scene_count": 1,
            "scene_boundaries": [{"id": "S01", "start_line": 1, "end_line": 3}],
            "character_count": 2,
            "pronoun_density": 0.1,
            "intent_word_count": 0,
            "metaphor_count": 0,
            "six_layer_coverage": 0.8,
            "stage1_pass_rate": 0.9,
        },
        "stage2": {
            "scene_boundaries": [{"id": "S01", "start_line": 1, "end_line": 3}],
            "anchor_count_per_scene": [
                {"scene": "S01", "anchors": 2, "names": ["door", "lamp"]}
            ],
            "initial_state_completeness": 0.8,
            "consistency_score": 0.9,
            "atmosphere_specificity": 0.7,
            "stage2_pass_rate": 0.85,
        },
        "stage3": {
            "shot_count": 2,
            "scene_shot_map": [{"scene": "S01", "shots": ["S01-SH01"]}],
            "avg_info_layers": 4.5,
            "format_consistency": 1.0,
            "risk_distribution": {"low": 1, "medium": 1, "high": 0},
            "dual_high_conflict_count": 0,
            "stage3_pass_rate": 0.9,
        },
        "stage4": {
            "key_action_events": [
                {
                    "location": "S01-SH01",
                    "actor": "A",
                    "action": "opens",
                    "affected_asset": "door",
                }
            ],
            "action_complexity": 3.0,
            "emotion_leakage_count": 0,
            "missing_physics_feedback": 0,
            "action_chain_issues": 0,
            "overloaded_shots": 0,
            "interaction_risk_count": 0,
            "stage4_pass_rate": 1.0,
        },
        "stage4_5": {
            "tracked_asset_count": {"character": 2, "scene": 1, "prop": 1},
            "continuity_risk_count": {"high": 0, "medium": 0, "low": 1},
            "high_risk_asset_jumps": [],
            "requires_writer_confirmation_count": 0,
            "suggested_visual_anchor_updates": [
                {"asset": "door", "location": "S01-SH01", "reason": "continuity"}
            ],
            "low_risk_patch_count": 1,
            "stage4_5_pass_rate": 1.0,
        },
        "stage5": stage5_payload(True)["metrics"],
        "stage6": {
            "isolation_compliance": 1.0,
            "ai_taste_score": 2.0,
            "dialogue_mismatch_count": 0,
            "natural_speech_score": 0.9,
            "stage6_pass_rate": 0.95,
        },
        "stage7": {
            "team_handoff_score": {
                "director": 0.9,
                "storyboard": 0.9,
                "art": 0.8,
                "animation": 0.8,
                "ai_generation": 0.9,
                "continuity_handoff": 1.0,
            },
            "acceptance_readiness": 0.9,
            "stage7_pass_rate": 0.9,
        },
    }
    return deepcopy(examples[stage_id])


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
        self.assertIn("writerDecisionStateCategories", correction)
        self.assertIn("assetStateChangeCategories", correction)
        self.assertEqual(
            ["blood", "displacement", "occlusion", "orientation"],
            correction["writerDecisionStateCategories"],
        )
        self.assertEqual(
            ["condition", "blood", "displacement", "occlusion", "orientation"],
            correction["assetStateChangeCategories"],
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
            states={"other": {"category": "condition", "value": "clean"}},
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
            states={"other": {"category": "condition", "value": "clean"}},
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
            states={"prop": {"category": "condition", "value": "intact"}},
        )
        self.assertIn(
            "incompatible_asset_state", policy.conflict_reasons(left, right)
        )

    def test_stale_hash_fails_closed(self):
        stale = proposal(expected_hash="f" * 64)
        with self.assertRaisesRegex(policy.WorkflowBlocked, "BLOCKED: STALE_PATCH"):
            policy.apply_correction_proposals("original", [stale])

    def test_stale_hash_wins_over_writer_decision(self):
        stale_and_protected = proposal(
            expected_hash="f" * 64,
            states={"prop": {"category": "blood", "value": "blood_stained"}},
            writer_decision=True,
        )
        with self.assertRaisesRegex(policy.WorkflowBlocked, "BLOCKED: STALE_PATCH"):
            policy.apply_correction_proposals("original", [stale_and_protected])

    def test_invalid_span_wins_over_conflict_and_writer_decision(self):
        invalid = proposal(
            start_line=0,
            end_line=1,
            states={"prop": {"category": "blood", "value": "blood_stained"}},
            writer_decision=True,
        )
        conflicting = proposal(
            proposal_id="P-stage2-R2.5-S01-SH001-001",
            finding_id="F-stage2-R2.5-S01-SH001-001",
            start_line=1,
            end_line=1,
            expected_hash=policy.source_fragment_sha256("original", 1, 1),
            states={"prop": {"category": "condition", "value": "intact"}},
        )
        with self.assertRaisesRegex(policy.WorkflowBlocked, "BLOCKED: STALE_PATCH"):
            policy.apply_correction_proposals("original", [invalid, conflicting])

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

    def test_false_flagged_blood_proposal_cannot_apply(self):
        script = "original"
        source_hash = policy.source_fragment_sha256(script, 1, 1)
        protected = proposal(
            expected_hash=source_hash,
            states={"prop": {"category": "blood", "value": "blood_stained"}},
            writer_decision=False,
        )
        with self.assertRaisesRegex(
            policy.WorkflowBlocked, "BLOCKED: WRITER_DECISION_REQUIRED"
        ):
            policy.apply_correction_proposals(script, [protected])
        self.assertEqual("original", script)

    def test_unknown_or_malformed_state_category_fails_closed(self):
        script = "original"
        source_hash = policy.source_fragment_sha256(script, 1, 1)
        invalid_states = (
            {"prop": {"category": "contamination", "value": "dirty"}},
            {"prop": "blood_stained"},
            {"prop": {"category": "blood"}},
        )
        for states in invalid_states:
            with self.subTest(states=states):
                invalid = proposal(expected_hash=source_hash, states=states)
                with self.assertRaisesRegex(
                    policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
                ):
                    policy.apply_correction_proposals(script, [invalid])

    def test_blocked_delivery_selects_candidate_and_never_standardized(self):
        artifacts = policy.select_delivery_artifacts("BLOCKED")
        self.assertIn("candidate-script", artifacts)
        self.assertNotIn("standardized-script", artifacts)

    def test_rework_delivery_selects_candidate_and_never_standardized(self):
        try:
            artifacts = policy.select_delivery_artifacts("REWORK")
        except ValueError as exc:
            self.fail("REWORK must be a supported delivery status: {}".format(exc))
        self.assertIn("candidate-script", artifacts)
        self.assertNotIn("standardized-script", artifacts)

    def test_target_profile_null_is_present_but_gate_is_false(self):
        derive = getattr(policy, "target_profile_declared_gate", None)
        require = getattr(policy, "validate_target_profile_input", None)
        self.assertIsNotNone(derive, "target-profile gate derivation is required")
        self.assertIsNotNone(require, "target-profile input validation is required")
        self.assertFalse(derive(None))
        self.assertFalse(require(None))

    def test_valid_target_profile_sets_gate_true(self):
        derive = getattr(policy, "target_profile_declared_gate", None)
        require = getattr(policy, "validate_target_profile_input", None)
        self.assertIsNotNone(derive, "target-profile gate derivation is required")
        self.assertIsNotNone(require, "target-profile input validation is required")
        profile = valid_target_profile()
        self.assertTrue(derive(profile))
        self.assertTrue(require(profile))

    def test_invalid_non_null_target_profile_fails_closed(self):
        derive = getattr(policy, "target_profile_declared_gate", None)
        require = getattr(policy, "validate_target_profile_input", None)
        self.assertIsNotNone(derive, "target-profile gate derivation is required")
        self.assertIsNotNone(require, "target-profile input validation is required")
        invalid_profiles = (
            valid_target_profile(mode="unsupported"),
            valid_target_profile(mode=[]),
            valid_target_profile(aspect_ratio="0:9"),
            valid_target_profile(extra="not allowed"),
            {key: value for key, value in valid_target_profile().items() if key != "model"},
        )
        for profile in invalid_profiles:
            with self.subTest(profile=profile):
                try:
                    derived = derive(profile)
                except Exception as exc:
                    self.fail("invalid profile must derive false, not error: {}".format(exc))
                self.assertFalse(derived)
                with self.assertRaisesRegex(
                    policy.WorkflowBlocked, "BLOCKED: CONTRACT_ERROR"
                ):
                    require(profile)

    def test_stage5_parser_accepts_boolean_target_profile_gate_and_exact_metrics(self):
        metrics = {
            "target_profile_declared": True,
            "generation_risk_score": 2.0,
            "anchor_coverage": 1.0,
            "visual_nail_count": 1,
            "negative_constraint_coverage": 1.0,
            "high_risk_shots": 0,
            "failure_mode_distribution": {
                "face_swap": 0,
                "limb_error": 0,
                "prop_vanish": 0,
                "lr_drift": 0,
                "bg_jump": 0,
                "action_break": 0,
                "occlusion": 0,
            },
            "stage5_pass_rate": 1.0,
        }
        payload = {"finding": [], "correction_proposal": [], "metrics": metrics}
        try:
            parsed = policy.parse_stage_output(
                payload,
                "stage5",
                prerequisites={"target_profile": valid_target_profile()},
            )
        except policy.WorkflowBlocked as exc:
            self.fail("canonical Stage 5 metrics must parse: {}".format(exc))
        self.assertEqual(payload, parsed)

        for invalid_metrics in (
            {key: value for key, value in metrics.items() if key != "target_profile_declared"},
            dict(metrics, unexpected=True),
            dict(metrics, target_profile_declared=1),
        ):
            with self.subTest(metrics=invalid_metrics):
                with self.assertRaisesRegex(
                    policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
                ):
                    policy.parse_stage_output(
                        {
                            "finding": [],
                            "correction_proposal": [],
                            "metrics": invalid_metrics,
                        },
                        "stage5",
                        prerequisites={"target_profile": valid_target_profile()},
                    )

    def test_documented_metric_example_for_every_stage_parses(self):
        for stage_id, relative_path in STAGE_DOCUMENTS.items():
            with self.subTest(stage_id=stage_id):
                metrics = documented_metric_example(relative_path, stage_id)
                payload = {
                    "finding": [],
                    "correction_proposal": [],
                    "metrics": metrics,
                }
                prerequisites = (
                    {"target_profile": valid_target_profile()}
                    if stage_id == "stage5"
                    else None
                )
                try:
                    parsed = policy.parse_stage_output(
                        payload, stage_id, prerequisites=prerequisites
                    )
                except Exception as exc:
                    self.fail(
                        "documented {} metrics must parse: {}".format(stage_id, exc)
                    )
                self.assertEqual(payload, parsed)

    def test_documented_stage3_shot_totals_are_cross_field_consistent(self):
        metrics = documented_metric_example(
            STAGE_DOCUMENTS["stage3"], "stage3"
        )
        risk_total = sum(metrics["risk_distribution"].values())
        mapped_shot_total = sum(
            len(scene["shots"]) for scene in metrics["scene_shot_map"]
        )
        self.assertEqual(metrics["shot_count"], risk_total)
        self.assertEqual(metrics["shot_count"], mapped_shot_total)

    def test_handoff_lists_the_exact_canonical_metric_keys(self):
        text = (ROOT / "references/handoff-protocol.md").read_text(encoding="utf-8")
        marker = "<!-- canonical-stage-metric-keys -->"
        self.assertIn(marker, text)
        block = text.split(marker, 1)[1].split("```json", 1)[1].split("```", 1)[0]
        documented = json.loads(block)
        expected = {
            stage_id: [
                field
                for field in self.contract["stages"][stage_id]["produces"]
                if not field.endswith("_findings")
            ]
            for stage_id in self.contract["stageOrder"]
        }
        self.assertEqual(expected, documented)

    def test_handoff_prerequisite_examples_match_declared_requires(self):
        text = (ROOT / "references/handoff-protocol.md").read_text(encoding="utf-8")
        stage3 = text.split("### Stage 3: 镜头级检查", 1)[1].split(
            "### Stage 4: 动作表演检查", 1
        )[0]
        stage4_5 = text.split("### Stage 4.5: 资产连续性追踪层", 1)[1].split(
            "### Stage 5: AI生成适配检查", 1
        )[0]
        self.assertIn("names:", stage3)
        self.assertIn("names:", stage4_5)

        stage7 = text.split("### Stage 7: 工业化检查", 1)[1].split("---", 1)[0]
        for field in self.contract["stages"]["stage7"]["requires"]:
            if field != "script_text":
                with self.subTest(required_field=field):
                    self.assertIn(field, stage7)
        for stale_field in (
            "continuity_risk_high",
            "continuity_risk_total",
            "total_high_findings",
            "total_findings",
        ):
            with self.subTest(stale_field=stale_field):
                self.assertNotIn(stale_field, stage7)

        continuity = (ROOT / "references/stage4-5-asset-continuity.md").read_text(
            encoding="utf-8"
        )
        downstream = continuity.split("## 下游handoff", 1)[1].split(
            "## 非计分说明", 1
        )[0]
        self.assertNotIn("continuity_risk_high", downstream)
        self.assertNotIn("continuity_risk_total", downstream)

    def test_metric_values_fail_closed_for_types_ranges_and_nested_shapes(self):
        cases = []

        def add(name, stage_id, field, value):
            metrics = valid_metrics(stage_id)
            metrics[field] = value
            cases.append((name, stage_id, metrics))

        add("integer string", "stage1", "scene_count", "not-an-integer")
        add("integer bool", "stage1", "scene_count", True)
        add("negative count", "stage1", "character_count", -1)
        add("object pass rate", "stage1", "stage1_pass_rate", {})
        add("pass rate above one", "stage2", "stage2_pass_rate", 1.01)
        add("negative ratio", "stage2", "consistency_score", -0.01)
        add("nan", "stage3", "stage3_pass_rate", math.nan)
        add("positive infinity", "stage3", "avg_info_layers", math.inf)
        add("negative infinity", "stage6", "ai_taste_score", -math.inf)
        add("scene boundaries string", "stage1", "scene_boundaries", "S01")
        add(
            "scene boundary extra property",
            "stage1",
            "scene_boundaries",
            [{"id": "S01", "start_line": 1, "end_line": 3, "extra": True}],
        )
        add(
            "scene boundary reversed line span",
            "stage1",
            "scene_boundaries",
            [{"id": "S01", "start_line": 3, "end_line": 1}],
        )
        add(
            "anchor name non-string",
            "stage2",
            "anchor_count_per_scene",
            [{"scene": "S01", "anchors": 1, "names": [1]}],
        )
        add(
            "empty scene shot list",
            "stage3",
            "scene_shot_map",
            [{"scene": "S01", "shots": []}],
        )
        add(
            "risk distribution extra property",
            "stage3",
            "risk_distribution",
            {"low": 1, "medium": 0, "high": 0, "unknown": 0},
        )
        add(
            "action event missing string",
            "stage4",
            "key_action_events",
            [
                {
                    "location": "S01-SH01",
                    "actor": "A",
                    "action": "opens",
                    "affected_asset": 7,
                }
            ],
        )
        add(
            "anchor update missing property",
            "stage4_5",
            "suggested_visual_anchor_updates",
            [{"asset": "door", "location": "S01-SH01"}],
        )
        add(
            "failure mode extra property",
            "stage5",
            "failure_mode_distribution",
            dict(valid_metrics("stage5")["failure_mode_distribution"], unknown=0),
        )
        add("generation risk above ten", "stage5", "generation_risk_score", 10.1)
        add("AI taste below one", "stage6", "ai_taste_score", 0.9)
        add(
            "handoff score extra property",
            "stage7",
            "team_handoff_score",
            dict(valid_metrics("stage7")["team_handoff_score"], extra=1.0),
        )
        add("acceptance above one", "stage7", "acceptance_readiness", 1.1)

        for name, stage_id, metrics in cases:
            with self.subTest(name=name, stage_id=stage_id):
                prerequisites = (
                    {"target_profile": valid_target_profile()}
                    if stage_id == "stage5"
                    else None
                )
                with self.assertRaisesRegex(
                    policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
                ):
                    policy.parse_stage_output(
                        {
                            "finding": [],
                            "correction_proposal": [],
                            "metrics": metrics,
                        },
                        stage_id,
                        prerequisites=prerequisites,
                    )

    def test_huge_metric_integer_fails_closed_without_overflow(self):
        metrics = valid_metrics("stage3")
        metrics["avg_info_layers"] = 10**1000
        payload = {"finding": [], "correction_proposal": [], "metrics": metrics}
        try:
            policy.parse_stage_output(payload, "stage3")
        except policy.WorkflowBlocked as exc:
            self.assertRegex(str(exc), "BLOCKED: INVALID_STAGE_OUTPUT")
        except OverflowError as exc:
            self.fail("huge metric integer escaped the policy boundary: {}".format(exc))
        else:
            self.fail("out-of-range huge metric integer was accepted")

    def test_huge_invalid_target_profile_integer_is_contract_error(self):
        profile = valid_target_profile(clip_duration_seconds=-(10**1000))
        try:
            policy.parse_stage_output(
                stage5_payload(False),
                "stage5",
                prerequisites={"target_profile": profile},
            )
        except policy.WorkflowBlocked as exc:
            self.assertRegex(str(exc), "BLOCKED: CONTRACT_ERROR")
        except OverflowError as exc:
            self.fail(
                "huge target-profile integer escaped the policy boundary: {}".format(
                    exc
                )
            )
        else:
            self.fail("invalid huge target-profile integer was accepted")

    def test_stage5_parser_derives_declaration_from_prerequisites(self):
        for profile, declared in ((None, False), (valid_target_profile(), True)):
            with self.subTest(profile=profile):
                payload = stage5_payload(declared)
                try:
                    parsed = policy.parse_stage_output(
                        payload, "stage5", prerequisites={"target_profile": profile}
                    )
                except Exception as exc:
                    self.fail("canonical Stage 5 prerequisite must parse: {}".format(exc))
                self.assertEqual(declared, parsed["metrics"]["target_profile_declared"])

    def test_stage5_parser_requires_target_profile_prerequisite(self):
        for prerequisites in (None, {}):
            with self.subTest(prerequisites=prerequisites):
                try:
                    policy.parse_stage_output(
                        stage5_payload(False), "stage5", prerequisites=prerequisites
                    )
                except policy.WorkflowBlocked as exc:
                    self.assertRegex(str(exc), "BLOCKED: CONTRACT_ERROR")
                except Exception as exc:
                    self.fail("missing prerequisite must fail closed: {}".format(exc))
                else:
                    self.fail("missing target_profile prerequisite was accepted")

    def test_stage5_parser_rejects_reviewer_declaration_mismatch(self):
        mismatches = (
            (None, True),
            (valid_target_profile(), False),
        )
        for profile, declared in mismatches:
            with self.subTest(profile=profile, declared=declared):
                try:
                    policy.parse_stage_output(
                        stage5_payload(declared),
                        "stage5",
                        prerequisites={"target_profile": profile},
                    )
                except policy.WorkflowBlocked as exc:
                    self.assertRegex(str(exc), "BLOCKED: INVALID_STAGE_OUTPUT")
                except Exception as exc:
                    self.fail("declaration mismatch must fail closed: {}".format(exc))
                else:
                    self.fail("reviewer declaration mismatch was accepted")

    def test_stage5_parser_rejects_invalid_non_null_profile_as_contract_error(self):
        try:
            policy.parse_stage_output(
                stage5_payload(False),
                "stage5",
                prerequisites={"target_profile": valid_target_profile(mode="invalid")},
            )
        except policy.WorkflowBlocked as exc:
            self.assertRegex(str(exc), "BLOCKED: CONTRACT_ERROR")
        except Exception as exc:
            self.fail("invalid target profile must fail closed: {}".format(exc))
        else:
            self.fail("invalid non-null target profile was accepted")

    def test_inferred_continuity_states_require_writer_decision(self):
        for state in ("blood", "displacement", "occlusion", "orientation"):
            with self.subTest(state=state):
                self.assertTrue(policy.continuity_state_requires_writer_decision(state))
        self.assertFalse(
            policy.continuity_state_requires_writer_decision("confirmed_broken")
        )

    def test_source_fragment_hash_preserves_selected_blank_records(self):
        script = "alpha\r\nbeta\r\ngamma\r\n"
        self.assertEqual("beta\ngamma", policy.source_fragment(script, 2, 3))
        self.assertEqual(
            sha256("beta\ngamma".encode("utf-8")).hexdigest(),
            policy.source_fragment_sha256(script, 2, 3),
        )
        trailing_blank = "alpha\r\n\r\n"
        short_fragment = policy.source_fragment(trailing_blank, 1, 1)
        long_fragment = policy.source_fragment(trailing_blank, 1, 2)
        self.assertEqual("alpha", short_fragment)
        self.assertEqual("alpha\n", long_fragment)
        self.assertNotEqual(
            policy.source_fragment_sha256(trailing_blank, 1, 1),
            policy.source_fragment_sha256(trailing_blank, 1, 2),
        )

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

    def test_stage_output_parser_preserves_established_positional_api_only(self):
        payload = {
            "finding": [],
            "correction_proposal": [],
            "metrics": {
                "team_handoff_score": 0.9,
                "acceptance_readiness": 0.9,
                "stage7_pass_rate": 0.9,
            },
        }
        try:
            parsed = policy.parse_stage_output(payload, "stage7")
        except Exception as exc:
            self.fail("established (payload, stage_id) API must parse: {}".format(exc))
        self.assertEqual(payload, parsed)
        with self.assertRaisesRegex(
            policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
        ):
            policy.parse_stage_output("stage7", payload)

    def test_stage_output_parser_validates_all_three_components(self):
        payload = {
            "finding": [finding()],
            "correction_proposal": [
                proposal(
                    proposal_id="P-stage7-R7.34-S01-SH001-001",
                    finding_id="F-stage7-R7.34-S01-SH001-001",
                    expected_hash="0" * 64,
                    states={},
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

        false_flagged_blood = deepcopy(payload)
        false_flagged_blood["correction_proposal"][0]["asset_state_changes"] = {
            "prop": {"category": "blood", "value": "blood_stained"}
        }
        false_flagged_blood["correction_proposal"][0][
            "requires_writer_decision"
        ] = False
        with self.assertRaisesRegex(
            policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
        ):
            policy.parse_stage_output(false_flagged_blood, "stage7")

    def test_unknown_and_cross_stage_rule_ids_block_proposal_application(self):
        script = "ORIGINAL"
        source_hash = policy.source_fragment_sha256(script, 1, 1)
        for rule_id in ("R999", "R7.34"):
            with self.subTest(rule_id=rule_id):
                finding_id = "F-stage1-{}-S01-SH001-001".format(rule_id)
                unsafe_finding = finding(
                    finding_id=finding_id,
                    stage_id="stage1",
                    rule_id=rule_id,
                    source_text_sha256=source_hash,
                )
                unsafe_proposal = proposal(
                    proposal_id="P-stage1-{}-S01-SH001-001".format(rule_id),
                    finding_id=finding_id,
                    expected_hash=source_hash,
                    replacement="INJECTED",
                    states={},
                )
                payload = {
                    "finding": [unsafe_finding],
                    "correction_proposal": [unsafe_proposal],
                    "metrics": valid_metrics("stage1"),
                }
                try:
                    parsed = policy.parse_stage_output(payload, "stage1")
                except policy.WorkflowBlocked as exc:
                    self.assertRegex(str(exc), "BLOCKED: INVALID_STAGE_OUTPUT")
                else:
                    applied = policy.apply_correction_proposals(
                        script, parsed["correction_proposal"]
                    )
                    self.fail(
                        "{} was accepted and changed the script to {!r}".format(
                            rule_id, applied
                        )
                    )
        self.assertEqual("ORIGINAL", script)

    def test_proposal_writer_flag_must_cover_all_linked_findings(self):
        writer_finding = finding(writer_decision_needed=True)
        linked_proposal = proposal(
            proposal_id="P-stage7-R7.34-S01-SH001-001",
            finding_id="F-stage7-R7.34-S01-SH001-001",
            writer_decision=False,
            states={},
        )
        payload = {
            "finding": [writer_finding],
            "correction_proposal": [linked_proposal],
            "metrics": valid_metrics("stage7"),
        }
        with self.assertRaisesRegex(
            policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
        ):
            policy.parse_stage_output(payload, "stage7")

        payload["correction_proposal"][0]["requires_writer_decision"] = True
        self.assertEqual(payload, policy.parse_stage_output(payload, "stage7"))

    def test_proposal_target_must_match_linked_finding_evidence(self):
        base_payload = {
            "finding": [finding()],
            "correction_proposal": [
                proposal(
                    proposal_id="P-stage7-R7.34-S01-SH001-001",
                    finding_id="F-stage7-R7.34-S01-SH001-001",
                    states={},
                )
            ],
            "metrics": valid_metrics("stage7"),
        }
        mutations = (
            ("location", lambda item: item.__setitem__("location_id", "S99")),
            (
                "span",
                lambda item: item.__setitem__(
                    "source_span", {"start_line": 2, "end_line": 2}
                ),
            ),
            (
                "hash",
                lambda item: item.__setitem__("expected_source_sha256", "1" * 64),
            ),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                payload = deepcopy(base_payload)
                mutate(payload["correction_proposal"][0])
                with self.assertRaisesRegex(
                    policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
                ):
                    policy.parse_stage_output(payload, "stage7")

    def test_multi_finding_proposal_requires_one_coherent_target(self):
        first = finding()
        second = finding(
            finding_id="F-stage7-R7.35-S01-SH002-002",
            location_id="S01-SH002",
            source_span={"start_line": 2, "end_line": 2},
            source_text_sha256="1" * 64,
            rule_id="R7.35",
        )
        combined = proposal(
            proposal_id="P-stage7-R7.34-S01-SH001-001",
            finding_id="F-stage7-R7.34-S01-SH001-001",
            states={},
        )
        combined["finding_ids"] = [first["finding_id"], second["finding_id"]]
        payload = {
            "finding": [first, second],
            "correction_proposal": [combined],
            "metrics": valid_metrics("stage7"),
        }
        with self.assertRaisesRegex(
            policy.WorkflowBlocked, "BLOCKED: INVALID_STAGE_OUTPUT"
        ):
            policy.parse_stage_output(payload, "stage7")

    def test_parse_then_apply_preserves_snapshot_error_precedence(self):
        script = "original"
        stale_payload = {
            "finding": [finding(source_text_sha256="f" * 64)],
            "correction_proposal": [
                proposal(
                    proposal_id="P-stage7-R7.34-S01-SH001-001",
                    finding_id="F-stage7-R7.34-S01-SH001-001",
                    expected_hash="f" * 64,
                    states={
                        "prop": {"category": "blood", "value": "blood_stained"}
                    },
                    writer_decision=True,
                )
            ],
            "metrics": {
                "team_handoff_score": 0.9,
                "acceptance_readiness": 0.9,
                "stage7_pass_rate": 0.9,
            },
        }
        parsed_stale = policy.parse_stage_output(stale_payload, "stage7")
        with self.assertRaisesRegex(policy.WorkflowBlocked, "BLOCKED: STALE_PATCH"):
            policy.apply_correction_proposals(
                script, parsed_stale["correction_proposal"]
            )

        valid_payload = deepcopy(stale_payload)
        valid_payload["correction_proposal"][0][
            "expected_source_sha256"
        ] = policy.source_fragment_sha256(script, 1, 1)
        valid_payload["finding"][0][
            "source_text_sha256"
        ] = policy.source_fragment_sha256(script, 1, 1)
        parsed_valid = policy.parse_stage_output(valid_payload, "stage7")
        with self.assertRaisesRegex(
            policy.WorkflowBlocked, "BLOCKED: WRITER_DECISION_REQUIRED"
        ):
            policy.apply_correction_proposals(
                script, parsed_valid["correction_proposal"]
            )
        self.assertEqual("original", script)

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
        self.assertIn('category: "condition"', example)
        self.assertIn('value: "broken"', example)

        handoff = (ROOT / "references/handoff-protocol.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("asset_state_changes", handoff)
        self.assertIn("category", handoff)
        self.assertIn("value", handoff)
        self.assertIn("finding evidence", handoff)

    def test_security_policy_permits_only_the_three_output_components(self):
        security = (ROOT / "references/security-model.md").read_text(encoding="utf-8")
        self.assertIn("finding、correction_proposal 和 metrics", security)
        self.assertIn("BLOCKED: INVALID_STAGE_OUTPUT", security)


if __name__ == "__main__":
    unittest.main()
