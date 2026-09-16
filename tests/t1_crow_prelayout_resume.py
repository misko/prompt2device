#!/usr/bin/env python3
"""T1: crow JLC prelayout pauses resume exact, fully pinned design bytes."""

from __future__ import annotations

import csv
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from harness import ROOT, check, main, run, test, tmpdir


sys.path.insert(0, str(ROOT / "skills/jlcpcb-fab/scripts"))
import jlc_pcba_availability as pcba  # noqa: E402


FULL_DRIVERS = (
    ROOT / "projects/crow-audio-carrier-v1/03_src/rebuild_all.sh",
    ROOT / "projects/crow-mic-pod-v3/03_src/rebuild_all.sh",
)
REUSE_DRIVERS = (
    ROOT / "projects/crow-audio-carrier-v1/03_src/rebuild_reuse.sh",
    ROOT / "projects/crow-mic-pod-v3/03_src/rebuild_reuse.sh",
)
INPUT_CHECKPOINT = (
    ROOT / "projects/crow-roof-array-v1/03_src/prelayout_input_checkpoint.py"
)
RESUME_GATE = ROOT / "projects/crow-roof-array-v1/03_src/prelayout_resume_gate.py"
_resume_spec = importlib.util.spec_from_file_location(
    "crow_prelayout_resume_gate", RESUME_GATE)
assert _resume_spec and _resume_spec.loader
resume_gate = importlib.util.module_from_spec(_resume_spec)
_resume_spec.loader.exec_module(resume_gate)
PORTABLE_PROJECTS = (
    (ROOT / "projects/crow-audio-carrier-v1", "crow_audio_carrier_v1"),
    (ROOT / "projects/crow-mic-pod-v3", "crow_mic_pod_v3"),
)


def contract_failures(text: str) -> list[str]:
    """Return structural failures in one project-local resume state machine."""
    failures: list[str] = []
    positions = {
        "lock": text.find("/usr/bin/flock -n 9"),
        "flag": text.find("--resume-after-prelayout"),
        "preflight": text.find("refusing to rerun nondeterministic TSX"),
        "resume_arm": text.find('if [ "$RESUME_AFTER_PRELAYOUT" = true ]'),
        "prelayout_gate": text.find('"$PRELAYOUT_RESUME_GATE" .'),
        "schematic_arm": text.find(
            'elif [ "$RESUME_AFTER_SCHEMATIC_REVIEW" = true ]'),
        "schematic_gate": text.find(
            '"$PRELAYOUT_RESUME_GATE" .',
            text.find('elif [ "$RESUME_AFTER_SCHEMATIC_REVIEW" = true ]')),
        "full_arm": text.find(
            'if [ "$RESUME_AFTER_PRELAYOUT" = false ] &&',
            text.find('elif [ "$RESUME_AFTER_SCHEMATIC_REVIEW" = true ]')),
        "producer": text.find("run_stage tscircuit_build"),
        "prepare": text.find('jlc_pcba_availability.py" prepare "$CJ"'),
        "input_record": text.find(
            '"$PRELAYOUT_CHECKPOINT_TOOL" record .'),
        "checkpoint_record": text.find('stage_checkpoint.py" record . prelayout'),
        "erc": text.find("kicad-cli sch erc --severity-all"),
        "schematic_else": text.find(
            "\nelse\n", text.find('stage_checkpoint.py" record . schematic')),
        "review": text.find(
            'pre_route_review_check.py" . --phase schematic'),
    }
    missing = [name for name, offset in positions.items() if offset < 0]
    if missing:
        failures.append(f"missing state-machine element(s): {missing}")
        return failures

    wanted_order = (
        "lock", "flag", "preflight", "resume_arm", "prelayout_gate",
        "schematic_arm", "schematic_gate", "full_arm", "producer",
        "prepare", "input_record", "checkpoint_record", "erc",
        "schematic_else", "review",
    )
    offsets = [positions[name] for name in wanted_order]
    if offsets != sorted(offsets):
        failures.append(f"unsafe stage order: {wanted_order}")
    if "PCB-REBUILD-LOCK" not in text[:positions["flag"]]:
        failures.append("project conductor lock is absent or late")

    preflight = text[positions["preflight"] - 1200:positions["preflight"] + 500]
    for token in ("$PCBA_REQUEST", "$PCBA_RESPONSE", "$PCBA_RECEIPT",
                  "$PCBA_CHECKPOINT", "$PCBA_INPUT_CHECKPOINT", "exit 2"):
        if token not in preflight:
            failures.append(f"preflight does not guard {token}")

    resume_identity = text[positions["resume_arm"]:positions["full_arm"]]
    if "tsci build" in resume_identity or "tscircuit_build" in resume_identity:
        failures.append("prelayout resume arm can invoke the TSX producer")
    if "--context resume-prelayout" not in resume_identity:
        failures.append("prelayout resume does not invoke shared gate")
    schematic_identity = text[
        positions["schematic_arm"]:positions["full_arm"]]
    if ("--context resume-schematic" not in schematic_identity or
            "--require-schematic" not in schematic_identity):
        failures.append("schematic resume does not invoke full shared gate")

    checkpoint_end = text.find("GATE INCOMPLETE [1c] J-PCBA-PRELAYOUT",
                               positions["checkpoint_record"])
    checkpoint = text[positions["checkpoint_record"]:checkpoint_end]
    if '--input "$PCBA_REQUEST"' not in checkpoint:
        failures.append("prelayout checkpoint omits the immutable request")
    if '--input "$PCBA_INPUT_CHECKPOINT"' not in checkpoint:
        failures.append("stage checkpoint does not pin the input census record")
    for mutable in ('--input "$PCBA_RESPONSE"', '--input "$PCBA_RECEIPT"'):
        if mutable in checkpoint:
            failures.append(f"prelayout checkpoint pins mutable evidence: {mutable}")

    instruction_window = text[
        positions["checkpoint_record"]:positions["erc"]]
    if "$0 --resume-after-prelayout" not in instruction_window:
        failures.append("initial pause does not print the safe continuation CLI")
    for token in ("--resume-after-public-prelayout",
                  "ALLOW_PUBLIC_CATALOG", "--allow-public-catalog"):
        if token not in text:
            failures.append(f"public-catalog continuation omits {token}")

    if 'if [ "$RESUME_AFTER_SCHEMATIC_REVIEW" = false ]; then' not in text:
        failures.append("prelayout and schematic resume branches are not distinct")
    return failures


