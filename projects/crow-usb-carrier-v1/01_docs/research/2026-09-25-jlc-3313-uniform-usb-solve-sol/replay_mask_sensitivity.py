#!/usr/bin/env python3
"""Two public, unauthenticated JLC 3313A fixed-artwork calculations."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import time
import uuid

from replay_frontend_binding import fetch

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE / "frontend_binding_capture.json"
OUT = HERE / "mask_sensitivity_capture.json"
GUIDE = "https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    old_bytes = PREVIOUS.read_bytes()
    old = json.loads(old_bytes)
    assert old["selected_template"]["appointName"] == "JLC04161H-3313A"
    assert old["calc_attempts"][-1]["response"]["body"]["impedance_calc_result"]["dResultValid"] == 1
    template_request = old["template_request"]
    templates, template_http = fetch(
        "/api/jlcTools/impedance/selectPageImpedanceDefaultTemplate", template_request)
    selected = [x for x in templates["body"]["list"]
                if x["appointName"] == "JLC04161H-3313A"]
    assert len(selected) == 1
    template = selected[0]
    assert template["impedanceDefaultTemplateKeyId"] == old["selected_template"]["impedanceDefaultTemplateKeyId"]
    assert template["impedanceDefaultTemplateAccessId"] == old["selected_template"]["impedanceDefaultTemplateAccessId"]
    assert "特殊" in template["receptionDisplayName"]
    plies = [x for x in template["basicDataList"] if x["materialName"].startswith("3313 ")]
    assert [x["dielectricThick"] for x in plies[:2]] == [0.107, 0.0994]
    assert all(x["dielectricConstant"] == 4.1 for x in plies[:2])
    core = [x for x in template["basicDataList"] if x["dielectricThick"] == 1.065]
    assert len(core) == 1 and core[0]["dielectricConstant"] == 4.38

    cover, cover_http = fetch("/api/jlcTools/impedance/impedance-config/coverlay/list", {})
    width, width_http = fetch("/api/jlcTools/impedance/impedance-config/copper-trace-width/list", {})
    def pick(config):
        rows = [x for x in config["data"] if x["systemCopperThickness"] == 1
                and x["baseCopperThickness"] == 0.5 and x["layerType"] == 1]
        assert len(rows) == 1
        return rows[0]
    live_mask, live_width = pick(cover), pick(width)
    assert [live_mask[x] for x in ("coatingAboveSubstrate", "coatingAboveTrace", "coatingBetweenTraces")] == [1.0, 0.6, 1.0]
    assert (live_width["traceCopperThickness"], live_width["traceWidthDelta"]) == (1.6, 0.5)

    base = old["calc_request"]["impedance_calc_arg"]
    assert base["H1"] == (0.107 + 0.0994) / 0.0254
    assert base["Er1"] == 4.1 and base["T1"] == 1.6
    assert base["W1"] == 0.180 / 0.0254 and base["S1"] == 0.100 / 0.0254
    assert base["CEr"] == 3.8 and base["dCalculateMode"] == 3
    assert old["calc_request"]["impedance_calc_mark"] == "DiffEdgeCoupledCoatedMicrostrip1B"
    cases = []
    for name, mask, reduction in (
        ("retained_live_config", (1.0, 0.6, 1.0), 0.5),
        ("guide_parameters", (1.2, 0.6, 1.2), 0.7),
    ):
        args = copy.deepcopy(base)
        args.update(C1=mask[0], C2=mask[1], C3=mask[2],
                    W2=args["W1"] - reduction, W2LinkW1Incr=reduction)
        request = {"accessId": uuid.uuid4().hex,
                   "impedance_calc_mark": "DiffEdgeCoupledCoatedMicrostrip1B",
                   "paramMd5": "", "impedance_calc_arg": args, "uuid": str(uuid.uuid4())}
        attempts = []
        outcome = {"valid": False, "ohms": None}
        for _ in range(8):
            try:
                response, http = fetch("/api/jlcTools/impedance/calc", request)
            except Exception as exc:
                outcome["error"] = repr(exc)
                break
            attempts.append({"http": http, "response": response})
            body = response.get("body")
            if body is None:
                time.sleep(0.5)
                continue
            result = body.get("impedance_calc_result") or {}
            valid = (response.get("result") == "success"
                     and body.get("impedance_calc_status") == 0
                     and result.get("dResultValid") == 1)
            outcome = {"valid": valid, "ohms": result.get("dImpedance") if valid else None}
            break
        if not outcome["valid"] and "error" not in outcome:
            outcome["error"] = "API returned no valid result"
        cases.append({"name": name, "mask_mil": mask, "top_width_reduction_mil": reduction,
                      "artwork_base_width_mm": 0.180, "artwork_spacing_mm": 0.100,
                      "modeled_top_width_mm": args["W2"] * 0.0254,
                      "request": request, "attempts": attempts, "outcome": outcome})

    capture = {
        "status": "PUBLIC_RESEARCH_ONLY", "previous_capture_sha256": digest(old_bytes),
        "source_template_url": "https://jlcpcb.com/pcb-impedance-calculator",
        "guide_url": GUIDE, "guide_parameters": "JLC public guide, updated 2026-09-16; calculation parameters table",
        "template_request": template_request, "template_http": template_http,
        "template": template, "live_mask_http": cover_http, "live_mask": live_mask,
        "live_width_http": width_http, "live_width": live_width,
        "cases": cases, "production_impedance_claim": False,
    }
    OUT.write_text(json.dumps(capture, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"capture_sha256": digest(OUT.read_bytes()),
                      "results": [{"name": x["name"], **x["outcome"]} for x in cases]}, indent=2))


if __name__ == "__main__":
    main()
