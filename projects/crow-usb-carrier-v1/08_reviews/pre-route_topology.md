# Independent pre-route topology review

review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
usb_esd_electrical_status: PROVISIONAL-UNPROVEN
netlist_sha256: d6f6bb95cb57fb783a27758b7e0f93636c430a99e5d88261873d142aaa0f1094
parts_sha256: 8f7742744fdd43c1089176e27316ebc3995556d295140ceb06586d98c62d45d8
design_rules_sha256: c5f9432e8640b78c5fdc1425b4cb04095a9d97cd0d7b83a6bef01fe27c33fc31

I independently reviewed the fresh KiCad electrical netlist, selected-part
source, and semantic design rules for the provisional U_USB_ESD change. The
schematic-stage checkpoint verifies 7/7 pinned files. This verdict concerns
connectivity and source-stage ratings; it does not approve the delivered
schematic's readability or any board geometry.

## Electrical delta and USB protection

I exported the preceding tracked KiCad schematic to a separate netlist and
compared its native component and `ref.pad -> net` maps with the current
netlist. Both contain 569 components, 1,787 physical pin assignments and 428
nets. No component reference was added or removed, and no pad-to-net tuple
changed. The only component identity/footprint delta is U_USB_ESD:
TI TPD2EUSB30ADRTR/DRT-3 became Nexperia PESD2USB3UV-TR/SOT23. Its pins
remain 1=USB_DP, 2=USB_DN, 3=GND. The current USB_DP net joins J_USB A6/B6,
U_USB_ESD.1, and U_XU.60; USB_DN joins J_USB A7/B7, U_USB_ESD.2, and
U_XU.59. The reversible contacts do not cross or short together. VBUS_USB,
CC1/CC2 terminations and their separate protection remain on their preceding
nets. The route topology also declares the new device as a two-line shunt,
with protected pads 1/2 and return pad 3.

I checked that assignment against the retained [Nexperia PESD2USB3UV-T
primary datasheet](https://assets.nexperia.com/documents/data-sheet/PESD2USB3UV-T.pdf),
Table 2: pads 1/2 are individual cathodes, pad 3 is the common anode. The manufacturer lists this part for USB2.0, but its 3.3-V reverse
standoff is below Crow's 3.394-V worst-case N3V3X DC setpoint and 3.60-V
XU316 USB_VDD33 at-pin ceiling. Those are supply limits, not demonstrated
D+/D- high or idle voltages. The XMOS primary used here does not state a
worst-case USB line high/idle voltage, so the DC leakage margin is
**PROVISIONAL/UNPROVEN**, not an electrical drop-in finding. No known DC
incompatibility has been demonstrated either. Closing this selection requires
an authoritative worst-case line level no higher than 3.3 V, or a protector
with reverse standoff at least as high as the transmitter maximum (3.60 V
under the conservative rail ceiling), before electrical acceptance.

The 4.2-8-V breakdown range and 0.83-pF typical/1.0-pF maximum capacitance
differ materially from the former TI selection. A typical TLP clamp value
cannot establish XU316 powered or unpowered pin survival. Realized USB
high-speed eye/insertion loss, the low-inductance ground return, and
transient coordination remain separate open qualifications. The selected
pin graph is coherent, which is the limited basis for this topology SOUND
verdict; it does not certify the provisional protection device electrically.

## Unchanged circuit and scope

The complete pad-net comparison preserves the external-input fuse and reverse
protection, the protected 12-V trunk and eight spoke branches, the converter
and bypass rail domains, supervisors and held-domain clock inhibit, ADC
clock/data interfaces, and flash QSPI pins. The power-tree edit changes only
the strict source-circuit fingerprint after the part swap; it does not author
a new physical power connection or relax its conditional external-source and
fault obligations. The fresh electrical checks report zero ERC errors and
9/9 closure; these support the reviewed netlist, not PCB realization.

This SOUND verdict is limited to pre-route topology and source-stage ratings.
The current review does not grant connector FULL, P1/P2/P3, USB transient or
signal-integrity qualification, 3D model registration, fabrication, or JLC
assembly allocation. The exact U_USB_ESD model and route/return remain owed;
source-selected part stock is not a purchase allocation. The prior accepted
route contract still names the TI part and must be reviewed afresh. The
purchase hold remains DO-NOT-ORDER.