def resume_gate_failures(text: str) -> list[str]:
    failures = []
    positions = {
        "provenance": text.find('"build_provenance.py", "audit"'),
        "prelayout": text.find('"stage_checkpoint.py", "verify", ".", "prelayout"'),
        "inputs": text.find('input_gate, "verify"'),
        "schematic": text.find('"stage_checkpoint.py", "verify", ".", "schematic"'),
        "request": text.find('"jlc_pcba_availability.py", "verify-request"'),
        "receipt": text.find('"jlc_pcba_availability.py", "verify", receipt'),
        "readiness": text.find('"manufacturing_readiness.py", "grade"'),
    }
    if any(offset < 0 for offset in positions.values()):
        failures.append(f"shared gate element missing: {positions}")
        return failures
    if not (positions["provenance"] < positions["prelayout"] <
            positions["inputs"] < positions["schematic"] <
            positions["request"] < positions["receipt"] <
            positions["readiness"]):
        failures.append("shared verification order is unsafe")
    receipt_window = text[positions["receipt"]:positions["readiness"]]
    if '"--bom", circuit' not in receipt_window or '"--phase", "prelayout"' not in receipt_window:
        failures.append("shared receipt verifier omits current circuit/phase")
    for name in ("circuit", "request", "response", "assembly",
                 "procurement"):
        if f'({name}, "' not in text:
            failures.append(f"shared gate does not require regular {name} evidence")
    if "regular(receipt," not in text:
        failures.append("shared gate does not require a regular receipt")
    for token in ("--allow-public-catalog", "blank_response_matches_request",
                  "--catalog-request", "--catalog-evidence",
                  "--catalog-decision"):
        if token not in text:
            failures.append(f"shared public-catalog gate omits {token}")
    for checkpoint in ("prelayout_record", "input_record", "schematic_record"):
        if checkpoint not in text:
            failures.append(f"shared gate does not identify {checkpoint}")
    return failures


