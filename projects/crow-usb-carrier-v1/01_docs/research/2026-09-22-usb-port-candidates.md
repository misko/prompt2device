# USB port candidates — 2026-09-22

Status: candidate research; no part or pin netlist frozen. The USB bridge
selection remains a separate Sol task.

The GCT USB4105 series is an active, top-mounted, horizontal USB2 Type-C
receptacle with 16 contacts, SMT signal pins and through-hole shell stakes.
The vendor lists a 3.31 mm profile, 7.35 mm body length and multiple shell-stake
lengths. Exact suffix, drawing revision, PCB thickness/stake interaction and
supported cable need selection before a footprint can be adopted. Its connector
power rating does not authorize USB power delivery from this board.
Source: [GCT product page](https://gct.co/connector/usb4105), accessed2026-09-22.
A local KiCad footprint candidate exists at
`Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`;
its presence is not independent pin/land-pattern verification.

TI TPD2EUSB30A is a candidate low-capacitance passive two-line data ESD array.
The manufacturer datasheet Rev.G identifies the DRT3-pin mapping as1=D+,
2=D-,3=GND; operating range0–3.6 V, absolute DC limit4 V, typical0.7 pF.
Consequently it is a data-line candidate, not a5 V VBUS or CC clamp.
Layout must follow the datasheet's connector-to-protection path and short
return guidance; package size and nominal capacitance do not prove USB signal
integrity or IEC protection at the assembled port.
Source: [TI datasheet](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf),
pages3–5 and11–13, accessed2026-09-22.

Before selection, obtain exact MPN/PCBA availability, pinned drawing/datasheet
bytes, authorized-pool sourcing and matched footprint/model evidence. Recheck
protection against the chosen USB PHY and complete VBUS/CC/shield strategy.
Neither candidate closes connector mating, assembly or electrical acceptance.
