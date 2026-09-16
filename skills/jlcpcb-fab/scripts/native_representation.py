"""Explicit authority for a native body when fetched vendor CAD has no model.

This module validates identities and scope only. Physical registration remains
owned by model_registration_gate; A-RENDER measures independent Fab/pixel data.
"""
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_file(root, relative):
    p = Path(str(relative))
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError("native representation path must be bundle/project relative")
    resolved = (Path(root) / p).resolve()
    if not resolved.is_relative_to(Path(root).resolve()):
        raise ValueError("native representation path escapes its root")
    if not resolved.is_file() or resolved.stat().st_size == 0:
        raise ValueError(f"native representation file missing/empty: {relative}")
    return resolved


def declarations(rows):
    result = {}
    fields = {"reason", "mpn", "vendor_footprint_sha256", "model_sha256",
              "registration_group", "authority", "native_footprint", "generator",
              "provenance", "reviewer", "reviewed_on", "limitations"}
    for row in rows:
        spec = row.get("native_representation")
        if spec is None:
            continue
        cad_absent = isinstance(spec, dict) and spec.get("reason") == "vendor_cad_absent"
        required = ((fields - {"vendor_footprint_sha256"}) |
                    {"catalog_response_body_sha256", "absence_review", "pin_review",
                     "catalog_comparison"}) if cad_absent else fields
        if not isinstance(spec, dict) or set(spec) != required:
            raise ValueError("native_representation requires the closed authority schema")
        if (row.get("render_model_source") != "native" or
                spec["reason"] not in ("vendor_model_absent", "vendor_cad_absent")):
            raise ValueError("native representation requires an explicit supported absence reason")
        if cad_absent and spec["catalog_comparison"] != "unavailable":
            raise ValueError("absent catalog CAD cannot claim a vendor comparison")
        refs = row.get("refs")
        if (not isinstance(refs, list) or not refs or len(refs) != len(set(refs)) or
                any(not isinstance(r, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", r)
                    for r in refs)):
            raise ValueError("native representation refs must be explicit, unique and safe")
        if not re.fullmatch(r"C[0-9]+", str(row.get("lcsc", ""))):
            raise ValueError("native representation requires exact LCSC code")
        for key in ("mpn", "registration_group", "reviewer", "limitations"):
            if not isinstance(spec[key], str) or not spec[key].strip():
                raise ValueError(f"native representation requires {key}")
        date.fromisoformat(spec["reviewed_on"])
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", spec["registration_group"]):
            raise ValueError("native registration group must be a safe identifier")
        for key in (("catalog_response_body_sha256", "model_sha256") if cad_absent else
                    ("vendor_footprint_sha256", "model_sha256")):
            if not re.fullmatch(r"[a-f0-9]{64}", str(spec[key])):
                raise ValueError(f"native representation invalid {key}")
        for key in source_keys(spec):
            record = spec[key]
            expected = {"path", "sha256"} | ({"pages", "revision"} if key == "authority" else set())
            if (not isinstance(record, dict) or set(record) != expected or
                    not re.fullmatch(r"[a-f0-9]{64}", str(record.get("sha256", "")))):
                raise ValueError(f"native representation invalid {key} record")
            if key == "authority":
                pages = record["pages"]
                if (not isinstance(pages, list) or not pages or
                        any(type(p) is not int or p <= 0 for p in pages) or
                        len(pages) != len(set(pages)) or
                        not isinstance(record["revision"], str) or not record["revision"].strip()):
                    raise ValueError("native authority needs positive unique pages and revision")
        for ref in refs:
            if ref in result:
                raise ValueError(f"duplicate native representation ref {ref}")
            result[ref] = {**spec, "lcsc": row["lcsc"], "refs": sorted(refs)}
    return result


def source_keys(spec):
    return ("authority", "native_footprint", "generator", "provenance") + (
        ("absence_review", "pin_review") if spec["reason"] == "vendor_cad_absent" else ())


def check_catalog_response(directory, code, expected_body_sha, accepted_at=None):
    """Bind current affirmative absence; time is evaluated at twin production.

    Later offline overlay replays that production-time observation, preserving
    the dated claim rather than pretending a sealed artifact fetched today.
    """
    record_path = safe_file(directory, "catalog-response.json")
    record = json.loads(record_path.read_text())
    body = safe_file(directory, "catalog-response.body")
    url = f"https://easyeda.com/api/products/{code}/components"
    parsed = json.loads(body.read_bytes())
    now = datetime.fromisoformat(accepted_at) if accepted_at else datetime.now(timezone.utc)
    observed = datetime.fromisoformat(record["observed_at"])
    if now.tzinfo is None or observed.tzinfo is None or not 0 <= (now-observed).total_seconds() <= 86400:
        raise ValueError("catalog absence observation is future/stale/unzoned")
    if (record.get("schema") != 1 or record.get("lcsc") != code or
            record.get("url") != url or record.get("response_url") != url or
            record.get("status") != 200 or record.get("classification") != "absent" or
            record.get("body_size") != body.stat().st_size or
            record.get("body_sha256") != sha(body) or sha(body) != expected_body_sha or
            not isinstance(parsed, dict) or set(parsed) != {"success", "code", "message"} or
            parsed["success"] is not False or type(parsed["code"]) is not int or
            parsed["code"] != 404 or parsed["message"] != "Component not found" or
            record.get("parsed") != parsed):
        raise ValueError("catalog absence response identity/transport/shape differs")
    if list(Path(directory).rglob("*.kicad_mod")):
        raise ValueError("catalog footprint now exists; absence selection must be reviewed")
    return sha(record_path)


def check_vendor(spec, code, footprint, model_count, catalog_dir=None, accepted_at=None):
    if code != spec["lcsc"] or model_count != 0:
        raise ValueError("native absence authority disagrees with code/vendor model count")
    if spec["reason"] == "vendor_cad_absent":
        if footprint or catalog_dir is None:
            raise ValueError("catalog absence cannot include a vendor footprint")
        return check_catalog_response(catalog_dir, code, spec["catalog_response_body_sha256"], accepted_at)
    if not footprint or sha(footprint) != spec["vendor_footprint_sha256"]:
        raise ValueError("native absence authority disagrees with fetched footprint bytes")


def check_source_files(project, spec):
    for key in source_keys(spec):
        record = spec[key]
        if sha(safe_file(project, record["path"])) != record["sha256"]:
            raise ValueError(f"native representation {key} source changed")


def check_overlay_receipt(bundle, source_board, ref, code, footprint, model_count, spec):
    """Reopen delivered identities without using rendered pixels as authority."""
    receipt = json.loads(safe_file(bundle, "native_representation_receipt.json").read_text())
    catalog_sha = check_vendor(spec, code, footprint, model_count,
                              Path(bundle) / "easyeda" / code, receipt.get("created_at"))
    if receipt.get("schema") != 1 or receipt.get("source_board_sha256") != sha(source_board):
        raise ValueError("native representation receipt source board differs")
    if receipt.get("twin_board_sha256") != sha(safe_file(bundle, "twin.kicad_pcb")):
        raise ValueError("native representation receipt twin board differs")
    matches = [r for r in receipt.get("rows", []) if r.get("ref") == ref]
    if len(matches) != 1 or matches[0].get("declaration") != spec:
        raise ValueError("native representation receipt scope/authority differs")
    row = matches[0]
    if set(row.get("source_files", {})) != set(source_keys(spec)):
        raise ValueError("native representation delivered source authority is incomplete")
    for key, path in row["source_files"].items():
        if sha(safe_file(bundle, path)) != spec[key]["sha256"]:
            raise ValueError(f"native representation delivered {key} differs")
    if spec["reason"] == "vendor_cad_absent":
        if (not receipt.get("created_at") or row.get("catalog_comparison") != "unavailable" or
                row.get("catalog_response_sha256") != catalog_sha):
            raise ValueError("catalog absence receipt comparison/observation differs")
    if sha(safe_file(bundle, row["model"])) != spec["model_sha256"]:
        raise ValueError("native representation bundled model differs")
    registration = safe_file(bundle, row["registration_manifest"])
    if sha(registration) != row["registration_manifest_sha256"]:
        raise ValueError("native representation registration manifest differs")
    manifest = json.loads(registration.read_text())
    if manifest.get("status") != "PASS":
        raise ValueError("native representation registration is not accepted")
    for name, record in manifest["outputs"].items():
        artifact = safe_file(registration.parent, name)
        if artifact.stat().st_size != record["size"] or sha(artifact) != record["sha256"]:
            raise ValueError("native representation registration evidence differs")
    return row