def reuse_failures(text: str) -> list[str]:
    failures = []
    lock = text.find("/usr/bin/flock -n 9")
    gate = text.find('"$PRELAYOUT_RESUME_GATE" .')
    # Function definitions above the preflight contain commands but execute
    # nothing.  This mkdir is the first unconditional generated write in the
    # driver body after the gate.
    first_write = text.find('mkdir -p "$PIPELINE_EVIDENCE/bundles"',
                            max(gate, 0))
    if gate < 0 or gate > first_write:
        failures.append("reuse shared gate does not precede every generated write")
    if lock < 0 or lock > gate or "PCB-REBUILD-LOCK" not in text[:gate]:
        failures.append("reuse project conductor lock is absent or late")
    window = text[gate:first_write]
    for token in ("--require-schematic", "--pinned-schematic",
                  "--generated-schematic", "--context reuse-preflight"):
        if token not in window:
            failures.append(f"reuse preflight omits {token}")
    if "PRELAYOUT_AUTH_ARGS=(--allow-public-catalog)" not in text:
        failures.append("reuse cannot consume explicit public-catalog authority")
    if '-o "$NETLIST_CANDIDATE"' not in text or \
            'from pre_route_review_check import netlist_digest' not in text or \
            'netlist_digest(candidate) != netlist_digest(frozen)' not in text:
        failures.append(
            "reuse does not compare a temporary electrical netlist to frozen authority")
    if 'cmp -s -- "$NETLIST_CANDIDATE" "$NETLIST"' in text:
        failures.append(
            "reuse raw-compares KiCad path/date metadata instead of electrical content")
    if '-o "06_build/netlists/$BOARD.net"' in text or \
            'cp "$SCH" "04_kicad/$BOARD.kicad_sch"' in text:
        failures.append("reuse overwrites a frozen checkpoint artifact")
    return failures


@test("both crow drivers are shell-valid and implement exact prelayout resume")
def t_drivers_clean():
    for driver in FULL_DRIVERS:
        result = run(["bash", "-n", driver])
        check(result.rc == 0, f"{driver}: bash -n failed: {result.out}")
        failures = contract_failures(driver.read_text(encoding="utf-8"))
        check(not failures, f"{driver}: {failures}")
    for driver in REUSE_DRIVERS:
        result = run(["bash", "-n", driver])
        check(result.rc == 0, f"{driver}: bash -n failed: {result.out}")
        failures = reuse_failures(driver.read_text(encoding="utf-8"))
        check(not failures, f"{driver}: {failures}")
    failures = resume_gate_failures(RESUME_GATE.read_text(encoding="utf-8"))
    check(not failures, f"{RESUME_GATE}: {failures}")


@test("all crow conductors reject a concurrent project invocation",
      kind="known_bad")
def t_concurrent_driver_rejected():
    for driver in (*FULL_DRIVERS, *REUSE_DRIVERS):
        project = driver.parents[1]
        result = run([
            "/bin/bash", "-c",
            ('cd "$1"; exec 8<.; /usr/bin/flock -n 8; '
             '"$1/03_src/$2"'),
            "crow-lock-test", project, driver.name,
        ])
        check(result.rc == 2 and "PCB-REBUILD-LOCK" in result.out,
              f"{driver}: concurrent conductor was not rejected: {result.out}")


@test("prelayout resume rejects a driver without the pre-TSX evidence guard",
      kind="known_bad")
def t_guard_removed():
    text = FULL_DRIVERS[0].read_text(encoding="utf-8")
    mutated = text.replace("refusing to rerun nondeterministic TSX",
                           "normal rebuild allowed", 1)
    check(contract_failures(mutated), "missing pre-TSX guard was accepted")


@test("prelayout resume rejects a driver without checkpoint verification",
      kind="known_bad")
def t_checkpoint_verify_removed():
    text = RESUME_GATE.read_text(encoding="utf-8")
    mutated = text.replace(
        '"stage_checkpoint.py", "verify", ".", "prelayout"',
        '"stage_checkpoint.py", "omitted", ".", "prelayout"', 1)
    check(mutated != text, "fixture did not remove checkpoint verification")
    check(resume_gate_failures(mutated),
          "resume without checkpoint verify passed")


