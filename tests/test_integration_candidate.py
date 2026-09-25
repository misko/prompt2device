"""Executable no-credit integration research and fail-closed admission tests."""
import hashlib
import json
import sys
import tempfile
import io
from contextlib import contextmanager, redirect_stdout
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/pcb-design/scripts"))
import integration_candidate as candidate
from decision_progress import evaluate as decision_evaluate


@contextmanager
def raises(exc_type, match):
    try:
        yield
    except exc_type as exc:
        assert match in str(exc), str(exc)
    else:
        raise AssertionError(f"expected {exc_type.__name__}: {match}")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(tmp_path):
    root = tmp_path
    (root / "01_docs").mkdir()
    (root / "06_build").mkdir()
    (root / "03_src").mkdir()
    (root / "01_docs/requirement.md").write_text("G1 research\n")
    files = {}
    for role in sorted(candidate.REQUIRED):
        suffix = (".kicad_pro" if role == "pro" else ".kicad_dru" if role == "dru"
                  else ".json" if role in {"circuit", "modular_plan", "p1_contract", "interfaces"}
                  else ".py" if role.endswith("checker") or role == "producer" else ".txt")
        name = "rules" + suffix if role in {"pro", "dru"} else role + suffix
        path = root / name
        content = ("{}\n" if suffix == ".json" else "source\n")
        if role == "producer":
            content = ("from pathlib import Path\nimport sys,shutil,json,hashlib\n"
                       "Path(sys.argv[1]).mkdir(parents=True)\n"
                       "(Path(sys.argv[1])/'made.txt').write_text('ok')\n"
                       "shutil.copy2(sys.argv[2],Path(sys.argv[1])/'candidate.kicad_pcb')\n"
                       "rows={}\n"
                       "for role,path in [('board',Path(sys.argv[1])/'candidate.kicad_pcb'),"
                       "('p1_source',Path(sys.argv[3])),('p1_contract',Path(sys.argv[4]))]:\n"
                       " rows[role]={'path':path.relative_to(Path.cwd()).as_posix(),"
                       "'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}\n"
                       "(Path(sys.argv[1])/'candidate_inputs.json').write_text(json.dumps(rows))\n")
        if role == "modular_checker":
            content = "def evaluate(*args): return {'status':'FAIL','coverage':{},'findings':['open']}\n"
        if role == "p1_checker":
            content = "def evaluate(*args,**kwargs): return {'status':'INCOMPLETE','errors':['open']}\n"
        path.write_text(content)
        files[role] = {"path": name, "sha256": sha(path)}
    contract = {"schema": 2, "board_sha256": files["board"]["sha256"],
                "source_sha256": files["p1_source"]["sha256"],
                "interfaces_sha256": files["interfaces"]["sha256"],
                "floorplan_sha256": files["floorplan"]["sha256"],
                "aliases_sha256": files["aliases"]["sha256"]}
    (root / files["p1_contract"]["path"]).write_text(json.dumps(contract))
    files["p1_contract"]["sha256"] = sha(root / files["p1_contract"]["path"])
    (root / "03_src/route.yaml").write_text(yaml.safe_dump({
        "project": {"board": files["board"]["path"]},
        "flow": {"decision_admission": {"mode": "legacy_unmigrated"}}}))
    files["route_config"] = {"path": "03_src/route.yaml", "sha256": sha(root / "03_src/route.yaml")}
    requirement = root / "01_docs/requirement.md"
    finding = {"id": "coupled_choice", "state": "open", "owner": "pcb",
               "closes_when": "Independent engineering review", "blocks_at_or_above": "DESIGN_CLEAN",
               "investigation": {"schema": 1,
                   "requirement": {"path": "01_docs/requirement.md", "sha256": sha(requirement), "locator": "G1"},
                   "due_stage": "KICAD-SCHEMATIC", "operating_states": ["prototype"],
                   "question": "Which coupled placement?", "milestones": {"a": "A eliminated", "b": "B selected"},
                   "max_nonimproving_attempts": 2, "max_attempts": 2,
                   "launches": [], "history": [],
                   "next": {"action": "investigate", "hypothesis": "A is routable",
                            "on_support": "Review A", "on_reject": "Reject A",
                            "uncertainty": "bounded"}}}
    (root / "01_docs/findings.yaml").write_text(yaml.safe_dump({"schema": 1, "findings": [finding]}))
    output = "06_build/research/trial1"
    spec = {"schema": 1, "decision_id": "coupled_choice", "experiment_id": "trial1",
            "files": files, "command": [sys.executable, str(root / "producer.py"), str(root / output),
                                         str(root / files["board"]["path"]),
                                         str(root / files["p1_source"]["path"]),
                                         str(root / files["p1_contract"]["path"])],
            "timeout_s": 10, "output_root": output,
            "next_acceptance_consumer": "independent P1 review and native P2/P3 gates"}
    return root, spec


