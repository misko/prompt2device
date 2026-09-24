# IC reference semantic review — 2026-09-24

**Verdict: approved for IC-reference record semantics only.** This review approves neither P1 placement, routed copper, impedance/return geometry, SI, fabrication, release, nor order.

I independently evaluated the current `03_src/rules/ic_reference_research.yaml` against the source-declared netlist, the selected component/dossier pin maps, and retained inspection artifacts. The source census is 69 selected instances in 24 exact-MPN/package records; every instance appears exactly once. All 48 inspected artifact/fallback records name local files whose SHA-256 matches the recorded inspection hash. No remote/EVM URL is represented as locally inspected.

For all 69 applications, each `critical_pins_or_nets` item is either a current connected net or an exact connected `REF.pad` from the source netlist. The recorded applicability snapshots bind the current circuit, stackup, and route-rule digests. Modes are per-instance labels rather than a shared fabricated mode. All applications remain `limited`: their reasons correctly retain final Crow placement, return, and route geometry as unproved.

I checked the high-risk rows against their local manufacturer PDFs and dossier pin maps. XMOS `U_XU.59/.60` correctly name USB_DN/USB_DP and retain the USB supply pins; the retained XM-014532-PC contains USB PHY and PCB-layout-checklist material. TPSM63603 `U_BUCK` separates VIN/PGND/VOUT from FB `.25` and AGND `.24`; SLVSFS5A contains §10 layout guidance. LT3045 `U_LDO` correctly distinguishes IN `.1`, OUTS `.9`, OUT `.10`, SET `.7`, and GND `.8`; the retained Rev.D covers SET bypass/layout. Both TLV320ADC6140 rows use AVDD/AREG/VREF/AVSS and TDM pins; SBAS992A §11 contains the cited layout guidance. TPS62822 rows use VIN `.7`, PGND `.5`, SW `.6`, and FB `.2`. All eight TMUX4827 rows use VDD `.8`, GND `.5`, SEL `.2`, and the actual analog pins.

This is evidence-record review only. The tier-2 routed reference/EVM artifacts remain uninspected where stated, and the report does not promote the tier-1 documents into a native layout result.