@test("prelayout checkpoint rejects mutable operator evidence",
      kind="known_bad")
def t_mutable_response_pinned():
    text = FULL_DRIVERS[0].read_text(encoding="utf-8")
    needle = '--input "$PCBA_REQUEST"'
    checkpoint = text.find('stage_checkpoint.py" record . prelayout')
    location = text.find(needle, checkpoint)
    check(checkpoint >= 0 and location >= 0,
          "fixture could not find stage checkpoint request input")
    mutated = (text[:location] + needle + '\n        --input "$PCBA_RESPONSE"' +
               text[location + len(needle):])
    check(mutated != text, "fixture did not add mutable checkpoint input")
    check(contract_failures(mutated), "mutable operator CSV was checkpointed")


@test("prelayout receipt wiring rejects omission of the exact circuit",
      kind="known_bad")
def t_receipt_bom_wiring_removed():
    text = RESUME_GATE.read_text(encoding="utf-8")
    receipt = text.find('"jlc_pcba_availability.py", "verify", receipt')
    readiness = text.find('"manufacturing_readiness.py", "grade"', receipt)
    bom = text.find('"--bom", circuit', receipt, readiness)
    check(receipt >= 0 and readiness > receipt and bom >= 0,
          "fixture could not locate receipt circuit binding")
    mutated = text[:bom] + '"--bom", request' + text[bom + len('"--bom", circuit'):]
    check(resume_gate_failures(mutated), "receipt without circuit binding passed")


@test("public-catalog continuation requires an untouched operator worksheet")
def t_public_catalog_blank_response():
    root = tmpdir("crow-public-blank-")
    request = root / "request.json"
    response = root / "response.csv"
    request.write_text(json.dumps({
        "rows": [{"requested_lcsc": "C100"},
                 {"requested_lcsc": "C200"}],
    }), encoding="utf-8")
    with response.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=pcba.RESPONSE_FIELDS)
        writer.writeheader()
        writer.writerow({"Requested LCSC": "C100"})
        writer.writerow({"Requested LCSC": "C200"})
    check(resume_gate.blank_response_matches_request(
        response, request, "PUBLIC-FIXTURE"),
        "blank exact worksheet was rejected")


@test("public-catalog continuation rejects operator-field contamination",
      kind="known_bad")
def t_public_catalog_populated_response():
    root = tmpdir("crow-public-populated-")
    request = root / "request.json"
    response = root / "response.csv"
    request.write_text(json.dumps({
        "rows": [{"requested_lcsc": "C100"}],
    }), encoding="utf-8")
    with response.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=pcba.RESPONSE_FIELDS)
        writer.writeheader()
        writer.writerow({"Requested LCSC": "C100",
                         "PCBA Status": "AVAILABLE"})
    check(not resume_gate.blank_response_matches_request(
        response, request, "PUBLIC-HOSTILE"),
        "public mode consumed fabricated operator evidence")


@test("schematic resume rejects omission of live prelayout authority",
      kind="known_bad")
def t_schematic_resume_authority_removed():
    text = FULL_DRIVERS[0].read_text(encoding="utf-8")
    needle = '--context resume-schematic --require-schematic'
    mutated = text.replace(needle, '--context resume-schematic', 1)
    check(mutated != text, "fixture did not remove schematic authority recheck")
    check(contract_failures(mutated), "schematic resume bypassed live receipt")


@test("schematic resume rejects omission of authored input census",
      kind="known_bad")
def t_schematic_resume_input_census_removed():
    text = RESUME_GATE.read_text(encoding="utf-8")
    mutated = text.replace('input_gate, "verify"',
                           'input_gate, "omitted"', 1)
    check(mutated != text, "fixture did not remove shared census check")
    check(resume_gate_failures(mutated),
          "schematic resume bypassed input census")


@test("reuse path rejects omission of shared prelayout authority",
      kind="known_bad")
