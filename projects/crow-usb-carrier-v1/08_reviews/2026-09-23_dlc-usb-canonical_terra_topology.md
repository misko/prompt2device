---
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
subject_raw_sha256: 416d4f78a8ae2e7040c51194d97dee7af424580e4acf8dc0e36d9c7b975a20da
subject_semantic_sha256: eb861a22f82ac97aa3f64be3070dc86bc125044e48618223ca39d94b1328cfe4
circuit_json_sha256: 416d4f78a8ae2e7040c51194d97dee7af424580e4acf8dc0e36d9c7b975a20da
schematic_pdf_sha256: 772cb0faee20406f1a398f30f0cf15f6bd08bb90207e2d6fdd8b2a062d38d0cd
netlist_sha256: efee66262e060ac952371d67435925a3b3c6786851b2117531ab5f040c1fa830
parts_sha256: 94417f2eb2803309b2a1f7cb9d5135846f8e26090577842e10b814bb27add50d
design_rules_sha256: de1382bbce85b354017af68a389bd386abf9e90d93f9746a1261c6ca764d54a3
helper_path: /home/mouse9911/gits/circuits/skills/kicad-pcb/scripts/pre_route_review_check.py
helper_sha256: 529db43f5e7a9d21a1884ed8dc60dfa27f9c94ee07e7c853547592dfc524ee6a
---

# Canonical DLC/USB topology review

## Decision: SOUND for the exact schematic topology

The native netlist has 568 component records; the source circuit has 568 components, 282 named source nets, 1,788 source ports, and 1,639 source traces. `U_XU` has all 129 unique pins numbered 1–129. The exact candidate differs from the `cf78…` baseline only in the eleven stated component identities and the three regulator port maps; there are no source-net record changes.

For `U_3V3X`, `U_1V8`, and `U_CORE`, the native source shows TPS62822DLCR pins 1/2/3/4/5/6/7/8 as EN/FB/AGND/NC/PGND/SW/VIN/PG. FB, SW and VIN retain their respective feedback, switch and `N5V_BUCK` nets; AGND and PGND are grounded; NC and unused PG are open. Their 10 uF input parts, 47 uF output parts, 0.47 uH inductors, divider values, sequencing, and loads remain as reviewed design screens. The new 3V3X top resistor is 453 kΩ and preserves the established divider relationship.

`J_USB` is USB4215-03-A without a source-port/net change: VBUS remains isolated to `VBUS_USB` sensing, CC1/CC2 stay separate with Rd, DP/DM remain paired to the XMOS, ground/shield remain grounded, and SBU contacts remain open. The XMOS USB, rails, reset, QSPI and clock port census is unchanged. The source/fault bridge remains intact: `J_PWR -> F_IN -> Q_IN -> N12V_PROTECTED`, all eight branch eFuses, and their ILIM/dVdT networks are outside the delta. Its conditional 2.185 A delivery, 3.4 A episode peak, and 2.85 A/rearm limits remain requirements, not measured behavior.

This verdict is limited to pin/net topology and manufacturer-record pin-map compatibility for the exact candidate. Qualified source/cable fault waveforms, hot fuse/PFET behavior, USB connector mating and SI/RF behavior, capacitor/thermal/startup margins, firmware, placement, routing, board DRC, first article, and ordering remain open. No repin or fault waiver is made.
