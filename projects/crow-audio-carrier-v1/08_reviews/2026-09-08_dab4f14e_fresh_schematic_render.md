# Independent exact-PDF schematic review

subject: crow-audio-carrier-v1 dab4f14efb780fbaf10cf7eca8fe47e6b829e3f4  
date: 2026-09-08  
reviewer: fresh-context agent, schematic_render lens  
context-given: exact-source-and-primary-documents, no prior reviews  
source_commit: dab4f14efb780fbaf10cf7eca8fe47e6b829e3f4  
review_stage: pre-route  
review_kind: schematic_render  
design_verdict: DEFECTIVE  
order_verdict: DO-NOT-ORDER  
netlist_sha256: f7586bb09e54b2db8e305a66670cc9e09468e32b52336e85d1b1d02f5935ada0  
parts_sha256: da40483f53767ef34e8d0b561eea11d36e6bc6c10162dcae50a9078cf5373e0d  
design_rules_sha256: 14603bc34e244ce702e97a3b14251090eeb88377107e26293fb6ace4d1d26fd9  
schematic_pdf_sha256: 603eda5f0505d66fd0a71c9b5b920a9ba15f5773d0f6bbc4c5da1d4909d6aad9  
review_completion: COMPLETE  
envelope_sha256: f35b146d8f75aee2ce6e20d8bc652c5e8547d3b3ea9885d047b92da769e90df7  
input_packet_sha256: 90c2736f5e7d6e40aa14c21ba9593f7459d56ca955b28a3a1cfab7478d23a952  

## Verdict

The integrated PDF is judgeable but does not pass schematic presentation review. Its functional organization is useful, all 299 component references are present, and every delivered page was actually viewed. However, page 19 visually joins two reset-strapping nets that the exact netlist keeps separate. Additional localized label, NC-endpoint, and symbol-body collisions remain.

These are findings about the delivered drawing. **This review does not allege that the native netlist contains the depicted shorts.**

## Scope, method, and clocks

Reviewed artifact: [exact delivered schematic PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_tscircuit/build/schematic.pdf).

I read the complete `pcb-design` and `kicad-pcb` skills; the selected execution-graph, execution-runtime, review-and-publication, tscircuit-folder, and schematic-generation procedures; and the project's `08_reviews/contracts.md`. I used the authored architecture and exact Circuit JSON/netlist to resolve drawing ambiguity. No earlier project reviews, source-correction reports, adjacent topology-packet contents, or prior reviewer reasoning were read.

Actual UTC clocks:

| Event | Clock |
|---|---|
| First recorded reviewer clock | 2026-09-08T01:05:18Z |
| Before-work identity verification | 2026-09-08T01:07:19Z |
| All 19 full-page views completed | 2026-09-08T01:08:41Z |
| Final detail/NC coverage checkpoint | 2026-09-08T01:13:54Z |
| After-work verification started | 2026-09-08T01:15:06.087424Z |
| After-work verification completed | 2026-09-08T01:15:06.219431Z |
| Commission deadline | 2026-09-08T01:22:12Z |

Each page was rasterized directly from the bound PDF and viewed individually at 96 dpi: 1200 × 810 pixels for the 18 landscape pages, and 810 × 1200 for portrait page 4. The PDF's actual page dimensions are 900 × 607.5 points, reversed on page 4. Detail views used 192–384 dpi. No physical print was inspected, and zoom crops were not substituted for full-page viewing.

## Findings

### SR-01 — P0 — Reset inputs A and B are drawn as one conductor

**Page 19, U_RST2 pins 1/A and 2/B, immediately left of the symbol.**

The green routes from these two pins form an apparently continuous vertical stem. Their separate destinations are also obscured where the routes pass behind the symbol body. The delivered drawing therefore does not clearly communicate the essential opposite reset straps.

The exact netlist establishes:

- `U_RST2.1` and `U_RST2.4` are on `GND`.
- `U_RST2.2` and `U_RST2.8` are on `3V3_ADC`.

The Circuit JSON independently explains the visual defect: `schematic_trace_245` uses a vertical segment at x = −1.52, while `schematic_trace_247` uses x = −1.53. Their overlapping y interval includes 0.8–1.0. These are distinct centerlines, but their rendered ink is not visibly separated, including in the 384-dpi inspection.

