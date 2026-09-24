"""Source-selected IC research coverage and stale applicability regressions."""
import copy
import hashlib
import json
from pathlib import Path
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ic_reference_check as check


def make_project(tmp_path):
    project = tmp_path / "project"
    for folder in ("02_parts/CHIP", "03_src/rules", "03_tscircuit/build",
                   "06_build/netlists", "01_docs"):
        (project / folder).mkdir(parents=True, exist_ok=True)
    (project / "03_src/floorplan.yaml").write_text(yaml.safe_dump({
        "project": {"netlist": "06_build/netlists/test.net"},
        "board": {"layers": 4, "stackup": {"thickness_mm": 1.6}},
        "design_rules": {"min_clearance": 0.15},
        "zones": [{"net": "GND", "layers": ["In1.Cu"]}],
    }))
    (project / "03_src/rules/nets.yaml").write_text(yaml.safe_dump({
        "fab_tier": "advanced", "classes": {"USB_HS": {"min_width": "0.41mm"}},
    }))
    (project / "03_src/route.yaml").write_text(yaml.safe_dump({
        "route": {"common": {"clearance": 0.15}, "waves": []},
    }))
    (project / "03_src/rules/rf.yaml").write_text(yaml.safe_dump({
        "rf": {"cross_sections": [{"width_mm": 0.41, "gap_mm": 0.15}]},
    }))
    part = {"mpn": "CHIP-1", "package": "QFN-8", "footprint": "Pkg:QFN8",
            "type": "buck_converter", "pins": {str(i): "P" for i in range(1, 9)},
            "layout_refs": [{"tier": 1, "artifact": "Maker guide page 4", "reached": True},
                            {"tier": 2, "artifact": "Maker design files", "reached": False,
                             "why": "Public file unavailable after recorded vendor search"}]}
    (project / "02_parts/CHIP/part.yaml").write_text(yaml.safe_dump(part))
    elements = [{"type": "source_component", "name": ref,
                 "manufacturer_part_number": "CHIP-1"} for ref in ("IC_A", "IC_B")]
    (project / "03_tscircuit/build/circuit.json").write_text(json.dumps(elements))
    (project / "06_build/netlists/test.net").write_text('''(export
 (components
  (comp (ref "IC_A") (value "CHIP-1") (footprint "Pkg:QFN8"))
  (comp (ref "IC_B") (value "CHIP-1") (footprint "Pkg:QFN8"))
 )
 (libparts)
 (nets (net (code "1") (name "VIN")
   (node (ref "IC_A") (pin "1")) (node (ref "IC_B") (pin "1")))
 )
)
''')
    evidence = project / "01_docs/maker-guide.pdf"
    evidence.write_bytes(b"examined guide section 4 layout figure")
    sha = hashlib.sha256(evidence.read_bytes()).hexdigest()
    selected, findings = check.selected_components(project)
    assert not findings and len(selected) == 2
    bindings = check.source_bindings(project)
    apps = []
    for comp in selected:
        apps.append({"refdes": comp["refdes"], "mode": "synchronous buck",
                     "footprint": comp["footprint"], "critical_pins_or_nets": ["VIN"],
                     "stackup": "4L F.Cu/In1.Cu", "route_rules": "USB_HS",
                     "applicability": {"status": "applicable", "reasons": [],
                         "reviewed_for": {"mpn": comp["mpn"], "package": comp["package"],
                                          "mode": "synchronous buck",
                                          "circuit_sha256": comp["circuit_sha256"], **bindings}},
                     "extracted_constraints": ["VIN capacitor close to pad 1"]})
    inspected = {"source_path": "01_docs/maker-guide.pdf", "sha256": sha,
                 "locator": "page 4 figure 2", "notes": "Measured input-loop placement"}
    packet = {"schema": 1, "engineering_status": "INCOMPLETE", "parts": [{
        "mpn": "CHIP-1", "package": "QFN-8", "state": "complete",
        "research_owner": "board team", "next_action": "review placement",
        "artifacts": [{"publisher": "Maker", "artifact": "Maker guide page 4",
                       "url": "https://example.test/guide", "tier": 1, "format": "PDF",
                       "editable": False, "inspected": True,
                       "retrieval": {"status": "retrieved", "at": "2026-09-24",
                                     "detail": "Opened and measured page 4"},
                       "inspection": inspected}],
        "docs_fallback": {}, "applications": apps,
    }]}
    write_packet(project, packet)
    return project, packet


