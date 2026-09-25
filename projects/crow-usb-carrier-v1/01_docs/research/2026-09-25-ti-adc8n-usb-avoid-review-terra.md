# Independent review: ADC8N USB-avoiding reroute

**Disposition: the local research reroute passes its stated native USB-separation, DRC, endpoint, and filled-return screens. It is not promotable to a source corridor, physical-cell result, P1, or P2.** I reran immutable SOL commit `fd13cef1`'s `reroute_probe.py` under the hash-pinned full TI profile.

The replay confirms 0.20-mm F.Cu geometry, eight segments, and 15.179545-mm centerline length. Full effective trace copper has no intersection with `usb_vbus_sense=[195,62,220,82]`; its minimum measured gap is 0.100001 mm on `(198.0,61.8)->(194.6,61.8)`. The embedded red control also passes: the first local route has one positive full-trace-shape intersection with the rectangle. The native different-net gap remains 0.190001 mm to `C_ADC_CM8N.2`, 0.040001 mm above the 0.150-mm rule.

Full-profile replay reports filled baseline/candidate 199 violations and 499 opens, with violation identities `+0/-0` and zero V-PROCESS failures. All 569 original footprint poses and pad ledgers, including the 27 fixed refs, are preserved. Native connectivity joins exactly `C_ADC_AC8N1.2` and `C_ADC_CM8N.1`; `C_ADC_AC8N2.2` and `U_ADC_B.13` remain unconnected. One GND In1.Cu zone is filled, and the route, both ordinary GND stitches, and the existing ISO8 GND via share filled outline 8; every eight 0.20-mm route-ribbon subtraction is zero uncovered area.

The USB separation should not be confused with a physical-footprint clearance. The limiting y=61.8 horizontal trace has copper from y=61.7 to 61.9. `C_ADC_AC8N1`'s native body is `[195.225,58.325,200.775,61.775]` and its checker physical envelope is `[195.205,58.305,200.795,61.795]`. The segment overlaps that same cap's body/courtyard span from x=195.225 to 198.0 and y=61.7 to 61.775. KiCad's electrical DRC permits copper under its own SMD component body, but this is not an assembly/placement clearance result and reinforces the packet's research-only status.

No source or physical-cell artifact is changed, and the packet has no `edge_attachment`. J8 remains at `(204.0,26.86)` with the existing edge-overhang issue; it earns no mechanical-cell credit. The full ADC8N tree, regional ownership, channel-8 physical cells, broader analog routes/returns, assembly, and connector evidence remain open.

Verification run:

```sh
python3 01_docs/research/2026-09-25-ti-adc8n-usb-avoid-sol/reroute_probe.py
```