def t_reuse_authority_removed():
    text = REUSE_DRIVERS[0].read_text(encoding="utf-8")
    mutated = text.replace('"$PRELAYOUT_RESUME_GATE" .',
                           '"$PRELAYOUT_RESUME_GATE_OMITTED" .', 1)
    check(mutated != text, "fixture did not remove reuse shared gate")
    check(reuse_failures(mutated), "reuse path bypassed shared authority")


@test("reuse path rejects direct overwrite of frozen netlist",
      kind="known_bad")
def t_reuse_netlist_overwrite():
    text = REUSE_DRIVERS[0].read_text(encoding="utf-8")
    mutated = text.replace('-o "$NETLIST_CANDIDATE"', '-o "$NETLIST"', 1)
    check(mutated != text, "fixture did not redirect exporter to frozen netlist")
    check(reuse_failures(mutated), "reuse path overwrote frozen netlist")


@test("reuse path rejects replacement of normalized electrical comparison",
      kind="known_bad")
def t_reuse_netlist_raw_compare():
    text = REUSE_DRIVERS[0].read_text(encoding="utf-8")
    mutated = text.replace(
        'netlist_digest(candidate) != netlist_digest(frozen)',
        'candidate.read_bytes() != frozen.read_bytes()', 1)
    check(mutated != text, "fixture did not replace normalized comparison")
    check(reuse_failures(mutated),
          "reuse path accepted a raw comparison of KiCad export metadata")


def policy(path: Path) -> Path:
    path.write_text(
        "schema: 1\ncurrency: USD\nlimits:\n"
        "  max_line_preorder_cash: 0\n"
        "  max_total_preorder_cash: 0\n"
        "  max_line_surplus_cost: 0\n"
        "  max_total_surplus_cost: 0\n"
        "  max_total_assembly_excess_cost: 0\n"
        "warnings:\n  surplus_ratio: 20\n",
        encoding="utf-8",
    )
    return path


@test("accepted prelayout receipt is rejected against a changed circuit",
      kind="known_bad")
def t_changed_circuit_receipt_rejected():
    root = tmpdir("crow-prelayout-receipt-")
    circuit = root / "circuit.json"
    circuit.write_text(json.dumps([
        {"type": "source_component", "name": "R1", "value": "10k",
         "supplier_part_numbers": {"jlcpcb": ["C100"]}},
    ]), encoding="utf-8")
    policy_path = policy(root / "procurement-policy.yaml")
    now = datetime.now(timezone.utc)
    request = pcba.prepare(
        circuit, build_quantity=5, phase="prelayout",
        procurement_policy=policy_path, generated_at=now)
    request_path = root / "request.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    response_path = root / "response.csv"
    with response_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=pcba.RESPONSE_FIELDS)
        writer.writeheader()
        writer.writerow({
            "Requested LCSC": "C100", "Resolved LCSC": "C100",
            "PCBA Status": "AVAILABLE", "Available Qty": "5",
            "Fulfillment": "PUBLIC_STOCK",
            "Economic Status": "NO_MINIMUM_COST", "Public Stock Qty": "5",
            "My Parts Qty": "0", "Attrition Qty": "0", "MOQ": "0",
            "Order Multiple": "0", "Preorder Purchase Qty": "0",
            "Preorder Part Subtotal": "0", "Preorder Fees": "0",
            "Assembly Charged Qty": "0", "Assembly Part Subtotal": "0",
            "Currency": "USD", "Checked At": now.isoformat(),
            "Evidence": "JLCPCB PCBA interface row",
        })
    receipt = pcba.grade(request_path, response_path,
                         max_age_hours=24, now=now)
    receipt_path = root / "receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    valid, failures, _ = pcba.verify_receipt(
        receipt_path, bom=circuit, required_phase="prelayout", now=now)
    check(valid and not failures, f"clean receipt fixture failed: {failures}")

    circuit.write_text(json.dumps([
        {"type": "source_component", "name": "R1", "value": "10k",
         "supplier_part_numbers": {"jlcpcb": ["C999"]}},
    ]), encoding="utf-8")
    valid, failures, _ = pcba.verify_receipt(
        receipt_path, bom=circuit, required_phase="prelayout", now=now)
    check(not valid, "receipt bound to the previous circuit was accepted")
    check(any("not bound to the current subject/BOM" in item for item in failures),
          f"changed-circuit diagnosis missing: {failures}")


