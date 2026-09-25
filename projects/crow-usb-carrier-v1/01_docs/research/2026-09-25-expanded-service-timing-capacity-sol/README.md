# Expanded locked P1 service and timing aperture screen

**Read-only result: P1 capacity remains INCOMPLETE.** This screens only
`xmos_service_escape` and `adc_timing_xmos_bundle` on the expanded 7628G board.
It neither changes the candidate nor promotes the coarse `INCOMPLETE` receipt.
The exact source declares 13 service nets/33 F.Cu native terminals and 14
timing nets/54 F.Cu native terminals; the script checks every ref.pad/net and
rejects a missing or duplicate member. The four timing crossings are
`AUDIO_MCLK_1V8`, `TDM_BCLK_1V8`, `TDM_DATA_1V8`, and `TDM_FSYNC_1V8`, each
with one translator and one XU pad. The service denominator includes six QSPI
nets, four JTAG nets, two XTAL nets, and the five-terminal `XU_RESET_N` tree.

Inputs, all SHA-256: board `fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`;
P1 source `e8ff456de1868386890dbb5413bb20dc054b5d711b7c9b97d8b02a6b4695ae92`;
floorplan `8a805d92d4f57c3a0db00a45d1c9aef57958eb0c219d44f9ca89e5531021d8b4`;
coarse contract `9faaed39333c0db45c188003d2ac6bacc69562f259f8332d0d6a79db7d25037f`;
modular plan `02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8`;
KiCad project rules `7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094`;
custom rules `00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a`.
The maintained capacity helper is `fdbf97c70a105205423a7b4430f584344346a2250ddb63a0f71260e7cb284dd0`.
The board is the existing ignored private diagnostic at
`06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb`.
It has 14 existing native vias and no routed service or timing trace. The
maintained packet reports zero native DRC violations and 499 unrouted items;
those counts are inherited, not rerun here.

The script projects each native F.Cu pad's `GetEffectiveShape(F.Cu)` and each
component body envelope to conservative rectangles, includes existing copper,
then expands obstacles by the Default clearance 0.15 mm. It reserves 0.15 mm
at each tested window edge. For an aperture *W*, the straight parallel-trace
count is `floor((W + 0.15)/(0.20 + 0.15))`; 0.20 mm is the Default track width,
while the project's absolute minimum is 0.15 mm. None of these named nets
matches a non-Default netclass or a custom width rule. Rectangle projection
can understate irregular free space. A count is a local geometric aperture,
not a pad-entry, electrical, filled-return, or four-net route proof.

| F.Cu cross-section (mm) | After obstacle/edge clearance | Default traces / demand | P1 meaning |
| --- | ---: | ---: | --- |
| QSPI `[219.2,110.5,223.2,118.5]`, vertical | 3.70 mm | 11 / 6 | Trunk free; narrow authored face is 3.55 mm (9-trace nominal capacity). |
| JTAG `[221,65,226,84]`, vertical | 4.70 mm | 13 / 4 | Trunk free; XU-side face is 2.80 mm (7-trace nominal capacity). |
| XTAL `[217.2,107,218.95,110.5]`, vertical | 1.45 mm | 4 / 2 | Handoff free; south face is 1.45 mm (3-trace nominal capacity). |
| TDM→XU direct `[182.475,94,199.825,100]`, horizontal | 1.53 mm | 4 / 4 | C_XU_VDDIO_109 and C_XU_VDD_104/105/106/113 split the band; its limiting native slice is near x=195.50 mm. No typed allocation. |
| Alternate boundary neck `[188,94,190,99.84]`, horizontal | 5.54 mm | 16 / 4 | Short local neck only; no source ownership or complete path. |

The three named service trunks have no native F.Cu obstacle or other authored
reservation overlap in their interiors. Their face spans and both 0.15-mm
edge margins were measured separately; these nominal face counts also omit
pad-to-face escape. All four *authored* fixed-JTAG access chains consist of
four or five segments with a 0.15-mm narrowest segment. They are source
reservations, **not native copper tracks**. Since a Default trace is 0.20 mm,
none proves an effective fixed-pad connection under the current rules.
The reset tree has five validated native endpoints but `geometry: null` and
no reserved branch capacity. Thus the 6/4/2 free trunk apertures cannot
establish a complete 13-net service capacity lower bound.

The direct timing band improves on the older 1.515-mm/three-slot result from
a different board; its 1.53-mm cleared aperture fits four 0.20-mm traces and
three 0.15-mm internal gaps exactly at this local bottleneck. The current
four translator pads are on its west side, while XU DATA is on XU's west edge
and the other three XU pads are on its south edge. The source still represents
all 14 timing nets as geometry-free branches/crossings, so neither the direct
band nor the alternate neck is a typed, nonoverlapping P1 reservation. The
earlier three-mouth obstruction and local-neck probes used other board hashes
and cannot establish these pad entrances. Coupled P2 placement must establish
actual pad access and bypass placement; P3 must establish connected routes,
timing and filled In1.Cu return. An independent D11 P1 review must first
decide whether the current source can reserve the needed complete corridors.

Reproduce from the worktree root with KiCad 10 `pcbnew` and PyYAML:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-expanded-service-timing-capacity-sol/measure.py > /tmp/crow-expanded-service-timing-capacity.json
cmp /tmp/crow-expanded-service-timing-capacity.json projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-expanded-service-timing-capacity-sol/measurement.json
```

The script hard checks all input hashes, native pad/net identities, netclass
assumptions, and denominators before writing JSON. It performs no route,
refill, DRC, source edit, or receipt relabel.
