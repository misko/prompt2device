#!/usr/bin/env python3
"""Regression tests for the crow child-board commission and maturity records."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import yaml

from harness import ROOT, check, eq, main, test


STATE_SCRIPTS = ROOT / "skills/kicad-pcb/scripts"
sys.path.insert(0, str(STATE_SCRIPTS))

from project_state import derive  # noqa: E402


PROJECTS = (
    ROOT / "projects/crow-audio-carrier-v1",
    ROOT / "projects/crow-mic-pod-v3",
)
PROMPT = (
    "/pcb-design please help me design a star shaped distributed microphone "
    "array to record and isolate which crow is talking from my roof"
)
PROMPT_SHA256 = "a6fcb7d5b8465bc23415c7d5f9381b368f12d69455da135d8b6b0b1cb89965b3"
DIRECTIVES = (
    "i think we can do 8m radius! can we have the array be planar? identity "
    "needs to persist across recordings of 120s long , simultaneous crows do "
    "not need to be separated, short internal usb is acceptable",
    "8m diameter",
    "must recognition persist only across consecutive 120-second files, or "
    "across separate visits/hours/days and different perches? - no , it must "
    "only persist in the 120 second file if the crow does not move much",
    "Great sounds good lets use the rpi5 with this, please continue design!",
    "Great! Lets make a new branch for this board dev, and lets finish the "
    "board and get a release ready",
)
MATING_PARAGRAPH = (
    "The eight pod connectors are governed by the shared parent contract. The "
    "MCHStreamer pinout is CITED from its user manual and the short interconnect "
    "is selected as two exact Samtec `TCSD-06-D-04.50-01` assemblies. Because "
    "miniDSP does not publish its board-header MPN, module-side post fit, pin-1 "
    "orientation, cable continuity, and hot-plug/power ordering remain first-"
    "article holds. The exact miniDSP-authorized TDM8 image is available only "
    "through the purchaser/dealer download workflow; its original bytes, "
    "SHA-256, updater version, load evidence and module readback are an "
    "additional COTS acquisition hold, not project-authored firmware. No "
    "physical Pi or Ethernet mating occurs on this PCB."
)


def prompt_bytes(text: str) -> bytes:
    begin = "<!-- prompt-verbatim-begin -->\n"
    end = "\n<!-- prompt-verbatim-end -->"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise ValueError("prompt marker pair must be unique")
    payload = text.split(begin, 1)[1].split(end, 1)[0]
    # The file has a deliberate blank line before the closing marker. The
    # contract command strips that blank line's terminator and hashes the
    # original prompt's one trailing newline, which is what remains here.
    if not payload.endswith("\n") or payload.endswith("\n\n"):
        raise ValueError("prompt block must retain exactly one trailing newline")
    return payload.encode()


def validate_brief(project: Path, text: str) -> None:
    status = re.search(r"^status:\s*(\S+)$", text, re.M)
    if not status or status.group(1) not in {
        "draft", "agreed", "in-progress", "delivered", "superseded"
    }:
        raise ValueError("noncanonical BRIEF status")
    if "current_release: no" not in text or "order_status: DO-NOT-ORDER" not in text:
        raise ValueError("release/order posture missing")
    payload = prompt_bytes(text)
    if payload.decode().removesuffix("\n") != PROMPT:
        raise ValueError("original prompt bytes drifted")
    if hashlib.sha256(payload).hexdigest() != PROMPT_SHA256:
        raise ValueError("prompt digest drifted")
    if f"prompt_sha256: {PROMPT_SHA256}" not in text:
        raise ValueError("recorded prompt digest drifted")

    sections = (
        "## Original prompt",
        "## End goal — definition of done",
        "## Log",
        "## Decision register",
        "## Spec tensions",
        "## Mating fact-lock",
        "## Commission fact-lock",
    )
    offsets = [text.find(section) for section in sections]
    if any(offset < 0 for offset in offsets) or offsets != sorted(offsets):
        raise ValueError("required BRIEF sections missing or out of order")
    if "## Subsequent user directives" in text:
        raise ValueError("paraphrase-only directive section returned")

    for index, quote in enumerate(DIRECTIVES, 1):
        if f"### D{index} —" not in text or f"> {quote}" not in text:
            raise ValueError(f"D{index} is not a verbatim log entry")
    if project.name == "crow-audio-carrier-v1":
        if ("### D6 — 2026-09-07 — user directive" not in text or
                "> This is great news! lets keep going" not in text):
            raise ValueError("accepted prototype directive D6 missing")
        d7 = ("### D7 — 2026-09-10 — user directive\n"
              "> please verify public stock and contunue\n")
        if d7 not in text:
            raise ValueError("accepted exact distributor design-only directive D7 missing")
        rj45_id = "D8"
        unsupported = r"^### D(?:9|\d{2,})\b"
    else:
        rj45_id = "D6"
        unsupported = r"^### D(?:[7-9]|\d{2,})\b"
    rj45 = f"### {rj45_id} — 2026-09-12 — user directive\n\n> Great lets do it!\n"
    if text.count(f"### {rj45_id} —") != 1 or rj45 not in text:
        raise ValueError("RJ45 choice relabelled as a user directive")
    if re.search(unsupported, text, re.M):
        raise ValueError("engineering choice relabelled as a user directive")

    acceptance = [line for line in text.splitlines() if line.startswith("| G")]
    if not acceptance:
        raise ValueError("acceptance denominator is empty")
    known_tags = {"P"}
    known_tags.update(re.findall(r"^### ([DQA]\d+) —", text, re.M))
    for line in acceptance:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4:
            raise ValueError(f"malformed acceptance row: {line}")
        source, result = cells[2], cells[3]
        if not (result == "unmet" or result.startswith("met — [") or
                re.fullmatch(r"dropped — [DQ]\d+", result)):
            raise ValueError(f"noncanonical acceptance status: {result}")
        for tag in (token.strip() for token in source.split(",")):
            if tag not in known_tags:
                raise ValueError(f"unresolved acceptance source {tag}")

    actual_adrs = {
        path.relative_to(project / "01_docs").as_posix()
        for path in (project / "01_docs/decisions").glob("[0-9][0-9][0-9][0-9]-*.md")
    }
    indexed_adrs = set(re.findall(r"\]\((decisions/[0-9][^)]*\.md)\)", text))
    if indexed_adrs != actual_adrs:
        raise ValueError(
            f"decision register does not cover ADR set: indexed={indexed_adrs}, "
            f"actual={actual_adrs}"
        )


@test("crow child BRIEFs retain verbatim commission authority and canonical state")
def t_child_briefs():
    for project in PROJECTS:
        text = (project / "01_docs/BRIEF.md").read_text(encoding="utf-8")
        validate_brief(project, text)
    carrier = (PROJECTS[0] / "01_docs/BRIEF.md").read_text(encoding="utf-8")
    check(MATING_PARAGRAPH in carrier,
          "carrier Mating fact-lock TDM8 acquisition paragraph drifted")


@test("crow findings derive their governed maturity and bench plans claim no hardware result")
def t_maturity_and_plans():
    expected_maturity = {
        "crow-audio-carrier-v1": "DRAFT",
        "crow-mic-pod-v3": "DESIGN_CLEAN",
    }
    for project in PROJECTS:
        ledger = project / "01_docs/findings.yaml"
        value = yaml.safe_load(ledger.read_text(encoding="utf-8-sig"))
        expected = expected_maturity[project.name]
        eq(value["schema"], 1, f"{project.name} findings schema")
        eq(value["target"], expected, f"{project.name} declared target")
        eq(derive(project, ledger)["derived_maturity"], expected,
           f"{project.name} derived maturity")
        plan = (project / "01_docs/FIRST_ARTICLE_TEST_PLAN.md").read_text(
            encoding="utf-8")
        check("status: PLANNED — NO HARDWARE RESULT" in plan,
              f"{project.name} test plan overclaims evidence")
        check("01_docs/journal/first_article.json" in plan,
              f"{project.name} test plan omits structured evidence path")
        check("Immediate abort rules" in plan or "abort rules" in plan,
              f"{project.name} test plan omits abort authority")


@test("crow BRIEF governance rejects rewritten prompts and invented statuses",
      kind="known_bad")
def t_brief_regressions_fail():
    project = PROJECTS[0]
    text = (project / "01_docs/BRIEF.md").read_text(encoding="utf-8")
    broken = text.replace("status: in-progress", "status: release-ready", 1)
    broken = broken.replace(PROMPT, PROMPT + "!", 1)
    try:
        validate_brief(project, broken)
    except ValueError:
        return
    raise AssertionError("rewritten commission record passed governance validation")


@test("carrier D7 remains exact and unrecorded later directives are rejected",
      kind="known_bad")
def t_d7_directive_boundary():
    project = PROJECTS[0]
    text = (project / "01_docs/BRIEF.md").read_text(encoding="utf-8")
    for broken in (
        text.replace("### D7 — 2026-09-10 — user directive",
                     "### D7 — 2026-09-11 — user directive", 1),
        text.replace("> please verify public stock and contunue",
                     "> purchase and allocate production stock", 1),
        text + "\n### D9 — 2026-09-10 — user directive\n> place the order\n",
    ):
        check(broken != text, "directive mutation did not alter the fixture")
        try:
            validate_brief(project, broken)
        except ValueError as exc:
            check("D7 missing" in str(exc) or "relabelled as a user directive" in str(exc),
                  f"directive rejected for unrelated reason: {exc}")
        else:
            raise AssertionError("changed or invented directive passed governance")


@test("carrier hardware tests do not block the prototype needed to perform them")
def t_prototype_boundaries():
    value = yaml.safe_load((PROJECTS[0] / "01_docs/findings.yaml").read_text())
    findings = {item["id"]: item for item in value["findings"]}
    for key in ("CAR-F4-mch-physical-boundary", "CAR-F5-authorized-tdm8-image",
                "CAR-F6-no-hardware-evidence", "CAR-F8-connector-physical-qualification"):
        eq(findings[key]["blocks_at_or_above"], "FIRST_ARTICLE_TESTED", key)
        eq(findings[key]["state"], "open", f"{key} must not imply measurements")
    eq(findings["CAR-F1-live-jlc-prelayout"]["blocks_at_or_above"],
       "FIRST_ARTICLE_ORDERABLE", "allocation still blocks order")
    for name in ("rebuild_all.sh", "rebuild_reuse.sh"):
        script = (PROJECTS[0] / "03_src" / name).read_text()
        board = script.index('$PY "$S/generate_board_generic.py"')
        admission = script.index('bash 03_src/check_connector_prototype.sh', board)
        placement = script.index('placement_routability_preflight.py" grade .', board)
        check(board < admission < placement, f"{name} prototype admission ordering")


if __name__ == "__main__":
    sys.exit(main())