def checkpoint_fixture():
    repo = tmpdir("crow-prelayout-inputs-")
    project = repo / "projects/demo-board"
    helper = repo / "projects/crow-roof-array-v1/03_src/prelayout_input_checkpoint.py"
    helper.parent.mkdir(parents=True)
    shutil.copy2(INPUT_CHECKPOINT, helper)

    for relative in (
        "skills/jlcpcb-fab/scripts/jlc_pcba_availability.py",
        "skills/jlcpcb-fab/scripts/manufacturing_readiness.py",
        "skills/kicad-pcb/scripts/stage_checkpoint.py",
        "skills/kicad-pcb/scripts/build_provenance.py",
        "projects/crow-roof-array-v1/03_src/prelayout_resume_gate.py",
        "projects/crow-roof-array-v1/03_src/check_spoke_interface.py",
        "projects/crow-roof-array-v1/03_src/rules/spoke_interface.yaml",
    ):
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"authority {relative}\n", encoding="utf-8")

    authored = {
        "02_parts/R1/part.yaml": "mpn: EXACT-R1\n",
        "02_parts/R1/authority.pdf": "%PDF-1.4 exact authority\n",
        "03_src/rebuild_all.sh": "#!/bin/bash\n",
        "03_src/floorplan.yaml": "board: demo\n",
        "03_src/route.yaml": "board: demo\n",
        "03_src/rules/mates.yaml": "device: demo_device\nconsumes: []\n",
        "03_src/rules/power_tree.yaml": "rails: []\n",
        "03_tscircuit/manifest.yaml": "schema: 1\n",
        "03_tscircuit/package.json": "{}\n",
        "03_tscircuit/bun.lock": "lock\n",
        "03_tscircuit/src/demo.tsx": "export const demo = 1\n",
        "01_docs/BRIEF.md": "# brief\n",
        "01_docs/capability-profile.json": "{}\n",
        "01_docs/ARCHITECTURE.md": "# architecture authority\n",
        "01_docs/DETAIL_DESIGN.md": "# numeric design authority\n",
        "01_docs/decisions/0001.md": "# decision\n",
        "01_docs/evidence/source.md": "# source\n",
        "01_docs/sourcing/procurement-policy.yaml": "schema: 1\n",
        "03_tscircuit/build/circuit.json": "[]\n",
        "06_build/sourcing/prelayout_request.json": "{}\n",
    }
    for relative, contents in authored.items():
        path = project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    foreign = repo / "external_hardware/demo_device"
    foreign.mkdir(parents=True)
    (foreign / "facts.yaml").write_text("schema: 1\nfacts: []\n")
    (foreign / "README.md").write_text("# foreign record\n")

    record = project / "06_build/checkpoints/prelayout-inputs.json"
    command = [
        "/usr/bin/python3", helper, "record", project,
        "--repo-root", repo, "--out", record,
        "--input", "03_tscircuit/build/circuit.json",
        "--input", "06_build/sourcing/prelayout_request.json",
    ]
    result = run(command)
    check(result.rc == 0, f"input checkpoint record failed: {result.out}")
    verify = [
        "/usr/bin/python3", helper, "verify", project,
        "--repo-root", repo, "--record", record,
    ]
    result = run(verify)
    check(result.rc == 0, f"clean input checkpoint failed: {result.out}")
    return repo, project, verify


@test("input checkpoint rejects changed electrical rule", kind="known_bad")
def t_rule_drift():
    _, project, verify = checkpoint_fixture()
    (project / "03_src/rules/power_tree.yaml").write_text("rails: [changed]\n")
    result = run(verify)
    check(result.rc != 0 and "recorded input changed" in result.out,
          f"changed rule passed: {result.out}")


@test("input checkpoint rejects deleted part dossier", kind="known_bad")
def t_dossier_drift():
    _, project, verify = checkpoint_fixture()
    (project / "02_parts/R1/part.yaml").unlink()
    result = run(verify)
    check(result.rc != 0 and "recorded input is missing" in result.out,
          f"deleted dossier passed: {result.out}")


@test("input checkpoint rejects changed normative detail design",
      kind="known_bad")
