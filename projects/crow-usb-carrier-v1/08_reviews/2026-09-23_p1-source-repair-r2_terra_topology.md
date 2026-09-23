---
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
circuit_json_sha256: 2b9a33b6473029138362253c48a28406138221e2dbf28907fb1a6f5a3dfd5410
netlist_sha256: efee66262e060ac952371d67435925a3b3c6786851b2117531ab5f040c1fa830
parts_sha256: 833913d1c3d68cec43ab53f34e63b48cbf0e38bd3ec5a5115abfbaa5e23c2a0e
design_rules_sha256: 2faf5c5a8401ff38720973129bd02e716cb66cedef44e64dc01b2948dbf0e1ad
helper_path: /home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/skills/kicad-pcb/scripts/pre_route_review_check.py
helper_sha256: b02a6d97feef2436ba71053e676d87e04c726b1ceec92cd92cf8a4b5d25c6b4e
---

# Fresh topology carryover

The exact current native schematic and Circuit JSON are byte-identical to accepted 106ace85, and the authoritative helper yields the current canonical netlist digest above. The changed parts digest binds layout contracts only; no component, pin, net, endpoint, value, or electrical source fact changes. Fresh topology carryover is therefore SOUND. ERC still has 0 errors and 4,216 warnings; this warning debt is retained, not waived. DO-NOT-ORDER.