def test_bounded_trial_collects_separate_diagnostics_without_acceptance(tmp_path):
    root, spec = fixture(tmp_path)
    store = root / "06_build/integration_candidates"
    store.mkdir()
    pointer = store / "accepted.json"
    pointer.write_text('{"id":"previous"}\n')
    receipt = candidate.run(root, spec)
    assert receipt["attempt_status"] == "PASS"
    assert receipt["diagnostics"]["modular"]["status"] == "FAIL"
    assert receipt["diagnostics"]["candidate_p1"]["status"] == "INCOMPLETE"
    assert receipt["engineering_acceptance"] is False
    assert receipt["p1_accepted"] is False
    assert receipt["candidate_board"]["sha256"] == spec["files"]["board"]["sha256"]
    assert (root / spec["output_root"] / "made.txt").read_text() == "ok"
    assert json.loads((store / "experiments/trial1.json").read_text())["outcome"] == "INCOMPLETE"
    assert pointer.read_text() == '{"id":"previous"}\n'
    progress = decision_evaluate(root, "coupled_choice")
    assert progress["decision"] == "ASSESS_PENDING"
    assert len(progress["investigations"][0]["pending_launches"]) == 1
    with raises(ValueError, "assessment or reassessment"):
        candidate.preflight(root, {**spec, "experiment_id": "trial2", "output_root": "06_build/research/trial2"})


MUTATIONS = [
    (lambda r,s: (r / s["files"]["board"]["path"]).write_text("changed"), "board: missing, empty or stale"),
    (lambda r,s: s["files"].pop("dru"), "files require"),
    (lambda r,s: s["files"]["p1_contract"].update(sha256="0" * 64), "p1_contract: missing, empty or stale"),
    (lambda r,s: s["command"].__setitem__(1, "other.py"), "pinned producer"),
    (lambda r,s: s.update(output_root="01_docs/trial"), "below 06_build"),
]
def test_bad_packet_never_mutates_budget_or_attempt(tmp_path):
    for index, (mutation, match) in enumerate(MUTATIONS):
        root = tmp_path / str(index)
        root.mkdir()
        root, spec = fixture(root)
        ledger = root / "01_docs/findings.yaml"
        before = ledger.read_bytes()
        mutation(root, spec)
        with raises(ValueError, match):
            candidate.run(root, spec)
        assert ledger.read_bytes() == before
        assert not (root / "06_build/task_runs").exists()
        assert not (root / spec["output_root"]).exists()


def test_cross_board_contract_refused_before_budget(tmp_path):
    root, spec = fixture(tmp_path)
    board = root / spec["files"]["board"]["path"]
    board.write_text("different valid board\n")
    spec["files"]["board"]["sha256"] = sha(board)
    before = (root / "01_docs/findings.yaml").read_bytes()
    with raises(ValueError, "contract board_sha256"):
        candidate.run(root, spec)
    assert (root / "01_docs/findings.yaml").read_bytes() == before


def test_failed_producer_retains_prior_pointer_and_counts_same_decision(tmp_path):
    root, spec = fixture(tmp_path)
    producer = root / "producer.py"
    producer.write_text("raise SystemExit(7)\n")
    spec["files"]["producer"]["sha256"] = sha(producer)
    store = root / "06_build/integration_candidates"
    store.mkdir()
    (store / "accepted.json").write_text('{"id":"previous"}\n')
    receipt = candidate.run(root, spec)
    assert receipt["attempt_status"] == "FAIL"
    assert json.loads((store / "experiments/trial1.json").read_text())["outcome"] == "REJECTED"
    assert (store / "accepted.json").read_text() == '{"id":"previous"}\n'
    assert decision_evaluate(root, "coupled_choice")["investigations"][0]["attempts"] == 1