def t_detail_design_drift():
    _, project, verify = checkpoint_fixture()
    (project / "01_docs/DETAIL_DESIGN.md").write_text(
        "# changed numeric design authority\n")
    result = run(verify)
    check(result.rc != 0 and "recorded input changed" in result.out,
          f"changed DETAIL_DESIGN passed: {result.out}")


@test("input checkpoint rejects changed foreign hardware fact", kind="known_bad")
def t_foreign_fact_drift():
    repo, _, verify = checkpoint_fixture()
    (repo / "external_hardware/demo_device/facts.yaml").write_text(
        "schema: 1\nfacts: [changed]\n")
    result = run(verify)
    check(result.rc != 0 and "recorded input changed" in result.out,
          f"changed foreign fact passed: {result.out}")


@test("input checkpoint rejects a newly added rule", kind="known_bad")
def t_rule_addition():
    _, project, verify = checkpoint_fixture()
    (project / "03_src/rules/new_rule.yaml").write_text("new: true\n")
    result = run(verify)
    check(result.rc != 0 and "new input appeared" in result.out,
          f"new rule passed: {result.out}")


@test("input checkpoint rejects symlink substitution", kind="known_bad")
def t_symlink_substitution():
    repo, project, verify = checkpoint_fixture()
    dossier = project / "02_parts/R1/authority.pdf"
    target = repo / "same-authority.pdf"
    target.write_bytes(dossier.read_bytes())
    dossier.unlink()
    dossier.symlink_to(target)
    result = run(verify)
    check(result.rc != 0 and "symlink is forbidden" in result.out,
          f"symlink substitution passed: {result.out}")


@test("input checkpoint rejects a symlinked parent of an explicit input",
      kind="known_bad")
def t_explicit_parent_symlink():
    repo, project, verify = checkpoint_fixture()
    build = project / "03_tscircuit/build"
    target = repo / "aliased-generated-build"
    shutil.copytree(build, target)
    shutil.rmtree(build)
    build.symlink_to(target, target_is_directory=True)
    result = run(verify)
    check(result.rc != 0 and "symlink is forbidden" in result.out,
          f"explicit input through symlinked parent passed: {result.out}")


@test("input checkpoint rejects broken normative-document symlink",
      kind="known_bad")
def t_broken_optional_symlink():
    _, project, verify = checkpoint_fixture()
    detail = project / "01_docs/DETAIL_DESIGN.md"
    detail.unlink()
    detail.symlink_to("missing-detail-authority.md")
    result = run(verify)
    check(result.rc != 0 and "symlink is forbidden" in result.out,
          f"broken authority symlink passed: {result.out}")


@test("input checkpoint survives checkout directory relocation")
def t_input_checkpoint_relocation():
    repo, project, _ = checkpoint_fixture()
    relocated = repo.with_name(repo.name + "-renamed-checkout")
    repo.rename(relocated)
    helper = relocated / "projects/crow-roof-array-v1/03_src/prelayout_input_checkpoint.py"
    moved_project = relocated / project.relative_to(repo)
    record = moved_project / "06_build/checkpoints/prelayout-inputs.json"
    payload = json.loads(record.read_text(encoding="utf-8"))
    check(payload.get("schema") == 2 and
          payload.get("kind") == "crow-prelayout-input-checkpoint-v2" and
          payload.get("path_model") == "repo-relative-v1",
          f"portable path model absent: {payload.keys()}")
    check("repo" not in payload, "checkpoint retained checkout basename")
    result = run([
        "/usr/bin/python3", helper, "verify", moved_project,
        "--repo-root", relocated, "--record", record,
    ])
    check(result.rc == 0,
          f"byte-identical relocated checkpoint failed: {result.out}")


@test("input checkpoint rejects a missing frozen generated subject",
      kind="known_bad")
def t_generated_subject_deleted():
    _, project, verify = checkpoint_fixture()
    (project / "03_tscircuit/build/circuit.json").unlink()
    result = run(verify)
    check(result.rc != 0 and
          ("recorded input is missing" in result.out or
           "input is missing or not a regular file" in result.out),
          f"deleted generated subject passed: {result.out}")