This is a **schematic-acceptance-blocking false connection**, not evidence of a native GND/3.3 V short.

Required source-level correction: separate both routes with a visible ink gap and keep them outside the symbol body. Do not “resolve” the ambiguity by adding a junction dot. Regenerate and review the complete resulting PDF.

Evidence: [page 19 reset-strapping detail](/tmp/carrier-render-dab4f14e.nL1IzL/detail19left-19.png).

### SR-02 — P1 — Foreign wires cross supply-label plates in nine locations

**Pages 6–13, U_AFE1–U_AFE8; page 4, U_AUDIO.**

On every channel page, the vertical `FB_Pn` feedback wire passes through the `5V_OPA` label plate and lettering above the amplifier's positive input. All eight occurrences were individually inspected at enlarged scale as well as on their complete pages.

The exact netlist keeps each `U_AFEn.2` on `FB_Pn`, while `U_AFEn.8` is on `5V_OPA`. The drawing overlays those separate identities.

On page 4, the `PWR_EN` route to `U_AUDIO.3` similarly passes through the `5V_LDO_HOLD` label plate supplying `U_AUDIO.4`.

Required source-level correction: move the affected label attachments or route the foreign wires around their complete plate/text envelopes.

Evidence: [channel 1 example](/tmp/carrier-render-dab4f14e.nL1IzL/detail6-06.png), [page 4 U_AUDIO detail](/tmp/carrier-render-dab4f14e.nL1IzL/detail4audio-04.png). Separate confirmation crops for all eight channels are retained as `afe-label-06.png` through `afe-label-13.png` in the same temporary directory.

### SR-03 — P1 — An intentional NC endpoint touches a signal-label border

**Page 18, U_OE pin 1/NC and the `TDM_SENSE_G` label.**

The pin-1 open endpoint coincides with the lower-right corner of the `TDM_SENSE_G` label plate. This visually couples an intentional NC to the input-net label beside pin 2.

The exact netlist instead places `U_OE.1` on `unconnected-(U_OE-NC-Pad1)` with `passive+no_connect`, and `U_OE.2` on `TDM_SENSE_G`.

Required source-level correction: move the label or change the local input routing so the complete NC stub and endpoint have clear separation.

Evidence: [page 18 U_OE detail](/tmp/carrier-render-dab4f14e.nL1IzL/detail18-18.png).

### SR-04 — P1 — Reset timing and pulse labels touch across separate nets

**Page 19, below/right of U_RST2, `RESET_RC` and `RESET_PULSE_H`.**

The bottom of the vertical `RESET_RC` plate lies against the separate `RESET_PULSE_H` conductor; the horizontal pulse-label tip also touches its lower-left corner. This is a label/conductor collision, not an ordinary dotless crossing.

The exact netlist distinguishes:

- `RESET_RC`: `C_RST_T.2`, `R_RST_T.2`, `U_RST2.7`.
- `RESET_PULSE_H`: `Q_RST1.1`, `R_RESET_GPD.1`, `U_RST2.5`.

Required source-level correction: reposition the timing label or its attachment so both complete label envelopes and the pulse conductor remain separate.

Evidence: [page 19 timing/pulse detail](/tmp/carrier-render-dab4f14e.nL1IzL/detail19-19.png).

### SR-05 — P1 — Supervisor MR_N connection disappears beneath its symbol

**Page 4, U_PWR pin 3/MR_N and the `5V_LDO_HOLD` connection.**

The MR_N route enters the left/top region of the filled U_PWR body away from a pin and disappears underneath it. The visible route therefore fails to show its complete connection to the supply branch.

The exact netlist places both `U_PWR.3` and `U_PWR.4` on `5V_LDO_HOLD`; the problem is hidden drawing continuity, not their electrical assignment.

Required source-level correction: route this tie outside the symbol body or provide an unobscured local supply attachment at MR_N.

Evidence: [page 4 U_PWR detail](/tmp/carrier-render-dab4f14e.nL1IzL/detail4-04.png).

## Complete page coverage

Every row below represents an actual full-page image view. Component counts were additionally checked by matching exact source-component reference names against extracted PDF text; this inventory check was not substituted for visual inspection.