def test_changed_board_is_recorded_but_old_p1_contract_cannot_grade_it(tmp_path):
    root, spec = fixture(tmp_path)
    producer = root / "producer.py"
    producer.write_text(producer.read_text().replace(
        "rows={}\n", "with (Path(sys.argv[1])/'candidate.kicad_pcb').open('a') as f: f.write('changed board')\nrows={}\n"))
    spec["files"]["producer"]["sha256"] = sha(producer)
    receipt = candidate.run(root, spec)
    assert receipt["attempt_status"] == "PASS"
    assert receipt["candidate_board"]["sha256"] != spec["files"]["board"]["sha256"]
    assert receipt["candidate_inputs"]["board"]["sha256"] == receipt["candidate_board"]["sha256"]
    assert receipt["diagnostics"]["baseline_p1"]["status"] == "INCOMPLETE"
    assert receipt["diagnostics"]["candidate_p1"]["status"] == "UNEVALUATED"
    assert "stale for produced board" in receipt["diagnostics"]["candidate_p1"]["reason"]


def test_changed_board_with_separately_pinned_replay_runs_p1_diagnostic(tmp_path):
    root, spec = fixture(tmp_path)
    producer = root / "producer.py"
    content = producer.read_text()
    content = content.replace("rows={}\n", (
        "with (Path(sys.argv[1])/'candidate.kicad_pcb').open('a') as f: f.write('changed board')\n"
        "contract=json.loads(Path(sys.argv[4]).read_text())\n"
        "contract['board_sha256']=hashlib.sha256((Path(sys.argv[1])/'candidate.kicad_pcb').read_bytes()).hexdigest()\n"
        "(Path(sys.argv[1])/'candidate_contract.json').write_text(json.dumps(contract))\n"
        "rows={}\n"))
    content = content.replace("('p1_contract',Path(sys.argv[4]))",
                              "('p1_contract',Path(sys.argv[1])/'candidate_contract.json')")
    producer.write_text(content)
    spec["files"]["producer"]["sha256"] = sha(producer)
    board_hash = hashlib.sha256((root / "board.txt").read_bytes() + b"changed board").hexdigest()
    contract = json.loads((root / "p1_contract.json").read_text())
    contract["board_sha256"] = board_hash
    contract_hash = hashlib.sha256(json.dumps(contract).encode()).hexdigest()
    spec["expected_candidate"] = {"board": board_hash,
                                  "p1_source": spec["files"]["p1_source"]["sha256"],
                                  "p1_contract": contract_hash}
    receipt = candidate.run(root, spec)
    assert receipt["candidate_board"]["sha256"] == board_hash
    assert receipt["candidate_inputs"]["p1_contract"]["sha256"] == contract_hash
    assert receipt["diagnostics"]["candidate_p1"]["status"] == "INCOMPLETE"
    assert receipt["diagnostics"]["candidate_p1"]["replay_hashes_pinned"] is True
    assert receipt["engineering_acceptance"] is False


def test_foreign_write_detected_and_timeout_never_promotes(tmp_path):
    for index, content in enumerate((
        "from pathlib import Path\nPath('01_docs/foreign.txt').write_text('bad')\n",
        "import time\ntime.sleep(2)\n",
        "from pathlib import Path\nPath('rules.kicad_dru').write_text('tampered')\n")):
        root = tmp_path / str(index)
        root.mkdir()
        root, spec = fixture(root)
        producer = root / "producer.py"
        producer.write_text(content)
        spec["files"]["producer"]["sha256"] = sha(producer)
        if index:
            spec["timeout_s"] = 0.1
        store = root / "06_build/integration_candidates"
        store.mkdir()
        (store / "accepted.json").write_text('{"id":"previous"}\n')
        receipt = candidate.run(root, spec)
        assert receipt["attempt_status"] in ("ERROR", "TIMED_OUT")
        if index == 2:
            attempt = json.loads((root / receipt["attempt_path"]).read_text())
            assert attempt["output"]["input_packet"]["after"]["status"] == "FAIL"
        assert json.loads((store / "experiments/trial1.json").read_text())["outcome"] == "REJECTED"
        assert (store / "accepted.json").read_text() == '{"id":"previous"}\n'
        assert decision_evaluate(root, "coupled_choice")["investigations"][0]["attempts"] == 1


