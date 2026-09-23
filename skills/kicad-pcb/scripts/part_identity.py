"""Exact part identities and evidenced pin aliases shared by native exporters."""
from __future__ import annotations

from pathlib import Path

import yaml


def sval(value) -> str:
    return str(value).strip()


def pin_name(value) -> str:
    if isinstance(value, dict):
        return sval(value.get("name", ""))
    return sval(value)


def part_ids(doc: dict, path: Path) -> set[str]:
    ids = {sval(doc.get("mpn") or path.parent.name), path.parent.name}
    sourcing = doc.get("sourcing") or {}
    for value in [sourcing.get("lcsc"), *(sourcing.get("alternates") or [])]:
        if value:
            ids.add(sval(value))
    return ids


def load_parts(parts_dir: Path):
    by_id, docs, errors = {}, {}, []
    for path in sorted(parts_dir.glob("*/part.yaml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
        except Exception as exc:
            errors.append(f"{path}: cannot parse YAML: {exc}")
            continue
        mpn = sval(doc.get("mpn") or path.parent.name)
        docs[mpn] = (doc, path)
        for ident in part_ids(doc, path):
            if ident in by_id and by_id[ident] != mpn:
                errors.append(f"identifier {ident!r} resolves to both "
                              f"{by_id[ident]} and {mpn}")
            by_id[ident] = mpn
    return by_id, docs, errors


def alias_map(doc: dict, mpn: str, errors: list[str]):
    pins = {sval(k): v for k, v in (doc.get("pins") or {}).items()}
    raw = doc.get("pin_aliases") or {}
    if not isinstance(raw, dict):
        errors.append(f"{mpn}: pin_aliases must be a mapping keyed by logical pin")
        raw = {}
    raw = {sval(k): v for k, v in raw.items()}
    mapping = {}
    for logical in pins:
        spec = raw.get(logical)
        if spec is None:
            mapping[logical] = {"schematic": logical, "footprint": logical,
                                "fused": False}
            continue
        if not isinstance(spec, dict):
            errors.append(f"{mpn} pin {logical}: alias must be a mapping")
            continue
        unknown = set(spec) - {"schematic", "footprint", "fused", "why", "evidence"}
        if unknown:
            errors.append(f"{mpn} pin {logical}: unknown alias keys {sorted(unknown)}")
        schematic = sval(spec.get("schematic", logical))
        footprint = sval(spec.get("footprint", logical))
        changed = schematic != logical or footprint != logical
        if changed and (not sval(spec.get("why", "")) or
                        not sval(spec.get("evidence", ""))):
            errors.append(f"{mpn} pin {logical}: a non-identity alias requires "
                          "both why and evidence")
        mapping[logical] = {"schematic": schematic, "footprint": footprint,
                            "fused": bool(spec.get("fused", False))}
    extra = set(raw) - set(pins)
    if extra:
        errors.append(f"{mpn}: pin_aliases names pins absent from pins: {sorted(extra)}")
    return pins, mapping

