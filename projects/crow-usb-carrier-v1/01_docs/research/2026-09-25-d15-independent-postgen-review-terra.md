# D15 independent post-generation review — FAILED_RESEARCH confirmed

**Signed review: Terra, 2026-09-25.** I reran the post-generation verifier:

```sh
/usr/bin/python3 01_docs/research/2026-09-25-d15-postgen-sol/verify_postgen.py
```

It returned `D15_POSTGEN_FAILED_RESEARCH_RECEIPT_VERIFIED`. The receipt and
current private artifacts bind one actual generation, no retry, and
`FAILED_RESEARCH`; all lifecycle credit fields remain false.

The only V-PROCESS finding is `TMUX-DRU: foreign clearance/via/hole
constraint`. It is caused by the unchanged TMUX checker treating D15's exact,
area-bounded USB_DP/USB_DN 0.100-mm clearance rule as foreign. This is a gate
failure even though the rule is TMUX-disjoint. It must not be repaired or
rerun under consumed D15 authority.

The verifier reran the native object audit. It reports no footprint/pad pose
or identity delta, no track/via or existing zone/outline delta, and exactly one
new F.Cu rule area, `usb_pair_xu_launch`. The saved candidate has 14 original
GND vias, nine rule areas, one copper zone, and no saved zone fill. The
post-generation files are limited to the private KiCad sidecars, V-PROCESS JSON
and disposable DRC JSON; no board fabrication export was created.

The hash-bound disposable native DRC report has zero violations, 499
unconnected items, and zero performed schematic-parity issues. The receipt
records count parity 569/569 and pin-map parity over 799 physical identities.
These clean checks do not override V-PROCESS and confer no routing,
Connector FULL, fabrication, release, or order credit.