def test_crow_d0_packet_and_e07_mismatch_are_read_only():
    """Current real inputs bind, but its existing investigation is not launchable."""
    project = ROOT / "projects/crow-usb-carrier-v1"
    base = "01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol/"
    role_paths = {
        "board": "01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb",
        "netlist": "01_docs/research/2026-09-25-ti-prototype-schematic-adoption/native_netlist.net",
        "circuit": "03_tscircuit/build/circuit.json",
        "floorplan": base + "floorplan.yaml", "p1_source": base + "p1_requirements.yaml",
        "p1_contract": base + "coarse.json", "interfaces": base + "modular_plan.json",
        "aliases": "02_parts/USB4215-03-A/part.yaml", "modular_plan": "03_src/modular_plan.json",
        "pro": "06_build/modular/repaired-trial/crow_carrier.kicad_pro",
        "dru": "06_build/modular/repaired-trial/crow_carrier.kicad_dru",
        "route_config": "03_src/route.yaml",
        "producer": "repo:skills/kicad-pcb/scripts/p1_corridor_capacity.py",
        "p1_checker": "repo:skills/kicad-pcb/scripts/p1_corridor_capacity.py",
        "modular_checker": "repo:skills/pcb-design/scripts/modular_design.py",
    }
    files = {}
    for role, relative in role_paths.items():
        path = ROOT / relative.removeprefix("repo:") if relative.startswith("repo:") else project / relative
        files[role] = {"path": relative, "sha256": sha(path)}
    spec = {"schema": 1, "decision_id": "USB-XTAL-native-realization",
            "experiment_id": "crow-d0-read-only-example", "files": files,
            "command": [sys.executable, str(ROOT / "skills/kicad-pcb/scripts/p1_corridor_capacity.py")],
            "timeout_s": 10, "output_root": "06_build/research/crow-d0-read-only-example",
            "next_acceptance_consumer": "independent P1 review after finding reassessment"}
    with raises(ValueError, "assessment or reassessment"):
        candidate.preflight(project, spec)
    e07 = project / "01_docs/research/2026-09-25-ti-cin3-qpre-owner-repair-sol/candidate.kicad_pcb"
    mixed = copy_spec(spec)
    mixed["files"]["board"] = {"path": e07.relative_to(project).as_posix(), "sha256": sha(e07)}
    with raises(ValueError, "contract board_sha256"):
        candidate.preflight(project, mixed)
    for role in ("p1_source", "dru"):
        stale = copy_spec(spec)
        stale["files"][role]["sha256"] = "0" * 64
        with raises(ValueError, f"{role}: missing, empty or stale"):
            candidate.preflight(project, stale)


def test_stale_runtime_repair_packet_does_not_reserve_budget(tmp_path):
    from datetime import datetime, timedelta, timezone
    from pipeline_execution import TaskEnvelope
    from pipeline_runtime import execute_attempt
    from pipeline_identity import subject_identity, TypedIdentityInput
    root, _ = fixture(tmp_path)
    before = (root / "01_docs/findings.yaml").read_bytes()
    subject = subject_identity("repair-packet-test", 1, [
        TypedIdentityInput("source", "scalar", "stale", b"stale")])
    envelope = TaskEnvelope(
        task_id="stale-repair", stage_id="P1", run_id="stale-repair", subject=subject,
        executor="subprocess", execution_class="local", recommended_agent_role=None,
        agent_role=None, role_escalation_reason=None, context_mode="NOT_APPLICABLE",
        input_handoff_id=None,
        input_packet=[{"name": "board", "path": "board.txt", "sha256": "0" * 64, "size": 7}],
        deadline_at=(datetime.now(timezone.utc) + timedelta(seconds=2)).isoformat().replace("+00:00", "Z"),
        max_nonimproving_attempts=2, replacement_limit=0,
        writer_scope={"mode": "EXCLUSIVE", "paths": ["06_build/scratch"]},
        output_path="06_build/task_runs/stale-repair/attempt.json", schema=2,
        completion={"outputs": ["result.txt"], "checks": ["source"]},
        repair={"owner_id": "owner", "hypothesis_sha256": "a" * 64,
                "max_attempts": 2, "setup_remedies": [], "finding_id": "coupled_choice"})
    attempt = execute_attempt(envelope, [sys.executable, "-c", "print('SHOULD_NOT_RUN')"],
                              cwd=root, env={}, console=None)
    assert attempt.status == "ERROR"
    assert attempt.output["runtime"] is None
    assert (root / "01_docs/findings.yaml").read_bytes() == before


