#!/usr/bin/env python3
"""Replay only public, unauthenticated JLC 4L 3313A calculator endpoints."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen
import uuid


HERE = Path(__file__).resolve().parent
BASE = "https://jlcpcb.com"
API = BASE + "/api/jlcTools/impedance/"


def fetch(path: str, payload: dict | None = None) -> tuple[dict | str, dict]:
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    with urlopen(Request(BASE + path, data=data, headers=headers), timeout=20) as response:
        raw = response.read()
        meta = {"status": response.status, "date": response.headers.get("Date"),
                "url": BASE + path}
    assert meta["status"] == 200, meta
    return (json.loads(raw) if path.startswith("/api/") else raw.decode()), meta


def calc(request: dict) -> tuple[dict, list[dict]]:
    attempts = []
    for _ in range(8):
        response, meta = fetch("/api/jlcTools/impedance/calc", request)
        attempts.append({"response": response, "http": meta})
        if response.get("body") is not None:
            assert response["result"] == "success"
            return response, attempts
        time.sleep(0.5)
    raise AssertionError("/calc stayed body:null after eight identical requests")


def main() -> None:
    html, page_http = fetch("/pcb-impedance-calculator")
    scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)', html)
    matches = []
    for source in scripts:
        if not source.startswith("/ssr/js/"):
            continue
        js, js_http = fetch(source)
        if "/jlcTools/impedance/calc" in js and "getThicknessBetween:function" in js:
            matches.append((source, js, js_http))
    assert len(matches) == 1
    source, js, js_http = matches[0]
    # Current UI: template-indexed material supplies H1/Er; accessId belongs
    # to a generated impedance-list item, and calc receives its numeric args.
    for witness in ("e.userTemplate.push(t.basicDataList)",
                    "getThicknessBetween:function(e,t,n)",
                    "r=this.userTemplate[n]", "accessId:e.generateUUID()",
                    "accessId:r.accessId", "impedance_calc_arg:c"):
        assert witness in js, witness

    template_request = {"pageNum": 1, "pageSize": 99999,
                        "plateLayerNumber": 4, "plateThickness": 1.6,
                        "cuprumThickness": 1, "innerCopperThickness": 0.5,
                        "boardType": 1, "usePurpose": 1}
    templates, templates_http = fetch(
        "/api/jlcTools/impedance/selectPageImpedanceDefaultTemplate",
        template_request)
    choices = [item for item in templates["body"]["list"]
               if item["appointName"] == "JLC04161H-3313A"]
    assert len(choices) == 1
    chosen = choices[0]
    assert "特殊" in chosen["receptionDisplayName"]
    # The public API exposes Chinese material labels; the browser translates
    # them to the English `Prepreg` branch used by getThicknessBetween.
    plies = [x for x in chosen["basicDataList"]
             if x["materialName"].startswith("3313 ")]
    assert [x["dielectricThick"] for x in plies[:2]] == [0.107, 0.0994]
    height = sum(x["dielectricThick"] for x in plies[:2])
    assert abs(height - 0.2064) < 1e-12
    assert all(x["dielectricConstant"] == 4.1 for x in plies[:2])

    pictures, pictures_http = fetch(
        "/api/jlcTools/impedance/selectPageImpedancePicture",
        {"layerNumber": None, "pageNum": 1, "pageSize": 999, "usePurpose": 1})
    models = [x for x in pictures["body"]["list"]
              if x["impedanceType"] == "DiffEdgeCoupledCoatedMicrostrip1B"
              and x["layerNumber"] == 1]
    assert len(models) == 1
    model = models[0]
    hz0 = next(x for x in model["parameterList"] if x["paramName"] == "HZ0")
    assert hz0["displayStatus"] == 4 and hz0["defaultValue"] == 108.0

    cover, cover_http = fetch("/api/jlcTools/impedance/impedance-config/coverlay/list", {})
    width, width_http = fetch("/api/jlcTools/impedance/impedance-config/copper-trace-width/list", {})
    def selected(config):
        found = [x for x in config["data"] if x["systemCopperThickness"] == 1
                 and x["baseCopperThickness"] == 0.5 and x["layerType"] == 1]
        assert len(found) == 1
        return found[0]
    mask = selected(cover)
    trace = selected(width)
    assert (mask["coatingAboveSubstrate"], mask["coatingAboveTrace"],
            mask["coatingBetweenTraces"]) == (1.0, 0.6, 1.0)
    assert (trace["traceCopperThickness"], trace["traceWidthDelta"]) == (1.6, 0.5)

    mil = 0.0254
    args = {key: 0 for key in ("H2", "Er2", "H3", "Er3", "H4", "Er4", "G1",
                                "G2", "D1", "O1", "REr")}
    args.update(dCalculateMode=3, H1=height/mil, Er1=4.1,
                W1=0.180/mil, W2=0.180/mil-trace["traceWidthDelta"],
                S1=0.100/mil, T1=trace["traceCopperThickness"],
                C1=mask["coatingAboveSubstrate"], C2=mask["coatingAboveTrace"],
                C3=mask["coatingBetweenTraces"], CEr=3.8, HZ0=108.0,
                isLinkComputingMode=False, W2LinkW1Incr=trace["traceWidthDelta"])
    request = {"accessId": uuid.uuid4().hex,
               "impedance_calc_mark": model["impedanceType"], "paramMd5": "",
               "impedance_calc_arg": args, "uuid": str(uuid.uuid4())}
    result, attempts = calc(request)
    ohms = result["body"]["impedance_calc_result"]["dImpedance"]
    assert result["body"]["impedance_calc_result"]["dResultValid"] == 1
    assert abs(ohms - 89.9172598796) < 1e-6, ohms
    changed = json.loads(json.dumps(request))
    changed["accessId"] = uuid.uuid4().hex
    changed["uuid"] = str(uuid.uuid4())
    changed["impedance_calc_arg"]["HZ0"] = 90.0
    control, control_attempts = calc(changed)
    control_ohms = control["body"]["impedance_calc_result"]["dImpedance"]
    assert abs(control_ohms - ohms) < 1e-9

    receipt = {"status": "PUBLIC_RESEARCH_ONLY", "frontend_script": source,
               "frontend_script_sha256": hashlib.sha256(js.encode()).hexdigest(),
               "page_http": page_http, "frontend_http": js_http,
               "template_request": template_request, "template_http": templates_http,
               "selected_template": chosen, "picture_http": pictures_http,
               "selected_model": model, "coverlay_http": cover_http,
               "selected_coverlay": mask, "trace_width_http": width_http,
               "selected_trace_width": trace, "calc_request": request,
               "calc_attempts": attempts, "control_request": changed,
               "control_attempts": control_attempts,
               "observed_ohms": ohms, "control_ohms": control_ohms,
               "bound_named_stack_by_live_ui": False,
               "p1_accepted": False, "release_admitted": False}
    (HERE / "frontend_binding_capture.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": "PUBLIC_RESEARCH_ONLY", "ohms": ohms,
                      "hz0_90_ohms": control_ohms,
                      "template": chosen["appointName"],
                      "frontend_sha256": receipt["frontend_script_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
