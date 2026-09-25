"""Independent workflow invariants for integration-research receipts."""
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/pcb-design/scripts"))
import integration_candidate as candidate


class WorkflowReceiptIndependentTest(unittest.TestCase):
    def test_unevaluated_partial_findings_are_retained(self):
        report = candidate.diagnostic_causes({
            "candidate_p1": {
                "status": "UNEVALUATED", "reason": "candidate binding unavailable",
                "errors": ["partial native result"],
                "diagnostics": [{"detail": "interrupted checker"}],
            }
        })
        self.assertEqual(report["supported_causes"], [{
            "check": "candidate_p1", "cause": "UNEVALUATED",
            "basis": "candidate binding unavailable",
        }])
        self.assertEqual(report["unclassified_findings"], [
            {"check": "candidate_p1", "finding": "partial native result"},
            {"check": "candidate_p1", "finding": {"detail": "interrupted checker"}},
        ])
        self.assertFalse(report["engineering_acceptance"])

    def test_mixed_causes_keep_unknowns_and_incomplete_proof_debt(self):
        contract = {"allocations": [{"id": "escape", "coverage_nets": ["RESET"],
                                      "boundary_witnesses": [], "reservations": []}]}
        raw = {"status": "FAIL", "errors": [
            "escape: missing per-net boundary witness", "unclassified clearance"],
            "diagnostics": [], "allocations": [{
                "id": "escape", "reason": "escape: missing per-net boundary witness"}]}
        grouped = candidate.summarize_p1_findings(raw, contract)
        report = candidate.diagnostic_causes({
            "baseline_p1": {**raw, "finding_groups": grouped},
            "candidate_p1": {"status": "INCOMPLETE", "errors": [], "diagnostics": [],
                             "finding_groups": {"primary_missing_per_net_witnesses": [],
                                                "other_findings": [],
                                                "consequent_branch_errors": []}},
        })
        self.assertIn({"check": "baseline_p1", "cause": "MISSING_EVIDENCE",
                       "basis": "checker finding and contract coverage agree",
                       "allocation": "escape", "net": "RESET"}, report["supported_causes"])
        self.assertTrue(any(row["check"] == "candidate_p1" and
                            row["cause"] == "MISSING_EVIDENCE"
                            for row in report["supported_causes"]))
        self.assertIn({"check": "baseline_p1", "finding": "unclassified clearance"},
                      report["unclassified_findings"])
        self.assertEqual(report["design_violation_review"], "REQUIRES_INDEPENDENT_EVIDENCE")
        self.assertEqual(report["checker_limit_review"], "REQUIRES_INDEPENDENT_EVIDENCE")

    def test_same_board_research_handoff_has_no_physical_progress_or_promotion(self):
        board = {"path": "06_build/research/example/candidate.kicad_pcb", "sha256": "a" * 64}
        handoff = candidate.consumer_handoff({
            "candidate_board": board, "research_status": "INCOMPLETE",
            "diagnostics": {"candidate_p1": {"status": "INCOMPLETE"}},
            "decision_progress": {"decision": "ASSESS_PENDING"},
            "decision_id": "reset-service", "reservation_id": "reservation-1",
            "next_acceptance_consumer": "existing independent P1 review",
        })
        self.assertEqual(handoff["status"], "RESEARCH_ONLY")
        self.assertEqual(handoff["candidate"], board)
        self.assertEqual(handoff["current_decision"], "ASSESS_PENDING")
        self.assertEqual(handoff["board_progress"], "NOT_ESTABLISHED_BY_THIS_DIAGNOSTIC")
        self.assertFalse(handoff["engineering_acceptance"])
        self.assertTrue(handoff["independent_authority_required"])
        self.assertIn("P1/P2/P3", handoff["required_review"])


if __name__ == "__main__":
    unittest.main()
