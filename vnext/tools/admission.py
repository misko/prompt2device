"""Structural stage-admission verifier; never substitutes for engineering review.

Review JSON is the sole ``json`` fenced block in a dated 08_reviews Markdown file.
It records an independent verdict, not a producer-generated assessment. Certificates
are freshness receipts; this tool does not promote STATUS or remove a hold.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path


class AdmissionError(ValueError):
    pass


CRITERIA = {
    "PCB-COMMISSION": ("scope", "input_envelope", "applicability", "qualification_boundary"),
    "PCB-ARCHITECTURE": ("power", "analog", "digital", "external_interfaces", "budget", "integration"),
    "PCB-SOURCING": ("exact_identity", "pin_facts", "availability", "assembly", "cost"),
}
ROLES = {"PCB-COMMISSION": "commissioned_brief", "PCB-ARCHITECTURE": "architecture_locked", "PCB-SOURCING": "parts_locked"}
PREVIOUS = {"PCB-ARCHITECTURE": "commissioned_brief", "PCB-SOURCING": "architecture_locked"}
REQUIRED = {
    "PCB-COMMISSION": {"01_docs/BRIEF.md", "01_docs/capability-profile.json", "03_src/rules/requirements.yaml"},
    "PCB-ARCHITECTURE": {"01_docs/ARCHITECTURE.md", "01_docs/DETAIL_DESIGN.md", "03_src/rules/power_tree.yaml", "03_src/rules/integration.yaml"},
    "PCB-SOURCING": {"01_docs/sourcing/exact-parts.csv", "contracts.md", "01_docs/schematic-contract.json", "01_docs/capability-profile.json"},
}
SHA = re.compile(r"[0-9a-f]{64}\Z")
FENCE = re.compile(r"^```json[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[-_].*)?\.md$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_keys(obj: object, keys: set[str], label: str) -> dict:
    if not isinstance(obj, dict) or set(obj) != keys:
        raise AdmissionError(f"{label}: expected exactly {sorted(keys)}")
    return obj


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise AdmissionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(data: bytes, label: str) -> dict:
    try:
        return json.loads(data, object_pairs_hook=unique_pairs)
    except (ValueError, UnicodeError) as exc:
        raise AdmissionError(f"{label}: invalid JSON: {exc}") from exc


def safe_file(project: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise AdmissionError(f"invalid project path: {relative!r}")
    rel = Path(relative)
    if rel.is_absolute() or any(p in ("", ".", "..") for p in relative.split("/")):
        raise AdmissionError(f"path escapes project: {relative!r}")
    path = project / rel
    if not path.resolve().is_relative_to(project.resolve()) or not path.is_file():
        raise AdmissionError(f"missing or escaping file: {relative}")
    return path


def nonempty(project: Path, relative: str) -> bytes:
    data = safe_file(project, relative).read_bytes()
    if not data.strip():
        raise AdmissionError(f"empty file: {relative}")
    return data


def review_data(project: Path, review_path: str) -> tuple[dict, bytes]:
    if not review_path.startswith("08_reviews/") or not DATE.fullmatch(Path(review_path).name):
        raise AdmissionError("review must be dated Markdown under 08_reviews/")
    raw = nonempty(project, review_path)
    try:
        body = raw.decode("utf-8")
    except UnicodeError as exc:
        raise AdmissionError("review is not UTF-8") from exc
    blocks = FENCE.findall(body)
    if len(blocks) != 1:
        raise AdmissionError("review needs exactly one fenced json block")
    obj = exact_keys(parse_json(blocks[0].encode(), "review"),
                     {"schema", "stage", "author", "reviewer", "verdict", "subjects", "checks"}, "review")
    if type(obj["schema"]) is not int or obj["schema"] != 1 or obj["stage"] not in CRITERIA:
        raise AdmissionError("unsupported review schema or stage")
    for identity in ("author", "reviewer"):
        if not isinstance(obj[identity], str) or not obj[identity].strip():
            raise AdmissionError(f"missing {identity}")
    if obj["author"].strip().casefold() == obj["reviewer"].strip().casefold():
        raise AdmissionError("author and reviewer must differ")
    if obj["verdict"] != "PASS":
        raise AdmissionError("review verdict is not PASS")
    subjects = obj["subjects"]
    if not isinstance(subjects, dict) or not subjects:
        raise AdmissionError("subjects must be nonempty path-to-SHA map")
    for path, recorded in subjects.items():
        resolved = safe_file(project, path).resolve().relative_to(project.resolve()).as_posix()
        if path.startswith(("03_src/drafts/", "06_build/drafts/")) or resolved.startswith(("03_src/drafts/", "06_build/drafts/")):
            raise AdmissionError("draft artifacts cannot supply admission evidence")
        if not isinstance(recorded, str) or not SHA.fullmatch(recorded):
            raise AdmissionError(f"invalid subject hash: {path}")
        if digest(nonempty(project, path)) != recorded:
            raise AdmissionError(f"stale subject: {path}")
    missing = REQUIRED[obj["stage"]] - subjects.keys()
    if missing:
        raise AdmissionError(f"missing required subjects: {sorted(missing)}")
    checks = obj["checks"]
    exact_keys(checks, set(CRITERIA[obj["stage"]]), "checks")
    for criterion, check in checks.items():
        exact_keys(check, {"verdict", "evidence", "rationale"}, criterion)
        if check["verdict"] != "PASS" or not isinstance(check["rationale"], str) or not check["rationale"].strip():
            raise AdmissionError(f"failed or empty criterion: {criterion}")
        evidence = check["evidence"]
        if not isinstance(evidence, list) or not evidence or any(not isinstance(p, str) or p not in subjects for p in evidence):
            raise AdmissionError(f"criterion lacks subject evidence: {criterion}")
    covered = {path for check in checks.values() for path in check["evidence"]}
    if not REQUIRED[obj["stage"]].issubset(covered):
        raise AdmissionError("required source lacks criterion coverage")
    if obj["stage"] == "PCB-SOURCING":
        dossiers = {p for p in subjects if p.startswith("02_parts/") and p.endswith("/part.yaml")}
        datasheets = {p for p in subjects if p.startswith("02_parts/") and p.lower().endswith(".pdf")}
        for criterion, required in {
            "exact_identity": {"01_docs/sourcing/exact-parts.csv"} | dossiers,
            "pin_facts": dossiers | datasheets,
            "availability": {"01_docs/sourcing/exact-parts.csv"} | dossiers,
        }.items():
            if not required.issubset(set(checks[criterion]["evidence"])):
                raise AdmissionError(f"{criterion} must cite every selected primary subject")
    if obj["stage"] == "PCB-COMMISSION":
        provenance = check_prompt(nonempty(project, "01_docs/BRIEF.md"), project, subjects)
        if not provenance.issubset(covered):
            raise AdmissionError("raw provenance lacks criterion coverage")
    if obj["stage"] == "PCB-SOURCING":
        sourcing_contract(project, obj)
        check_sourcing(project, subjects)
        policies = {p for p in subjects if p.startswith("01_docs/decisions/")
                    and p.endswith(".md") and "sourc" in p.lower()}
        if not policies.issubset(covered):
            raise AdmissionError("sourcing policy lacks criterion coverage")
    if obj["stage"] == "PCB-ARCHITECTURE":
        from source_snapshot import SnapshotError, validate
        try:
            members = validate(project, subjects)
        except SnapshotError as exc:
            raise AdmissionError(f"source snapshot: {exc}") from exc
        if not set(members).issubset(covered):
            raise AdmissionError("complete source snapshot lacks criterion coverage")
    return obj, raw


def check_prompt(raw: bytes, project: Path, subjects: dict) -> set[str]:
    text = raw.decode("utf-8")
    status = re.findall(r"(?im)^status:[ \t]*(\S+)[ \t]*$", text)
    if len(status) != 1 or status[0].lower() not in {"agreed", "in-progress"}:
        raise AdmissionError("brief requires current agreed or in-progress status")
    # Bootstrap stores immutable raw inputs instead of duplicating their text
    # in the brief. Bind all three provenance entries, including decisions;
    # never allow an inline fallback to bypass an existing raw-input project.
    raw_paths = ("01_docs/inputs/PROMPT.md", "01_docs/inputs/USER_DECISIONS.md",
                 "01_docs/capability-profile.json")
    raw_mode = ((project / "01_docs/inputs").exists()
                or any(path in text or path in subjects for path in raw_paths[:2]))
    if raw_mode:
        for path in raw_paths:
            hashes = re.findall(r"(?m)^- `" + re.escape(path)
                                + r"` — SHA-256 `([0-9a-f]{64})`[ \t]*$", text)
            if len(hashes) != 1 or path not in subjects:
                raise AdmissionError(f"raw provenance missing, duplicate or unbound: {path}")
            actual = digest(nonempty(project, path))
            if hashes[0] != actual or subjects[path] != actual:
                raise AdmissionError(f"raw provenance hash mismatch: {path}")
        return set(raw_paths)
    sha = re.findall(r"(?m)^prompt_sha256:[ \t]*([0-9a-f]{64})[ \t]*$", text)
    start = "<!-- prompt-verbatim-begin -->\n"
    end = "<!-- prompt-verbatim-end -->"
    if len(sha) != 1 or text.count(start) != 1 or text.count(end) != 1:
        raise AdmissionError("brief needs one preserved prompt and prompt_sha256")
    prompt = text.split(start, 1)[1].split(end, 1)[0]
    if not prompt.endswith("\n"):
        raise AdmissionError("prompt marker must follow final newline")
    prompt = prompt[:-1]
    if not prompt or digest(prompt.encode()) != sha[0]:
        raise AdmissionError("original prompt hash mismatch")
    return {"01_docs/BRIEF.md"}


def require(condition, message):
    if not condition:
        raise AdmissionError(message)


def source_contract(project):
    """Validate applicability and declared paths before any CAD exists."""
    contract = parse_json(nonempty(project, '01_docs/schematic-contract.json'), 'schematic contract')
    require(isinstance(contract,dict),'schematic contract must be an object')
    version=contract.get('version')
    exact_keys(contract, {'version', 'manifest', 'expected', 'rf'} |
                        ({'producers'} if version==2 else set()), 'schematic contract')
    require(type(version) is int and version in (1,2),
            'unsupported schematic contract')
    if version==2:
        producers=contract['producers']
        require(isinstance(producers,list) and producers and all(isinstance(v,str) for v in producers)
                and len(producers)==len(set(producers)) and set(producers)<={'native','imported'},
                'explicit supported producers required')
    # RF clearance/hierarchical schematic routes have not been migrated. An
    # independent applicability check owns this declaration, not a default false.
    require(contract['rf'] is False, 'RF schematic admission is not implemented')
    capability = parse_json(nonempty(project, '01_docs/capability-profile.json'), 'capability')
    require(isinstance(capability, dict), 'capability must be an object')
    require('rf' not in capability or type(capability['rf']) is bool,
            'capability.rf must be boolean when present')
    require('signal_integrity' not in capability or isinstance(capability['signal_integrity'], str),
            'capability.signal_integrity must be a string when present')
    require('signal_integrity' not in capability or capability['signal_integrity'] in
            ('ordinary', 'high_speed_digital', 'rf'),
            'capability.signal_integrity must be ordinary, high_speed_digital or rf; unknown scope is not non-RF')
    require(capability.get('rf') is not True
            and capability.get('signal_integrity') != 'rf',
            'RF applicability conflicts with supported schematic route')
    for key in ('manifest', 'expected'):
        # Declaration may precede authoring, but never permits an escaping or
        # draft output. Actual file existence is checked by assembly replay.
        name = contract[key]
        require(isinstance(name, str), 'schematic paths must be strings')
        path = Path(name)
        require(name and not path.is_absolute() and '..' not in path.parts
                and str(path) == name and '\\' not in name and name != '.',
                'invalid schematic declaration path')
        resolved = (project/name).resolve()
        require(resolved.is_relative_to(project.resolve()), 'schematic declaration escapes project')
        relative = resolved.relative_to(project.resolve()).as_posix()
        require(not any(p.startswith(('03_src/drafts/', '06_build/drafts/'))
                        for p in (name, relative)), 'draft declaration is not production source')
    require(contract['manifest'] != contract['expected'], 'manifest and independent expectation must differ')
    return contract


def sourcing_contract(project, review):
    """The same handoff predicate runs at sourcing admission and schematic dispatch."""
    required = {'contracts.md', '01_docs/schematic-contract.json',
                '01_docs/capability-profile.json'}
    require(required <= set(review['subjects']), 'sourcing contract subjects missing')
    require(required <= set(review['checks']['assembly']['evidence']),
            'sourcing assembly review must cover schematic, project and capability contracts')
    return source_contract(project)


def check_sourcing(project: Path, subjects: dict) -> None:
    table = nonempty(project, "01_docs/sourcing/exact-parts.csv").decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(table))
    if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
        raise AdmissionError("invalid exact-parts header")
    identity = next((field for field in ("MPN", "mpn", "Comment") if field in reader.fieldnames), None)
    if not identity:
        raise AdmissionError("exact-parts needs Comment or MPN identity column")
    rows = list(reader)
    if not rows or any(None in row or not (row.get(identity) or "").strip() for row in rows):
        raise AdmissionError("exact-parts has no selected exact parts or blank identities")
    for row in rows:
        mpn = row[identity].strip()
        if "Dossier" in reader.fieldnames:
            # Ordering identities are data, not paths (for example SS14-E3/61T).
            dossier = (row.get("Dossier") or "").strip()
            if not dossier.startswith("02_parts/") or not dossier.endswith("/part.yaml"):
                raise AdmissionError(f"invalid explicit dossier path: {mpn}")
            safe_file(project, dossier)
        else:
            # Preserve the historical convention for existing tables only.
            if "/" in mpn or "\\" in mpn or mpn in {".", ".."}:
                raise AdmissionError(f"part identity needs explicit Dossier path: {mpn}")
            dossier = f"02_parts/{mpn}/part.yaml"
        if dossier not in subjects:
            raise AdmissionError(f"selected part lacks dossier: {mpn}")
        folder = dossier.rsplit("/", 1)[0] + "/"
        datasheets = [p for p in subjects if p.startswith(folder) and p.lower().endswith(".pdf")]
        if not datasheets:
            raise AdmissionError(f"selected part lacks retained datasheet: {mpn}")
    adrs = [p for p in subjects if p.startswith("01_docs/decisions/") and p.endswith(".md") and "sourc" in p.lower()]
    if not adrs:
        raise AdmissionError("sourcing policy ADR not bound as subject")


def identities(tool_root: Path) -> dict[str, str]:
    files = {
        "verifier": tool_root / "tools/admission.py",
        "source_snapshot": tool_root / "tools/source_snapshot.py",
        "instruction": tool_root / "skills/pcb-design/procedures/commission/admission.md",
        "graph": tool_root / "skills/pcb-design/workflow/graph.json",
        "pcb_skill": tool_root / "skills/pcb-design/SKILL.md",
        "commission": tool_root / "skills/pcb-design/workflow/stages/commission.md",
        "architecture": tool_root / "skills/pcb-design/workflow/stages/architecture.md",
        "sourcing": tool_root / "skills/pcb-design/workflow/stages/sourcing.md",
        "project_binding": tool_root / "skills/pcb-design/bindings/project.md",
        "part_recheck": tool_root / "skills/pcb-design/procedures/part-recheck.md",
    }
    return {name: digest(path.read_bytes()) for name, path in files.items()}


def check_graph(tool_root: Path, stage: str) -> None:
    graph = parse_json((tool_root / "skills/pcb-design/workflow/graph.json").read_bytes(), "graph")
    specs = [item["spec"] for item in graph["stages"] if item["spec"]["id"] == stage]
    required = [] if stage not in PREVIOUS else [PREVIOUS[stage]]
    if len(specs) != 1 or specs[0]["produces"] != [ROLES[stage]] or specs[0]["requires"] != required:
        raise AdmissionError("graph stage roles or prerequisites differ from admission contract")


def certificate(project: Path, review: str, tool_root: Path, seen: set[str] | None = None) -> dict:
    obj, raw = review_data(project, review)
    stage = obj["stage"]
    check_graph(tool_root, stage)
    prereq = {}
    if stage in PREVIOUS:
        role = PREVIOUS[stage]
        path = f"06_build/checkpoints/{role}.json"
        if seen is None:
            seen = set()
        if path in seen:
            raise AdmissionError("certificate cycle")
        prior = validate_certificate(project, path, tool_root, seen | {path})
        if prior["role"] != role:
            raise AdmissionError("wrong prerequisite role")
        prereq[path] = digest(nonempty(project, path))
    return {"schema": 1, "stage": stage, "role": ROLES[stage], "review": review,
            "review_sha256": digest(raw), "subjects": obj["subjects"],
            "identities": identities(tool_root), "prerequisites": prereq}


def validate_certificate(project: Path, path: str, tool_root: Path, seen: set[str] | None = None) -> dict:
    if not path.startswith("06_build/checkpoints/") or not path.endswith(".json"):
        raise AdmissionError("certificate must be under 06_build/checkpoints/")
    stored = parse_json(nonempty(project, path), "certificate")
    exact_keys(stored, {"schema", "stage", "role", "review", "review_sha256", "subjects", "identities", "prerequisites"}, "certificate")
    expected = certificate(project, stored["review"], tool_root, seen)
    if stored != expected or Path(path).name != f"{expected['role']}.json":
        raise AdmissionError("stale, forged, or misplaced certificate")
    return stored


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    sub = parser.add_subparsers(dest="action", required=True)
    check = sub.add_parser("check", help="read-only recursive certificate validation")
    check.add_argument("--certificate", required=True)
    issue = sub.add_parser("issue", help="write only a new checkpoint certificate")
    issue.add_argument("--review", required=True)
    issue.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    project = args.project.resolve()
    tool_root = Path(__file__).resolve().parents[1]
    try:
        if args.action == "check":
            result = validate_certificate(project, args.certificate, tool_root)
        else:
            result = certificate(project, args.review, tool_root)
            out = args.out
            if out != f"06_build/checkpoints/{result['role']}.json":
                raise AdmissionError("output must be canonical checkpoint path")
            target = project / out
            parts = (project / "06_build", target.parent, target)
            if (any(path.is_symlink() for path in parts)
                    or target.exists()
                    or not target.parent.resolve().is_relative_to(project)
                    or not target.resolve().is_relative_to(project)):
                raise AdmissionError("refusing overwrite, symlink, or escaping output")
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation also refuses an entry created between checks.
            with target.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"{result['stage']} structural evidence current; engineering verdict remains reviewer-owned")
        return 0
    except (AdmissionError, OSError, UnicodeError, TypeError, KeyError) as exc:
        print(f"admission refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