def test_cli_exit_zero_child_without_manifest_is_rejected(tmp_path):
    root, spec = fixture(tmp_path)
    producer = root / "producer.py"
    producer.write_text("print('done without candidate')\n")
    spec["files"]["producer"]["sha256"] = sha(producer)
    spec_path = root / "research_spec.json"
    spec_path.write_text(json.dumps(spec))
    with redirect_stdout(io.StringIO()) as out:
        rc = candidate.main([str(root), str(spec_path)])
    assert rc == 1
    receipt = json.loads(out.getvalue()[out.getvalue().find('{'):])
    assert receipt["attempt_status"] == "PASS"
    assert receipt["research_status"] == "REJECTED"


def test_selection_and_pause_guards_refuse_before_reservation(tmp_path):
    for index, mode in enumerate(("selection", "pause")):
        root = tmp_path / str(index)
        root.mkdir()
        root, spec = fixture(root)
        if mode == "selection":
            (root / "03_src/rules").mkdir()
            (root / "03_src/rules/critical_part_selection.yaml").write_text(
                "schema: 1\nstatus: pending\nselections: []\n")
        else:
            (root / "01_docs/pause_state.json").write_text("{}\n")
        before = (root / "01_docs/findings.yaml").read_bytes()
        with raises(ValueError, "critical selection refuses" if mode == "selection" else "stale pause state"):
            candidate.run(root, spec)
        assert (root / "01_docs/findings.yaml").read_bytes() == before
        assert not (root / "06_build/task_runs").exists()


def copy_spec(spec):
    return json.loads(json.dumps(spec))


def test_native_witness_proposal_is_read_only_and_revokes_claims():
    project = ROOT / "projects/crow-usb-carrier-v1"
    board = project / "01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb"
    contract_path = project / "01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol/coarse.json"
    contract = json.loads(contract_path.read_text())
    original = copy_spec(contract)
    board_bytes, contract_bytes = board.read_bytes(), contract_path.read_bytes()
    witness = next(w for allocation in contract["allocations"]
                   for w in allocation.get("boundary_witnesses", [])
                   if w.get("kind") == "unresolved_multiterminal_branch")
    witness["boundary_bbox"] = [0, 0, 1, 1]
    contract["status"] = "PASS"
    contract["p1_accepted"] = True
    contract["routing_realized"] = True
    report = candidate.propose_native_witnesses(board, contract)
    assert report["geometry_changes"]
    assert report["proposed_contract"]["status"] == "INCOMPLETE"
    assert report["proposed_contract"]["p1_accepted"] is False
    assert report["proposed_contract"]["routing_realized"] is False
    assert report["invalidated_reviews"] == ["placement", "geometry", "P1", "routing", "release"]
    assert report["independent_review_required"] is True
    assert witness["boundary_bbox"] == [0, 0, 1, 1]
    assert board.read_bytes() == board_bytes and contract_path.read_bytes() == contract_bytes
    clean = candidate.propose_native_witnesses(board, report["proposed_contract"])
    assert clean["geometry_changes"] == []
    assert clean["board_binding_changed"] is False
    assert clean["invalidated_reviews"] == []
    assert original["p1_accepted"] is False
    output = io.StringIO()
    with redirect_stdout(output):
        assert candidate.main(["diagnose-native-witnesses", str(board), str(contract_path)]) == 0
    cli = json.loads(output.getvalue())
    assert cli["input_contract_sha256"] == sha(contract_path)
    assert cli["engineering_acceptance"] is False
    assert board.read_bytes() == board_bytes and contract_path.read_bytes() == contract_bytes


