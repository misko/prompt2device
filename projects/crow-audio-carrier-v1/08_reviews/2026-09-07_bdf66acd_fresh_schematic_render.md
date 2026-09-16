subject: crow-audio-carrier-v1 bdf66acdc7ce8454615ce53a0551eac781e60a91
date: 2026-09-07
reviewer: fresh-context agent, schematic_render lens
context-given: exact-source-and-primary-documents, no prior reviews
source_commit: bdf66acdc7ce8454615ce53a0551eac781e60a91
review_stage: pre-route
review_kind: schematic_render
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
netlist_sha256: fff1d88ea16195b5f57990597d69a35807ed10d82c34c37ef3af7f1b0d08f9d8
parts_sha256: 140bb54457a95637964e53542708692212d663c2af8dfceec483881565996206
design_rules_sha256: 51006cee26e05e4a3c6554be2ce8e776e99cb57528672e21c706925344ec0c55
schematic_pdf_sha256: d996da549d7881888721a2124562af078bb07a0b562e2037ff103c310ecaf993
task_envelope_sha256: 43e9fb79cf9415d23737e127b2338cf2194d1493f5956ae7ebbf1231cd9ab0de
started_at: 2026-09-07T22:42:07Z
examination_finished_at: 2026-09-07T22:49:32Z
deadline_at: 2026-09-07T22:53:10Z

# Independent schematic-readability witness

The delivered schematic fails human-readability review. All six pages were actually viewed at full-page size and in enlarged detail. The defects are presentation defects; this witness does not declare the underlying electrical design defective.

The repository PCB lifecycle and KiCad schematic procedures governed the exact-artifact binding, ordinary-size review, drawn-path requirements, and separation from order readiness.

## Identity and read-only boundary

MEASURED before and after examination:

- Strict `TaskEnvelope` parsing succeeded, and `pipeline_execution.verify_input_packet` passed **4/4 packet inputs**.
- Canonical envelope digest matched the commissioned digest.
- **7/7 subject hashes** matched: raw and normalized netlist, delivered PDF, native schematic, Circuit JSON, parts, and adopted design rules.
- The frozen census matched **367/367 files**, including byte sizes and SHA-256 values.
- Parts digest covered **77 dossiers**, using the gate’s path-and-byte construction. Netlist normalization and rule hashing used `pre_route_review_check.py`.
- Final worktree status was clean. The coordinator’s metadata-only commits changed HEAD during examination; the frozen input bytes remained unchanged.

No repository/design files were written by this reviewer. Temporary raster outputs were confined to `/tmp/carrier-schematic-render-bdf66acd.P1F3ee/`. No conductor, routing, external coordination, sub-delegation, or prior project reviews were used.

The examination interval was **445 seconds**, calculated from the recorded clocks. This is not canonical TaskAttempt telemetry; token usage is UNKNOWN.

## Coverage and method

The reviewed artifact was the exact [delivered schematic PDF](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_tscircuit/build/schematic.pdf).

MEASURED visual coverage: **6/6 full-page overviews and 6/6 pages with enlarged detail inspection**. Overviews were rendered with a 1400-pixel longest edge. Nine targeted crops were rendered and viewed at 216, 432, or 864 dpi. These were actual PDF rasterizations, not substitute source drawings.

| Page | Function | Components | Detail inspected | Body font sizes* |
|---|---|---:|---|---|
| 1 | Input protection, rails, spoke power, sequencing | 67 | J9/F_IN/Q_IN, D_IN/C_BUCK_IN, U_BUCK/L_BUCK | 1–2 pt |
| 2 | Analog channels 1–4 | 84 | U_AFE1 feedback/filter and U_ISO1 | 1–2 pt |
| 3 | Analog channels 5–8 | 84 | U_AFE5 feedback/filter and U_ISO5 | 1–2 pt |
| 4 | CS5308P mode and supply bypass | 12 | U_ADC pin field, straps, supplies, intentional NCs | 3 pt |
| 5 | VMID buffers and ADC reference filters | 26 | U_AFE9 feedback and VMID output isolation | 2–3 pt |
| 6 | MCHStreamer interface, clocks, TDM, reset | 26 | J10/J11/U_CLK and U_RST1/U_RST2/Q_RST1 | 4 pt |
| **Total** | | **299** | **6/6 pages** | |

\* Supplemental measurement from Poppler XML at `-zoom 1`, whose page dimensions match native PDF points. These are integer-rounded font-size reports, not precise glyph-height measurements. All **2,084 body text objects** were counted, excluding three heading/provenance objects per page.

Text extraction independently found **299/299 source reference names** in the PDF. This establishes presence, not individual visual legibility or electrical correctness. Visual inspection, rather than extraction, determined the verdict.

Page 1 is 607.5 × 900 PDF points; pages 2–6 are 900 × 607.5 points. No physical print test was performed.

## Findings

### SR-01 — P0 — Delivered page fitting makes circuit text unusably small

**Evidence:** Page headings are prominent and readable, while circuit references, values, pin names/numbers, and net labels become miniature marks at full-page viewing size. Pages 1–3 contain body text reported at only 1–2 points. Concrete examples include page 1 `U_BUCK` and `C_BUCK_BST`, page 2 `U_AFE1`, and page 3 `U_AFE5`. Pages 4–6 improve only to approximately 2–4 points.