def write_packet(project, packet):
    (project / "03_src/rules/ic_reference_research.yaml").write_text(
        yaml.safe_dump(packet, sort_keys=False))


def test_complete_inspected_research_is_only_coverage_pass(tmp_path):
    project, _ = make_project(tmp_path)
    result = check.evaluate(project)
    assert result["status"] == "COVERAGE_PASS"
    assert result["engineering_status"] == "INCOMPLETE"
    assert result["coverage"] == {"selected_ic": 2, "applications": 2,
                                   "research_covered": 2}


def test_omitted_selected_ic_cannot_vanish(tmp_path):
    project, packet = make_project(tmp_path)
    packet["parts"][0]["applications"].pop()
    write_packet(project, packet)
    result = check.evaluate(project)
    assert result["status"] == "FAIL"
    assert any("IC_B: selected IC requires exactly one application" in x for x in result["findings"])


def test_duplicate_application_and_unmatched_dossier_artifact_fail(tmp_path):
    project, packet = make_project(tmp_path)
    packet["parts"][0]["applications"].append(
        copy.deepcopy(packet["parts"][0]["applications"][0]))
    write_packet(project, packet)
    result = check.evaluate(project)
    assert result["status"] == "FAIL"
    assert any("IC_A: selected IC requires exactly one application" in x for x in result["findings"])
    packet["parts"][0]["applications"].pop()
    packet["parts"][0]["artifacts"][0]["artifact"] = "Unknown PDF"
    write_packet(project, packet)
    result = check.evaluate(project)
    assert result["status"] == "FAIL"
    assert any("absent from" in x and "layout_refs" in x for x in result["findings"])


def test_found_url_is_not_inspected_evidence(tmp_path):
    project, packet = make_project(tmp_path)
    artifact = packet["parts"][0]["artifacts"][0]
    artifact["inspected"] = False
    artifact["retrieval"]["status"] = "found"
    artifact.pop("inspection")
    write_packet(project, packet)
    result = check.evaluate(project)
    assert result["status"] == "FAIL"
    assert any("no inspected artifact" in x for x in result["findings"])


def test_generic_pin_and_layout_placeholder_do_not_pass(tmp_path):
    project, packet = make_project(tmp_path)
    app = packet["parts"][0]["applications"][0]
    app["critical_pins_or_nets"] = ["Exact source pad/net map is bound by circuit_sha256."]
    app["extracted_constraints"] = [
        "Use the retained manufacturer primary layout guidance; verify final implementation separately."]
    write_packet(project, packet)
    result = check.evaluate(project)
    assert result["status"] == "FAIL"
    assert result["coverage"]["research_covered"] == 1
    assert any("critical_pins_or_nets must name connected source" in x for x in result["findings"])


def test_applies_to_suffix_does_not_turn_generic_prose_into_constraint(tmp_path):
    project, packet = make_project(tmp_path)
    app = packet["parts"][0]["applications"][0]
    app["critical_pins_or_nets"] = ["IC_A.1"]
    app["extracted_constraints"] = [
        "Use manufacturer application guidance when final routing is complete. Applies to IC_A.1."]
    write_packet(project, packet)
    result = check.evaluate(project)
    assert result["status"] == "FAIL"
    assert any("concrete rule tied" in x for x in result["findings"])


