#!/usr/bin/python3
import json
from pathlib import Path

OLD = Path("/tmp/crow-adc65-schematic-run/projects/crow-usb-carrier-v1/03_src/rebuild_all.sh")
NEW = Path("/tmp/crow-adc65-conductor-backtrack/projects/crow-usb-carrier-v1/03_src/rebuild_all.sh")
REF = "C_ADC_3V3X_OK_VDD"


def positions(path):
    text = path.read_text()
    return {
        "module": text.index('"$S/module_first_check.py"'),
        "generate": text.index('cp "03_tscircuit/dist/src/$TSX/circuit.json" "$CJ"'),
        "diagnostics": text.index('"$S/circuit_json_diagnostics.py" "$CJ"'),
        "render": text.index('render_schematic_pdf.mjs'),
        "checkpoint": text.index('"$S/stage_checkpoint.py" record . schematic'),
    }


def simulate(module_before_generate, generated_refs):
    circuit = {"refs": ["C_ADC_DIGITAL_OK"]}

    def module_check():
        return REF in circuit["refs"]

    if module_before_generate and not module_check():
        return "P-MOD FAIL stale"
    circuit = {"refs": list(generated_refs)}
    if not module_check():
        return "P-MOD FAIL actual-missing"
    return "P-MOD PASS current"


old = positions(OLD)
new = positions(NEW)
assert old["module"] < old["generate"]
assert new["generate"] < new["diagnostics"] < new["module"] < new["render"] < new["checkpoint"]
assert simulate(True, [REF]) == "P-MOD FAIL stale"
assert simulate(False, ["C_ADC_DIGITAL_OK", REF]) == "P-MOD PASS current"
assert simulate(False, ["C_ADC_DIGITAL_OK"]) == "P-MOD FAIL actual-missing"
print(json.dumps({
    "old_order": old,
    "new_order": new,
    "old_new_ref": simulate(True, [REF]),
    "new_new_ref": simulate(False, ["C_ADC_DIGITAL_OK", REF]),
    "new_missing_ref": simulate(False, ["C_ADC_DIGITAL_OK"]),
    "result": "PASS",
}, sort_keys=True))
