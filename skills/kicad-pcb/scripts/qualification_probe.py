#!/usr/bin/env python3
"""Small native compatibility fixture; invoked by pcb_flow qualification.

No product board is read or modified. This probes serialization, effective class
resolution and exact positive/negative native DRC; it is not a rule evaluator.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys


def identify(scratch: Path, cli: str):
    import pcbnew
    import yaml
    import process_runner
    from pipeline_runtime import run_stage
    import shutil
    paths = {Path(sys.executable).resolve(), Path(pcbnew.__file__).resolve(),
             Path(yaml.__file__).resolve(), Path(shutil.which("ldd") or "/missing/ldd").resolve()}
    for module in tuple(sys.modules.values()):
        file = getattr(module, "__file__", None)
        if file and Path(file).is_file():
            paths.add(Path(file).resolve())
    maps = Path("/proc/self/maps")
    if not maps.is_file():
        raise RuntimeError("qualification library discovery requires Linux /proc")
    for line in maps.read_text().splitlines():
        path = line.split()[-1]
        if path.startswith("/") and Path(path).is_file():
            paths.add(Path(path).resolve())
    for name, argv in (("cli-version", [cli, "--version"]), ("cli-libraries", ["ldd", cli])):
        log = scratch / f"{name}.log"
        execution = run_stage({"id": "PCB-COMMISSION", "work_class": "local", "timeout_s": 15},
                              argv, log_path=log, console=None)
        (scratch / f"{name}-runtime.json").write_text(json.dumps(execution.to_mapping()))
        if execution.status != "PASS":
            raise ValueError(f"cannot identify actual native tool: {name}: {log}")
        if name == "cli-libraries":
            for token in log.read_text().split():
                if token.startswith("/") and Path(token).is_file():
                    paths.add(Path(token).resolve())
        else:
            cli_version = log.read_text().strip()
    return {"cli_version": cli_version, "python": sys.version, "pcbnew": pcbnew.Version(), "yaml": yaml.__version__,
            "files": [str(p) for p in sorted(paths)]}


def native_probe(out: Path, scratch: Path, cli: str):
    import pcbnew as k
    import process_runner  # supplies the shared runtime import path
    from pipeline_runtime import run_stage
    cls = dict(name="Default", clearance=.2, track_width=.2, via_diameter=.6,
        via_drill=.3, microvia_diameter=.3, microvia_drill=.1, diff_pair_gap=.25,
        diff_pair_width=.2, diff_pair_via_gap=.25, wire_width=6, bus_width=12,
        line_style=0, pcb_color="rgba(0, 0, 0, 0.000)",
        schematic_color="rgba(0, 0, 0, 0.000)", priority=2147483647, tuning_profile="")
    observed = {}
    for case, gap in (("clean", .3), ("hostile", .1)):
        board = k.BOARD()
        pads = {}
        for i in range(2):
            net = k.NETINFO_ITEM(board, f"PROBE_{i}"); board.Add(net)
            fp = k.FOOTPRINT(board); fp.SetReference(f"J{i+1}"); board.Add(fp)
            pad = k.PAD(fp); pad.SetNumber("1"); pad.SetShape(k.PAD_SHAPE_RECT)
            pad.SetAttribute(k.PAD_ATTRIB_SMD)
            pad.SetSize(k.VECTOR2I(k.FromMM(1), k.FromMM(1)))
            layers = k.LSET(); layers.AddLayer(k.F_Cu); pad.SetLayerSet(layers)
            pad.SetNet(net)
            pad.SetPosition(k.VECTOR2I(k.FromMM(20+i*(1+gap)), k.FromMM(20)))
            fp.Add(pad); pads[f"J{i+1}.1"] = str(pad.m_Uuid.AsString())
        edge = k.PCB_SHAPE(board); edge.SetShape(k.SHAPE_T_RECT)
        edge.SetStart(k.VECTOR2I(k.FromMM(10), k.FromMM(10)))
        edge.SetEnd(k.VECTOR2I(k.FromMM(30), k.FromMM(30)))
        edge.SetLayer(k.Edge_Cuts); edge.SetWidth(k.FromMM(.05)); board.Add(edge)
        path = scratch / f"{case}.kicad_pcb"; k.SaveBoard(str(path), board)
        project = {"board": {"design_settings": {"rules": {"min_clearance": .1}}},
            "net_settings": {"classes": [cls, dict(cls, name="Probe", priority=0, clearance=.25)],
                "netclass_assignments": {},
                "netclass_patterns": [{"netclass": "Probe", "pattern": "PROBE_*"}]}}
        path.with_suffix(".kicad_pro").write_text(json.dumps(project))
        manager = k.SETTINGS_MANAGER(); manager.LoadProject(str(path.with_suffix(".kicad_pro")))
        reloaded = k.LoadBoard(str(path)); reloaded.SetProject(manager.Prj())
        reloaded.SynchronizeNetsAndNetClasses(False)
        for net in ("PROBE_0", "PROBE_1"):
            effective = reloaded.GetDesignSettings().m_NetSettings.GetEffectiveNetClass(net)
            if effective.GetName() != "Probe" or effective.GetClearance() != k.FromMM(.25):
                raise ValueError(f"netclass fallback after reload: {case}/{net}")
        if sum(len(list(fp.Pads())) for fp in reloaded.GetFootprints()) != 2:
            raise ValueError("pad census changed after reload")
        report_path = out / f"{case}.json"
        # Nested runner inherits the outer task deadline; keep individual DRC finite.
        result = run_stage({"id": "PCB-COMMISSION", "work_class": "local", "timeout_s": 30}, [cli, "pcb", "drc", "--severity-all", "--all-track-errors",
            "--exit-code-violations", "--format", "json", "-o", str(report_path), str(path)],
            log_path=scratch / f"{case}.log", console=None)
        (scratch / f"{case}-runtime.json").write_text(json.dumps(result.to_mapping()))
        report = json.loads(report_path.read_text())
        rows = report["violations"]
        if report["unconnected_items"] or report["schematic_parity"]:
            raise ValueError(f"unexpected connectivity finding in {case}")
        if case == "clean":
            if result.returncode != 0 or rows:
                raise ValueError("clean native fixture failed")
        elif (result.returncode == 0 or len(rows) != 1 or rows[0]["type"] != "clearance" or
              {r["uuid"] for r in rows[0]["items"]} != set(pads.values())):
            raise ValueError("hostile fixture did not report the exact pad pair")
        observed[case] = {"pads": pads, "classes": 2, "clearance_findings": len(rows)}
    return observed


def main():
    out = Path(os.environ["PCB_TASK_OUTPUT_DIR"])
    scratch = Path(os.environ["PCB_TASK_SCRATCH_DIR"])
    mode = sys.argv[1]
    print(f"qualification input: {scratch}; mode={mode}", flush=True)
    if mode == "identify":
        result, output, check = identify(scratch, os.environ["PCB_QUALIFY_KICAD_CLI"]), "identity.json", "identity"
    elif mode == "native":
        result = native_probe(out, scratch, os.environ["PCB_QUALIFY_KICAD_CLI"])
        output, check = "native.json", "native-compatibility"
    else:
        raise ValueError("expected identify or native")
    (out / output).write_text(json.dumps(result, sort_keys=True) + "\n")
    (out / "result.json").write_text(json.dumps({
        "subject": json.loads(os.environ["PCB_TASK_SUBJECT_JSON"]),
        "checks": {check: "PASS"}, "unresolved": []}) + "\n")
    count = 1 if mode == "identify" else len(result)
    print(f"qualification {mode}: coverage={count}/{count}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