def test_changed_stack_or_rule_or_circuit_stales_review(tmp_path):
    project, _ = make_project(tmp_path)
    floor = project / "03_src/floorplan.yaml"
    text = floor.read_text().replace("min_clearance: 0.15", "min_clearance: 0.2")
    floor.write_text(text)
    assert any("stale applicability" in x for x in check.evaluate(project)["findings"])
    project, _ = make_project(tmp_path / "rule")
    nets = project / "03_src/rules/nets.yaml"
    nets.write_text(nets.read_text().replace("0.41mm", "0.5mm"))
    assert any("stale applicability" in x for x in check.evaluate(project)["findings"])
    project, _ = make_project(tmp_path / "circuit")
    net = project / "06_build/netlists/test.net"
    net.write_text(net.read_text().replace('(name "VIN")', '(name "VNEW")'))
    assert any("stale applicability" in x for x in check.evaluate(project)["findings"])
    project, packet = make_project(tmp_path / "mode")
    packet["parts"][0]["applications"][0]["mode"] = "power-save buck"
    write_packet(project, packet)
    assert any("stale applicability" in x for x in check.evaluate(project)["findings"])
    project, _ = make_project(tmp_path / "package")
    dossier = project / "02_parts/CHIP/part.yaml"
    dossier.write_text(dossier.read_text().replace("QFN-8", "QFN-8R"))
    assert any("no selected IC has exact MPN/package" in x for x in check.evaluate(project)["findings"])


def test_same_footprint_pad_clearance_change_stales_all_applicability(tmp_path):
    project, _ = make_project(tmp_path)
    nets_path = project / "03_src/rules/nets.yaml"
    nets = yaml.safe_load(nets_path.read_text())
    nets["same_footprint_pad_clearances"] = [{
        "id": "package_gap", "refs": ["IC_A"], "clearance": "0.15mm"}]
    nets_path.write_text(yaml.safe_dump(nets))
    result = check.evaluate(project)
    assert result["status"] == "FAIL"
    assert sum("stale applicability reviewed_for binding" in finding
               for finding in result["findings"]) == 2

    refreshed = check.source_bindings(project)["route_rules_sha256"]
    nets["same_footprint_pad_clearances"][0]["clearance"] = "0.10mm"
    nets_path.write_text(yaml.safe_dump(nets))
    assert check.source_bindings(project)["route_rules_sha256"] != refreshed


def test_unavailable_design_file_with_inspected_docs_completes_coverage(tmp_path):
    project, packet = make_project(tmp_path)
    row = packet["parts"][0]
    art = row["artifacts"][0]
    art["artifact"] = "Maker design files"
    art["tier"] = 2
    art["inspected"] = False
    art["retrieval"] = {"status": "unavailable", "at": "2026-09-24",
                        "detail": "Searched vendor downloads and requested PCB files"}
    art.pop("inspection")
    row["docs_fallback"] = {"artifact": "Maker guide page 4",
                            "url": "https://example.test/guide", "inspected": True,
                            "inspection": {"source_path": "01_docs/maker-guide.pdf",
                                           "sha256": hashlib.sha256((project / "01_docs/maker-guide.pdf").read_bytes()).hexdigest(),
                                           "locator": "page 4 figure 2", "notes": "Reviewed loop"},
                            "extracted_guidance": ["VIN capacitor close to pad 1"]}
    write_packet(project, packet)
    result = check.evaluate(project)
    assert result["status"] == "COVERAGE_PASS"
    assert result["engineering_status"] == "INCOMPLETE"
    assert result["docs_only"] == ["CHIP-1/QFN-8"]


def test_known_layout_mismatch_is_research_covered_but_unknown_is_not(tmp_path):
    project, packet = make_project(tmp_path)
    app = packet["parts"][0]["applications"][0]
    app["applicability"]["status"] = "limited"
    app["applicability"]["reasons"] = ["Reference uses a two-layer stack; target is four-layer"]
    write_packet(project, packet)
    result = check.evaluate(project)
    assert result["status"] == "COVERAGE_PASS"
    assert result["engineering_status"] == "INCOMPLETE"
    app["applicability"]["status"] = "unknown"
    write_packet(project, packet)
    assert check.evaluate(project)["status"] == "INCOMPLETE"


