# ADC7 four-part source silkscreen probe — 2026-09-25

The isolated floorplan overlay adds the four poses from `d7a47c93` to
`placement.post_anchors` and prepends `R_ADC_PD7N` to
`silk.refdes.priority_refs`. Running the existing native board, rules, and
TMUX POFV producers yields **zero DRC violations**, down from the four-part
board's 15 silkscreen-only warnings. The 12 reference fields directly involved
in those warnings, plus `R_ADC_PD7N` (whose footprint and pad were involved),
remain visible on `F.SilkS`. No board-only reference-field patch is involved.

Reproduce from the worktree root with:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc7-source-silk-probe-sol/probe.py
```

The script copies the diagnostic source packet to a temporary directory,
applies [`source_overlay.json`](source_overlay.json), runs
`generate_board_generic.py`, `generate_rules_generic.py`,
`generate_tmux4827_pofv.py`, and native `kicad-cli pcb drc --severity-all
--refill-zones`. It verifies all 569 footprint poses and pad/net/layer
identities against the exact four-part board, which includes all 27 P1 fixed
refs. The generated instance is [`candidate.kicad_pcb`](candidate.kicad_pcb);
its hashes and checks are in [`receipt.json`](receipt.json). KiCad generator
UUIDs vary between runs, so the board file SHA is an instance receipt rather
than an expected reproducible byte-for-byte hash.

This is **not yet a clean assembly-label arrangement**. The generator reports
11 of those 13 visible labels closer to another footprint than their own, with
no owned slot in its 4×84 offset search. The worst cases include `C_ADC_CM7N`
(11.31 mm to itself, 2.06 mm to `R_IN7N`), `C_ADC_CLOCK_OK` (9.20 mm versus
3.71 mm to `R_IN7N`), and `R_TDM_OE_PU` (11.31 mm versus 6.04 mm to
`U_TDM_XLATE`). The complete inventory is in the receipt. Source priority
fixes DRC collision, but placement or label-rule redesign is still needed for
unambiguous assembly reading. The board also retains 499 unconnected items;
no P1 or P2 placement acceptance is claimed.
