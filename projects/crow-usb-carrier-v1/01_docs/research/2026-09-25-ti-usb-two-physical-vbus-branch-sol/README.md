# Two-physical USB path with unresolved VBUS trees

**Isolated research packet; P1 remains INCOMPLETE.** `build_trial.py` copies
the exact two-physical DP/DN source packet, retaining the TI unrouted board
SHA-256 `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`,
the original floorplan and modular interface bytes, and the authoritative
`USB4215-03-A/part.yaml` aliases. It changes no canonical board, source,
checker, stock, route, or review.

The DP/DN linked path remains the only linked path in `usb_device_pair`.
Its edge and frontend-to-XU physical stages retain rough counts of **2/2**
and **3/2** slots respectively, exact endpoint joins, P2 pad/face obligations,
and filled-return debt. The whole path has null capacity and no realized
route. The former `vbus_entry` and `vbus_sense_entry` ordinary VBUS claims
are removed so they cannot duplicate capacity.

The source instead declares `vbus_unplaced_tree` as one geometry-free
`unresolved_multiterminal_branch`: all **8/8** source/native endpoints under
`usb_edge_connector`, `usb_frontend`, and `usb_vbus_sense`; exact alias
`J_USB.2→A4`, `J_USB.15→B9`, `J_USB.10→B4`, and `J_USB.7→A9`; one P2
pad-to-tree duty for each endpoint; an In1.Cu filled-return duty; and a P3
connected-tree duty with eight terminals and a seven-edge lower bound.
`capacity_slots` is null and no branch bbox exists. One exact A4 native-pad
witness represents the branch in the coarse contract. The original
`VBUS_PRESENT_N` three endpoints remain exact; its two failing movable-pad
witnesses/reservations are similarly replaced by `presence_unplaced_tree`
with **3/3** endpoints, P2 return/P3 tree duties, and null capacity. Its
representative witness is the exact native `Q_VBUS.3` pad.

The full hash-bound checker run with `--diagnose-all` reports **INCOMPLETE**,
**zero global errors**, **zero USB diagnostics**, and `usb_device_pair`
**INCOMPLETE** with no local reason. Its USB allocation has exactly the two
geometry-free power/control branch reservations plus the single DP/DN linked
path. The other three incomplete allocation families still have independent
legacy witness debt: first reasons `U_ADC_A.22`, `C_ADC_AC1N1.2`, and
`C_ADC_3V3X_OK_VDD.2`; the full result preserves 41 non-USB independent
diagnostics. `p1_accepted` is false.

The checker/source/contract/result SHA-256 values are respectively
`2cdd5a2dc58680409391f89f8619a564c2de0b591aa27618d665dfe9a1797e8e`,
`be824e24fc0b0e165cd9ca2d1623dddaac40ce72ce2dc9775b675c498ad1e385`,
`69d4f615a845f5eb1f4ad765614a7c6b1c8fbe98f172cb925cdbbca06ff179ca`,
and `09db23818bfd94078995b5048d7f98fed04209f9df963071adb2e070dd4fa4f6`.
The builder pins all six starting authorities and fails if the resulting
status, USB denominator, null capacity, or zero-USB-diagnostics condition
drifts. Reproduce from the repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-usb-two-physical-vbus-branch-sol/build_trial.py
```

This is a complete accounting of the present source debt, not a VBUS route,
current/thermal rating, filled return, DP/DN SI proof, connector qualification,
P1 acceptance, or order authority. The earlier wide VBUS edge strip still
hits native `U_USB_CC_ESD`, and the fused A4/B9 and B4/A9 contacts still need
physical launch authority before a geometric power claim can be made.
