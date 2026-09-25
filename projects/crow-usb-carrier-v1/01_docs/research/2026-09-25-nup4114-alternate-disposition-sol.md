# NUP4114 alternate USB protector screen — 2026-09-25 UTC

**Disposition: research candidate only; retain Crow's locked TI selection and
open `USB-ESD-selection-transient` finding.** The [XMOS multichannel audio
hardware manual](https://www.xmos.com/file/xcore_ai-multichannel-audio-platform-1v1-hardware-manual)
names `NUP4114` on its XU316-1024-TQ128-C24 USB-device schematic and documents
self-powered operation. It does not identify an orderable NUP4114 suffix or
publish powered/rail-off USB-pad transient limits, measured clamp current or
voltage at the XU, or an ESD result transferable to Crow. The XMOS precedent
therefore cannot by itself close `DESIGN_CLEAN`.

The [onsemi NUP4114/D Rev. 8 datasheet](https://www.onsemi.com/download/data-sheet/pdf/nup4114-d.pdf)
lists four I/O pins **1, 3, 4, 6**, ground **2**, and positive reference **5**.
Its application options either connect pin 5 to VCC (directly or through a
recommended 10-kΩ isolation resistor) or leave it unconnected to use the
internal ESD reference. Onsemi lists 5.5-V working reverse voltage, 5.5-V
minimum breakdown at 1 mA, 10-V maximum I/O-to-ground clamp at 1 A, 0.6-pF
maximum I/O-to-ground capacitance at 0 V/1 MHz, ±8-kV IEC contact survival,
and 12-A 8/20-µs pulse current for **pin 5 to pin 2**. That last current is
not an I/O-to-ground clamp guarantee. By comparison, Crow's selected
[TI TPD2EUSB30ADRTR datasheet](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf)
describes two I/O pins plus ground in a three-pin DRT, 3.6-V working voltage,
4.5-V minimum breakdown and an 8-V I/O-to-ground clamp value at 1 A. The
different topologies and test nodes prevent a direct system-protection ranking.

One exact orderable investigation target is **onsemi NUP4114UPXV6T1G / JLC
C74675**, SOT-563. The [exact JLC public part page](https://jlcpcb.com/partdetail/onsemi-NUP4114UPXV6T1G/C74675)
identifies the manufacturer, suffix, package and SMT Economic/Standard PCBA.
`jlcsearch` observed **915** catalog units at **2026-09-25T08:14:57.638360Z**,
above the *initial-candidate* five-board plus 150-extra threshold of **155**
by 760. This is neither reserved allocation nor a recheck of Crow's locked
TI stock decision. The report-only command was:

```text
python3 skills/jlcpcb-fab/scripts/jlcsearch.py discover NUP4114 --out projects/crow-usb-carrier-v1/06_build/research/nup4114_jlcsearch.json --cache-dir projects/crow-usb-carrier-v1/06_build/research/nup4114_jlc_cache --max-requests 4 --timeout 20
```

The ignored report SHA-256 is
`657e8a43ea79ff2bb1e3ab755fdcc0e114a4cdbb3fb053a1755828f61df4f241`;
its recorded public raw-response SHA-256 is
`3bab1a85babd07971b64be47200fba9b0860f3a446985fc27621f666ef8bc414`
from `https://jlcsearch.tscircuit.com/components/list.json?search=NUP4114`.
The exact selected TI dossier SHA-256 is
`091b698cfc5bd7f72766c80388ab1efe3331c025254bedea1d628de6b465a387`.
The unchanged USB frontend TSX source SHA-256 is
`62611f919a9e41d3a13a7f9df91e000761026f6d55719d1c3bccb8623980f477`,
and `jlcsearch.py` SHA-256 is
`057cc1dedb1b1fcaba2db4061d33b41a0c5ce87079fae9a669490dae221aa20d`.
No volatile raw catalog file is promoted here.

Adopting NUP4114 would require a new six-pin source symbol/pin map and
footprint, an explicit pin-5 VBUS/rail-or-NC decision, new U_USB_ESD placement
and connector-to-XU pair/ground-return geometry, updated VBUS and USB source
constraints, native parity, JLC assembly and signal-integrity review. The
VCC-referenced steering path can route positive transient current into that
rail; neither its component ESD rating nor the XMOS reference establishes
safe Crow XU316 pad stress in powered and unpowered states. Exact-board
stress evidence or an authoritative XU pad limit and coordinated clamp bound
remain necessary before release suitability can be accepted.