def test_native_witness_rejects_missing_duplicate_and_wrong_net(tmp_path):
    board = tmp_path / "board.kicad_pcb"
    board.write_text("native test board")
    class Box:
        def GetLeft(self): return 0
        def GetTop(self): return 0
        def GetRight(self): return 1
        def GetBottom(self): return 1
    class Pad:
        def __init__(self, net="N"): self.net = net
        def GetNumber(self): return "1"
        def GetNetname(self): return self.net
        def IsOnLayer(self, _): return True
        def GetBoundingBox(self): return Box()
    class Footprint:
        def __init__(self, pads): self.pads = pads
        def GetReference(self): return "U1"
        def Pads(self): return self.pads
    class Board:
        def __init__(self, pads): self.pads = pads
        def GetFootprints(self): return [Footprint(self.pads)]
        def GetLayerID(self, _): return 0
    class FakePcbnew:
        pads = []
        @classmethod
        def LoadBoard(cls, _): return Board(cls.pads)
        @staticmethod
        def IsCopperLayer(_): return True
        @staticmethod
        def ToMM(value): return value
    prior_pcbnew = sys.modules.get("pcbnew")
    sys.modules["pcbnew"] = FakePcbnew
    contract = {"allocations": [{"id": "a", "boundary_witnesses": [{
        "kind": "unresolved_multiterminal_branch", "native": "U1.1", "net": "N",
        "layer": "F.Cu", "boundary_bbox": [0, 0, 1, 1]}]}]}
    try:
        for pads, fragment in (([], "found 0"), ([Pad(), Pad()], "found 2"),
                               ([Pad("WRONG")], "pad/net mismatch")):
            FakePcbnew.pads = pads
            with raises(ValueError, fragment):
                candidate.propose_native_witnesses(board, contract)
    finally:
        if prior_pcbnew is None:
            sys.modules.pop("pcbnew", None)
        else:
            sys.modules["pcbnew"] = prior_pcbnew


def test_findings_group_primary_and_consequent_without_dropping_unknown():
    contract = {"allocations": [{"id": "a", "coverage_nets": ["N", "M"],
                                 "boundary_witnesses": [{"net": "M"}],
                                 "reservations": [{"kind": "unresolved_multiterminal_branch",
                                                   "branch_id": "tree-n", "nets": ["N"]}]}]}
    result = {"errors": ["tree-n: unresolved branch representative witness denominator mismatch",
                         "unknown: independent finding",
                         "other-tree: unresolved branch representative witness denominator mismatch"],
              "allocations": [{"id": "a", "status": "FAIL",
                               "reason": "a: missing per-net boundary witness"}],
              "diagnostics": [{"reason": "stale native pad"}]}
    grouped = candidate.summarize_p1_findings(result, contract)
    assert grouped["primary_missing_per_net_witnesses"] == [
        {"allocation": "a", "net": "N", "reason": "missing per-net boundary witness"}]
    assert grouped["consequent_branch_errors"] == [result["errors"][0]]
    assert result["errors"][1:] == grouped["other_findings"][:2]
    assert grouped["raw_errors"] == result["errors"]
    assert grouped["raw_allocations"] == result["allocations"]
    bad = candidate._safe_finding_groups({"errors": "malformed", "status": "FAIL"}, contract)
    assert bad["status"] == "UNEVALUATED"


if __name__ == "__main__":
    tests = [test_bounded_trial_collects_separate_diagnostics_without_acceptance,
             test_bad_packet_never_mutates_budget_or_attempt,
             test_cross_board_contract_refused_before_budget,
             test_failed_producer_retains_prior_pointer_and_counts_same_decision,
             test_changed_board_is_recorded_but_old_p1_contract_cannot_grade_it,
             test_changed_board_with_separately_pinned_replay_runs_p1_diagnostic,
             test_foreign_write_detected_and_timeout_never_promotes,
             test_stale_runtime_repair_packet_does_not_reserve_budget,
             test_cli_exit_zero_child_without_manifest_is_rejected,
             test_selection_and_pause_guards_refuse_before_reservation]
    with tempfile.TemporaryDirectory(prefix="integration-candidate-tests-") as directory:
        for index, test in enumerate(tests):
            path = Path(directory) / str(index)
            path.mkdir()
            test(path)
            print(f"PASS {test.__name__}")
    test_crow_d0_packet_and_e07_mismatch_are_read_only()
    print("PASS test_crow_d0_packet_and_e07_mismatch_are_read_only")
    test_native_witness_proposal_is_read_only_and_revokes_claims()
    print("PASS test_native_witness_proposal_is_read_only_and_revokes_claims")
    with tempfile.TemporaryDirectory(prefix="native-witness-errors-") as directory:
        test_native_witness_rejects_missing_duplicate_and_wrong_net(Path(directory))
    print("PASS test_native_witness_rejects_missing_duplicate_and_wrong_net")
    test_findings_group_primary_and_consequent_without_dropping_unknown()
    print("PASS test_findings_group_primary_and_consequent_without_dropping_unknown")
