#!/usr/bin/env python3
"""Generate the reduced Circuit JSON from its editable component source."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
source = json.loads((root / "03_tscircuit/src/components.json").read_text())
out = []
for index, item in enumerate(source):
    cid = f"source_component_{index}"
    code = item.get("jlc")
    out.append({
        "type": "source_component", "source_component_id": cid,
        "name": item["ref"], "manufacturer_part_number": item["mpn"],
        "supplier_part_numbers": {"jlcpcb": [code] if code else []},
    })
    for pin in item["pins"]:
        out.append({
            "type": "source_port", "source_component_id": cid,
            "source_port_id": f"{cid}_p{pin}", "pin_number": int(pin),
            "name": f"P{pin}", "port_hints": [f"pin{pin}", pin],
        })
target = root / "03_tscircuit/build/circuit.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