| Page | Function | Component references | Observation |
|---:|---|---:|---|
| 1 | Input fuse, reverse polarity, clamp | 9 | Primary entry/protection path traceable |
| 2 | Buck, raw hold-up, analog bead | 9 | Regulation and branch flow traceable |
| 3 | Precharge, held energy, ADC LDO | 17 | Support network visible; selected crossings enlarged |
| 4 | Rail supervision/audio enable | 14 | SR-02 and SR-05 |
| 5 | Delayed enable, discharge, held logic | 10 | Flow and local bypass ownership visible |
| 6 | Channel 1 | 22 | SR-02 |
| 7 | Channel 2 | 22 | SR-02 |
| 8 | Channel 3 | 22 | SR-02 |
| 9 | Channel 4 | 22 | SR-02 |
| 10 | Channel 5 | 22 | SR-02 |
| 11 | Channel 6 | 22 | SR-02 |
| 12 | Channel 7 | 22 | SR-02 |
| 13 | Channel 8 | 22 | SR-02 |
| 14 | CS5308P, hardware straps, bypass | 12 | Grouped pins/identities visible; dense pin field enlarged |
| 15 | External VMID dividers/followers | 14 | Divider, follower, isolation and polarity visible |
| 16 | ADC VMID/reference filter banks | 12 | Independent banks and returns traceable |
| 17 | MCHStreamer clocks/termination | 9 | Clock flow and NC bank inspected |
| 18 | TDM return/presence/output enable | 8 | SR-03 |
| 19 | Power-on reset sequence | 9 | SR-01 and SR-04 |
| **Total** | **19/19 pages** | **299/299** | **No missing reference names** |

Additional coverage:

- All eight complete analog channels were inspected, including coupling, bias, feedback, series outputs, differential capacitor, isolation switch, ADC-side support and local bypass.
- The exact netlist contains **40 intentional NC nodes**. Their NC-named pin presentations were inspected on the relevant pages; SR-03 identifies the collided endpoint.
- No cropped page content or general page-occupancy failure was observed.
- Important active identities and local support ownership are visible. The densest pin-number detail is on page 14 and benefits from enlargement.
- Ordinary through-crossings and the visible hop-overs inspected on pages 3, 6, 17 and 19 were not automatically treated as connections or findings.

## Identity and read-only verification

Before and after the visual work:

- The repository's strict `TaskEnvelope` parser accepted the envelope, and its canonical digest matched the commission.
- **4/4 packet files** matched their declared sizes and hashes.
- The canonical ordered packet-list digest matched the declared handoff ID.
- **368/368 census files** matched their frozen sizes and hashes; **zero drift** was detected.
- **7/7 subject digests** matched independently, using `pre_route_review_check.py` normalization/digest functions and its exact parts-digest construction.
- The parts digest covered **77 part dossiers**.

Additional verified subject identities:

| Subject | SHA-256 |
|---|---|
| Raw netlist | `bcee73d163d05ce806a91280ded1eabdae1d063bc3721f1bbfb366c8f5adcc03` |
| Native schematic | `104bdbfa2f409cf418651608798f202494b4638b2f023f3ae1b499e7471f8130` |
| Circuit JSON | `9e21d2e62649a45220f72c34232bd829d5bf8f9a5df0b57b59f9e5885ae7649c` |

Administrative HEAD remained `aa50552cd6266a8de830b3ab9a713a117a0c6a7a`. The committed delta from the source subject contained commission additions only. The two pre-existing dirty coordination paths, `STATUS.md` and `journal/schematic.md`, remained outside the frozen census; their contents were not read or changed by this reviewer.

No repository files were written. Only temporary PDF rasterizations under `/tmp/carrier-render-dab4f14e.nL1IzL/` were created. They remain available for coordinator archival; the bound PDF and page/reference descriptions remain the primary evidence. No TaskAttempt or token telemetry was invented.

## Exclusions and unresolved work

This completed lens does not grade electrical ratings calculations, independent datasheet pinout derivation, PCB placement, copper, routing, physical mating, manufacturing, allocation, accounts, ordering, or first-article qualification. No conductor, PCB operation, external account action, or delegation was performed.

The five findings remain unresolved because the commission is read-only. Source correction, regeneration, fresh exact-subject presentation review, and any required topology-equivalence rebind remain coordinator-owned follow-up. This witness grants no placement, routing, release, or order permission.