def test_missing_evidence_and_inspection_notes_fail_closed(tmp_path):
    project, packet = make_project(tmp_path)
    packet["parts"][0]["state"] = "missing_evidence"
    write_packet(project, packet)
    assert check.evaluate(project)["status"] == "INCOMPLETE"
    packet["parts"][0]["state"] = "complete"
    packet["parts"][0]["artifacts"][0]["inspection"].pop("notes")
    write_packet(project, packet)
    result = check.evaluate(project)
    assert result["status"] == "FAIL"
    assert any("locator and notes" in x for x in result["findings"])


def test_independent_semantic_receipt_binds_packet_and_source(tmp_path):
    project, packet = make_project(tmp_path)
    initial = check.evaluate(project)
    assert initial["status"] == "COVERAGE_PASS"
    assert initial["semantic_review"] == "UNVERIFIED"
    evidence = project / "08_reviews/ic_reference_semantic_notes.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("Independent review: pin roles and layout guidance checked against source.\n")
    receipt = {"schema": 1, "verdict": "approved", "reviewer": "reviewer.terra",
               "reviewed_at": "2026-09-24",
               "scope": "IC reference record semantics only",
               "packet_sha256": initial["packet_sha256"],
               "subject_sha256": initial["subject_sha256"],
               "reviewed_refs": initial["selected_refs"],
               "evidence": {"path": "08_reviews/ic_reference_semantic_notes.md",
                            "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
                            "locator": "full review note"}}
    review_path = project / "08_reviews/ic_reference_semantic_review.yaml"
    review_path.write_text(yaml.safe_dump(receipt))
    assert check.evaluate(project)["semantic_review"] == "APPROVED"
    receipt["reviewed_refs"] = []
    review_path.write_text(yaml.safe_dump(receipt))
    assert any("exact selected IC census" in x for x in
               check.evaluate(project)["semantic_findings"])
    receipt["reviewed_refs"] = initial["selected_refs"]
    receipt["subject_sha256"] = "0" * 64
    review_path.write_text(yaml.safe_dump(receipt))
    assert any("subject_sha256 is stale" in x for x in
               check.evaluate(project)["semantic_findings"])
    receipt["subject_sha256"] = initial["subject_sha256"]
    evidence.write_text("Review notes were changed after signoff.\n")
    review_path.write_text(yaml.safe_dump(receipt))
    assert any("evidence content hash is stale" in x for x in
               check.evaluate(project)["semantic_findings"])
    receipt["evidence"]["sha256"] = hashlib.sha256(evidence.read_bytes()).hexdigest()
    review_path.write_text(yaml.safe_dump(receipt))
    assert check.evaluate(project)["semantic_review"] == "APPROVED"
    packet["parts"][0]["next_action"] = "review physical placement"
    write_packet(project, packet)
    result = check.evaluate(project)
    assert result["status"] == "COVERAGE_PASS"
    assert result["semantic_review"] == "STALE"
    assert any("packet_sha256 is stale" in x for x in result["semantic_findings"])
    receipt["packet_sha256"] = result["packet_sha256"]
    receipt["reviewer"] = "board team"
    review_path.write_text(yaml.safe_dump(receipt))
    assert check.evaluate(project)["semantic_review"] == "STALE"


def test_legacy_migration_is_explicit(tmp_path):
    project, _ = make_project(tmp_path)
    (project / "03_src/rules/ic_reference_research.yaml").unlink()
    assert check.evaluate(project)["status"] == "INCOMPLETE"
    assert check.evaluate(project, allow_unmigrated=True)["status"] == "UNMIGRATED"


if __name__ == "__main__":
    # The KiCad /usr/bin/python3 toolchain does not require pytest.
    import tempfile
    for test in sorted(name for name in globals() if name.startswith("test_")):
        with tempfile.TemporaryDirectory() as tmp:
            globals()[test](Path(tmp))
        print("PASS", test)