This is visible in all six overview renders. Enlarging the targeted crops makes those same identities and values readable, confirming a fitting/scale defect rather than absent text. Successful deep zoom does not make the delivered ordinary-size drawing acceptable.

The functional partition is useful, but occupancy is inefficient: page 1 has large blank bands between very small circuits, pages 2–3 reserve broad margins around four miniature channel rows, and page 4 uses a tall ADC pin box with substantial separation from its support parts.

**Bounded correction:** Recompose the authored sheets and renderer fitting around a declared printable text-size floor. Reduce unnecessary spacing, enlarge symbols and their text together, and split crowded functions/channel groups where necessary. Preserve local support ownership and intentional-NC readability. Re-review the resulting delivered PDF at full-page size.

**Acceptance test:** References, values, pin identities and important nets must be readable without deep zoom on every delivered page—not merely recoverable from extracted text.

### SR-02 — P0 — Critical power and signal paths still require label reconstruction

**Evidence:** On page 1, `J9 → F_IN → Q_IN` is presented as separated blocks joined only by `12V_IN` and `12V_FUSED` labels. `U_BUCK.5` and `L_BUCK.1` likewise connect through separate `BUCK_SW` labels rather than a drawn switching path. The long visible wires preferentially depict some ground/feedback branches while the principal power chain is interrupted.

On pages 2–3, the input-bias nodes terminate in labels before the amplifier inputs. The filter/feedback network around `U_AFE1` and `U_AFE5`, and its connection to `U_ISO1`/`U_ISO5`, requires matching `BIAS_*`, `FB_*`, `OPA_*`, and `FILTER*` labels. The components are geographically arranged left-to-right, but the complete primary circuit is not drawn continuously.

On page 6, the clock buffer and its three series terminators are also separated by net-label jumps.

These are story-critical connections, not merely repeated decoupling or global supply attachments. They fail the S6 drawn-path requirement despite the presence of other wires.

**Bounded correction:** Author explicit primary power, analog-filter/feedback, and clock paths. Keep global labels at actual page boundaries and appropriate secondary connections. In particular, draw each analog channel as a complete local buffer/filter/isolation circuit and draw the power-entry/protection/regulation chain continuously.

**Acceptance test:** A reader must be able to follow those paths visually without rebuilding the circuit from repeated labels.

### SR-03 — P0 — Page 1 places a foreign net-label plate over the ground return

**Evidence:** At `D_IN` and `C_BUCK_IN`, the green return from `D_IN.2` passes under the interior of the `12V_PROTECTED` label plate belonging to `C_BUCK_IN.1`. The plate appears inline with the diode’s anode lead, while the ground return descends from within the plate. This remains ambiguous at very high zoom; it is not explained by small text alone.

The location is approximately **x = 298–315 pt, y = 105 pt**, measured from the page’s upper-left origin. The directly viewed evidence is [the enlarged PDF crop](/tmp/carrier-schematic-render-bdf66acd.P1F3ee/p1-din-crossing.png).

The exact netlist resolves the intended distinction:

- `12V_PROTECTED` contains `D_IN.1` and `C_BUCK_IN.1`.
- `GND` contains `D_IN.2` and `C_BUCK_IN.2`.

Thus this finding concerns false visual association, **not a claimed electrical short**.

**Bounded correction:** Reposition or reroute this local circuit in the owning schematic source so the ground return does not enter or pass underneath the unrelated net-label plate. Prefer a clear wired rail with the TVS and input capacitor drawn as separate shunt branches.

**Acceptance test:** The PDF must show the two distinct nets unambiguously at both full-page and detail scale, while preserving the existing intended netlist.

## Other observations and limits

The six functional headings and page numbering are clear. Important active identities are present and readable in enlarged views, including AP63205WU-7, OPA1656IDR, TMUX2821DSGR, CS5308P-DN, and the reset/clock devices.

Intentional-NC names are visible in enlarged examples, including `U_ADC.26–28` and the unused J10/J11 pins. No additional NC electrical defect is asserted. Their ordinary-size usability remains covered by SR-01.

Local support circuits are present, including amplifier bypass/filter parts, ADC supply filtering, VMID feedback, and reset timing components. This review did not establish that every support connection, rating, or timing calculation is correct. No obvious page-edge truncation was observed in the six overview inspections; that is not a geometric proof covering every glyph.

Source references used to resolve drawing meaning were the [authored TSX](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_tscircuit/src/crow_audio_carrier_v1.tsx:305), [exact netlist](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/netlists/crow_audio_carrier_v1.net:25993), and [PDF renderer](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/skills/kicad-pcb/scripts/render_schematic_pdf.mjs:496).

## Disposition and unresolved work

This bounded lens is complete before the deadline. SR-01, SR-02 and SR-03 require upstream presentation corrections, regeneration, and a fresh exact-PDF readability review. No corrections were implemented here.

Excluded: full electrical calculations, independent datasheet pin re-derivation, PCB placement/layout/copper, stale board renders, manufacturing staging, sourcing, ordering, and physical qualification.

**DEFECTIVE / DO-NOT-ORDER.** This witness does not authorize placement, routing, release, or purchase.