@test("crow prelayout checkpoints have a tracked portable closure")
def t_repository_portable_checkpoint_closure():
    for project, board in PORTABLE_PROJECTS:
        stage_path = project / "06_build/checkpoints/prelayout.json"
        input_path = project / "06_build/checkpoints/prelayout-inputs.json"
        stage = json.loads(stage_path.read_text(encoding="utf-8"))
        census = json.loads(input_path.read_text(encoding="utf-8"))
        check(census.get("schema") == 2 and
              census.get("kind") == "crow-prelayout-input-checkpoint-v2" and
              census.get("path_model") == "repo-relative-v1" and
              "repo" not in census,
              f"{project.name}: checkpoint binds checkout identity")

        tracked = {project / relative for relative in stage["files"]}
        tracked.update(
            ROOT / key.removeprefix("repo:")
            for key in census["files"]
            if isinstance(key, str) and key.startswith("repo:"))
        response = project / "06_build/sourcing/prelayout_response.csv"
        tracked.add(response)
        result = run([
            "git", "-C", ROOT, "ls-files", "--error-unmatch", "--",
            *(path.relative_to(ROOT) for path in sorted(tracked)),
        ])
        check(result.rc == 0,
              f"{project.name}: checkpoint input missing from index: {result.out}")

        request_path = project / "06_build/sourcing/prelayout_request.json"
        request = json.loads(request_path.read_text(encoding="utf-8"))
        for name in ("subject", "assembly", "procurement_policy"):
            recorded = str((request.get(name) or {}).get("path") or "")
            check(recorded and not Path(recorded).is_absolute(),
                  f"{project.name}: request {name} is not portable: {recorded}")
        with response.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        check(len(rows) == request["coverage"]["total"],
              f"{project.name}: blank response row count differs from request")
        check(all(row["Requested LCSC"] and not any(
            value for key, value in row.items() if key != "Requested LCSC")
                  for row in rows),
              f"{project.name}: tracked response fabricates operator evidence")
        receipt = project / "06_build/sourcing/prelayout_receipt.json"
        check(not receipt.exists(),
              f"{project.name}: receipt exists without live JLC evidence")
        ignored = run(["git", "-C", ROOT, "check-ignore", "-q", "--",
                       receipt.relative_to(ROOT)])
        check(ignored.rc == 1,
              f"{project.name}: future operator receipt remains ignored")


@test("index-only relocated crow checkpoint resumes to missing receipt")
def t_index_export_relocation_resume():
    exported = tmpdir("crow-portable-index-export-")
    paths: set[Path] = set()
    for project, _ in PORTABLE_PROJECTS:
        stage_path = project / "06_build/checkpoints/prelayout.json"
        input_path = project / "06_build/checkpoints/prelayout-inputs.json"
        stage = json.loads(stage_path.read_text(encoding="utf-8"))
        census = json.loads(input_path.read_text(encoding="utf-8"))
        paths.update(project / relative for relative in stage["files"])
        paths.update(
            ROOT / key.removeprefix("repo:")
            for key in census["files"]
            if isinstance(key, str) and key.startswith("repo:"))
        paths.update({
            stage_path,
            input_path,
            project / "06_build/sourcing/prelayout_response.csv",
        })
    result = run([
        "git", "-C", ROOT, "checkout-index",
        f"--prefix={exported.as_posix()}/", "--",
        *(path.relative_to(ROOT) for path in sorted(paths)),
    ])
    check(result.rc == 0, f"index-only checkpoint export failed: {result.out}")

    for project, _ in PORTABLE_PROJECTS:
        relocated_project = exported / project.relative_to(ROOT)
        result = run([
            "bash", "03_src/rebuild_all.sh", "--resume-after-prelayout",
        ], cwd=relocated_project,
            env={"CIRCUITS_ROOT": str(exported)})
        check(result.rc == 2 and
              "PRELAYOUT-INPUT PASS (verify)" in result.out and
              "JLC-PCBA REQUEST PASS" in result.out and
              "J-PCBA-RECEIPT" in result.out and
              "missing regular file" in result.out,
              f"{project.name}: relocated index checkpoint did not stop "
              f"honestly at missing receipt: {result.out}")


if __name__ == "__main__":
    raise SystemExit(main())
