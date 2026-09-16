# Schematic correction learnings

## 2026-09-07 — corrected local defaults; independent review reopens source

MEASURED in this iteration:

- Six resistor changes preserve the original 206-part, 601-pin connectivity:
  three clock pull-downs to 10 kohm, OE pull-up to 10 kohm, and the presence
  divider to 300 ohm / 10 kohm. This is preservation, not proof every original
  pin was correct. The fresh review found the pre-existing ADC SPI_CS error.
- The prototype DC screen reopens exact TI/Diodes PDF identity, checks source
  MPN/code/value and native pins, and reports all eight predicates. Its
  additional leakage/drift budgets are explicitly engineering allocations;
  neither module IO nor MOSFET all-temperature behavior is manufacturer-proven.
- The pinned tscircuit type declarations accept `schPinSpacing`, but the
  runtime emits a deprecation warning and ignores it, forcing 0.2 mm. A first
  attempted PDF therefore retained crowded labels. `schPinStyle` top/bottom
  margins are consumed: 0.3 mm on either side gives measured 0.8 mm per-side
  ADC pin pitch, with all 49 pins present. Type acceptance was not rendering
  evidence. No dependency or generated Circuit JSON was hand-patched.
- Splitting the ADC reference networks onto a separate sixth sheet removes
  the old R_VMID2_ISO/C_VMID1_4U7 collision. It does not fix boxed-label text
  baselines, resistor-value occlusion, or the separate power-page wire/label
  collisions identified by fresh review.
- Full producer/semantic gates pass with 0 error records, but 1370 warning
  records remain: refdes convention 25, unnamed traces 564, outside-sheet 513,
  underspecified pins 51, missing power attributes 51, missing ground
  attributes 51, supplier lookup 8, supplier footprint comparison 107.
  The fitted human pages and governed KiCad land patterns are independently
  checked; the warning census must not be summarized as a clean producer.
- Native ERC has 0 errors and 868 baseline warnings (551 off-grid endpoints,
  299 missing ambient `elt` library entries, 18 unconnected wire endpoints).
  Native netlist equivalence and named-net survival pass separately.
- Fresh public catalog screen covers 38/38 exact coded lines at five boards.
  The removed 1 Mohm code is no longer in the populated request. This is
  not JLC PCBA allocation; the operator worksheet remains blank.

Next source owners, not user/hardware blockers:

1. Re-derive and correct U_ADC SPI_CS pin 38 termination from Cirrus Table 1-2,
   with a new exact invariant. Do not preserve the bad connection merely to
   keep parity with the previous candidate.
2. Correct the audio ESD authority in `protection_paths.yaml`: typical TLP
   clamp voltage is not an 8/20 us maximum, and no 14 V silicon rating exists.
   The current E-SURGE checker does arithmetic over authored claims; its PASS
   did not establish those claims. Any unqualified prototype disposition must
   explicitly withdraw the unsupported guarantee, not relabel it as measured.
3. Inspect the shared `render_schematic_pdf.mjs` presentation adapter and
   `circuit-to-svg` baseline behavior. The adapter currently resolves ambient
   circuit-to-svg 0.0.391 / schematic-symbols 0.0.232, whereas the project's
   frozen dependency tree contains 0.0.400 / 0.0.239. This is an observed
   version difference, not yet proof it causes the glyph defect. Test against
   exact immutable Circuit JSON, preserve port alignment and add regression
   evidence before changing the renderer or its dependency resolution.
4. Reorganize the power page: F7/C_BUCK_IN3 labels overlap; Q_IN's current
   source-left/drain-right symbol arrangement makes the intended entry path
   difficult for the automatic schematic router. An explicit drain-left /
   source-right / gate-bottom schematic arrangement is a candidate remedy,
   not an approved connectivity change. Recheck the actual resulting pixels.

The topology witness also leaves three explicit engineering risks: OE input
slew with a 10 kohm pull-up and nonzero capacitance, the mismatch between the
LDO's 150 mA/400 mW budget and its dossier's 85 C thermal allocation, and ADC
startup including both 470 uF reference banks. Re-derive these source budgets;
do not defer a provable source contradiction to bench work or assert that an
illustrative typical-capacitance/thermal model proves physical failure.

The reviews are forensic DEFECTIVE evidence, not adopted approval. The visual
witness discloses persistence 20 seconds after its ten-minute deadline. The
topology witness's reported 13m28s interval exceeds its twelve-minute commission.
The coordinator did not enforce either deadline promptly. Retain both reports
verbatim, but do not promote them as timely reviews or count them as a passing
bounded-runtime attempt. Any corrected subject requires new bounded reviews.

The corrected-stage original artifacts are retained in Git and temporary
archives `/tmp/crow-carrier-source-correction.xRnX6j` (before six-value change)
and `/tmp/crow-carrier-spacing-correction.GA9Gyy` (first ignored-spacing attempt).
The next full producer run must preserve its current request/checkpoints before
regenerating; no immutable pod release may be edited.

## 2026-09-07 20:31 UTC — fresh-source correction results

- Unused pins do not share one blanket rule: DS1314F1 Table1-2 sends
  SPI_CS toVDD_IO while the other unused SPI controls go toGND. The new
  exact invariant and hostile source test pin that distinction.
- TLP typical clamp,8/20us peak current and IEC component amplitude are
  different evidence. The shared schema now permits explicit unqualified
  prototype ESD selection with real normalVIO/component ratings, nonzero
  exposed population, and no invented transient maxima. It cannot weaken
  the genuine input-surge checks or label board survivalPASS.
- DC gate margin did not solve OE slew. A genuine Schmitt inverter now
  handles slow presence input; its push-pull output drives the local OE.
  Native KiCad includes its NC pin as an empty-net entry, not an absent pin.
- A minimum-output-capacitance PASS is not a regulator/load-bank stability
  proof. Correcting400mW to238mW causes the existing E-TOPO gate to expose
  the thermal contradiction. Keep150mA/85C until a valid power redesign.
- Mode-specific DS1314F1 section4.5.6 overrides a generic VMID-buffer
  example. Hardware/default mid-Z requires an external VMID source;
  blindly preserving a checked topology preserved the wrong source.
- New generated subjects require new acceptance. Old catalog/checkpoint,
  ERC, review and placement artifacts are historical/stale. Preserved
  records and exact hashes are in SOURCE-CORRECTION-20260907.md; no prior
  DEFECTIVE review was edited or adopted as SOUND.

## 2026-09-08 — Ground-only clearance is not complete schematic ink clearance

- what happened: dab4f14e passes the0/169 Ground-only collision regression and
  all68 project tests, but fresh19/19-page review finds one P0 and four P1
  presentation groups. Root independently viewed each group. Complete electrical
  equivalence is SOUND, so no native short is established by these drawings.
- root cause: inferred from exact routes and rendered evidence: the presentation
  model routes to anchors without reliably reserving complete label plates,
  filled symbol bodies and NC endpoints. U_RST2's different-net vertical
  centerlines at x-1.52/-1.53 are geometrically distinct but their ink merges;
  ground-symbol obstacle testing cannot detect that class or a foreign plate.
- avoid next time: source-model regressions must cover foreign wire/plate ink,
  label/label contact, near-coincident parallel strokes, NC clearance and hidden
  body traversal, with positive/hostile fixtures and exact all-page inspection.
  Prefer explicit source rail/pin corridors; do not hide foreign wires behind
  opaque labels or silence the owning normalized digest. Preserve all circuit
  semantics and re-gate the actual generated subject.
- candidate-canon: yes — proposed schematic ink-obstacle/clearance regression
  alongside S6; this is a candidate, not an adopted shared policy or gate.

## 2026-09-08 — Source corridors and honest screen limits

- what happened: the five exact render findings were remedied by pin-side
  grouping and full supply/timing/pulse corridors. A broader project screen
  reproduces17 original contacts and reports0 on the final19-page candidate.
- root cause: CJ anchor/center offsets do not reliably encode rendered plate
  width; rotated RESET_RC disproves that shortcut. Filled-body routing and
  near-coincident foreign strokes also need separate classifications.
- avoid next time: use pinned renderer glyph metrics for complete ordinary
  plates, end-to-end hostile/good fixtures, an interior epsilon rather than a
  broad hidden-body inset, and preserve perpendicular crossings. A zero screen
  does not cover all component reference/value/general text: scratch3/4 were
  rejected from actual page views despite zero results in narrower screens.
  Keep final all-page/detail viewing and independent review mandatory.
- candidate-canon: yes — renderer-owned complete ink obstacle geometry; no
  shared policy or gate adoption occurred in this source-author pass.

## 2026-09-08 — Output disable does not establish an input default

- what happened: exact fresh topology review7b13bad1 found an undriven
  TDM_RAW input despite190 passing source tests and zero ERC errors.
  Independent root node census is exactly U_ADC.25/U_TDM.2;manufacturer
  text makes the ADC output high impedance outside transmission.
- root cause: the source power-state contract covers remote presence and
  output enable,but omits the local ADC's non-transmitting state. An input
  can float even when its buffer output is disabled. A weak resistor alone
  also needs transition-rate review when a previously high driver releases.
- avoid next time: enumerate transmitter drive/high-Z state separately from
  receiver power/OE state. Check the actual source net and selected input
  technology,then leakage,loading and release transitions together. Add
  hostile regression cases when adopting the correction;do not claim that
  this learning or an unimplemented candidate closes the finding.
- candidate-canon: no — local ADR0005/invariant coverage correction first;
  no shared gate or new policy ID was adopted in this review turn.

## 2026-09-09 — AC coupling is not startup current limiting

- what happened: fresh review identified an allowed connected-pod cold-start
  case outside OPA input absolute limits. Root confirmed source/primary limits
  and the missing startup envelope; no actual waveform/damage is claimed.
- root cause: settled common-mode and downstream isolation were checked, but
  a coupling capacitor passes a fast common-mode step into an unpowered input.
  A100kΩ shunt does not limit it; no-hot-plug does not exclude cold power-up.
- avoid next time: bound startup/shutdown/restart input voltage and current,
  both polarities, rail injection and added noise/loading. Add a known-bad
  source regression before adopting protection.
- candidate-canon: no — project-local source correction first; no shared gate
  or measured physical qualification is claimed.

## 2026-09-09 — Current limiting, shared rails and reporting need separate checks

- what happened: a real 16-input source correction passes 24 focused checks
  but the complete suite still has 18 failures. Independent RC arithmetic
  agrees under explicit budgets, while finite-inductance/repeated-input
  behavior, one power-entry witness and exact new geometry remain unclosed.
- root cause: local current limiting does not alone bound a shared powered-off
  rail. A nominal current-limit minimum is not an overload maximum; a damped
  linear rail model and a one-event magnetic reserve are not a nonlinear
  arbitrary-waveform proof. Old exact-delta fixtures also need a separately
  checked new delta, rather than count-only updates or broad exclusions.
- avoid next time: test current, common rail state, stress and inventory
  independently; retain real full-suite failures. Compute aggregate report
  status only after every check is merged, with a failed-child regression.
  Bind terminal records using the canonical TaskEnvelope digest, not the raw
  JSON file hash; schema parsing alone does not establish task admission.
- candidate-canon: no — these are project-local source/workflow findings.
  Candidate and precise next-owner obligations are in the damped-start report;
  no shared gate, accepted design or physical qualification was changed.

## Loaded precharge and unused-pin normalization (2026-09-09)

- what happened: the unloaded1.817mV settle result omitted controls/leakage;
  an intended-NC adapter overwrote real connected or absent terminals. Both
  actual RED cases now have GREEN in the239-test final source run.
- root cause: expected topology was used to rewrite observed topology, and a
  zero-load RC expression was presented as a loaded residual. Separately,
  buck minimum current limit was mislabeled as maximum feed stress.
- avoid next time: normalize only observed NC encodings, reject absent/wired
  terminals, model steady current during precharge, and separate converter
  minimum limit, engineering peak/duration budget and capacitor redistribution.
  Preserve finite-grid challenges without calling them a general theorem.
- candidate-canon: no — project-local corrections and evidence; no shared
  policy weakening or physical-qualification waiver. Geometry and239 source
  tests are green, but the coupled power and dossier acceptance is still open.

## Decision progress must survive context and model changes (2026-09-09)

- what happened: successive models produced useful corrections without closing
  the protection decision; the final linear model left its admitted domain.
- root cause: experiment execution and report production did not themselves
  account for cumulative decision progress. Source, realized-layout and physical
  obligations also need explicit owning boundaries to avoid circular demands.
- avoid next time: declare a finite decision and relevant operating states in
  the existing finding; reserve before dispatch, assess evidence afterward,
  credit each milestone once, and backtrack when uncertainty prevents a choice.
  Preserve ordinary YAML defaults while rejecting explicit duplicate history.
- candidate-canon: yes — harvested in this change into existing lifecycle/
  D-BACK guidance, decision_progress.py and its behavioral regression suite;
  no new acceptance gate or scientific verdict is implied.

## A rail-to-rail candidate is not a completed protection decision (2026-09-09)

- what happened: OPA2320's conditional input-headroom screen passed four delay
  cases and five negative controls. Moving it to the ADC supply looked simpler
  but would put pod-injected charge on a TPS7A92 output with an empty input.
- root cause: supply/common-mode compatibility, nonlinear protection, stored
  energy and regulator reverse bias are different questions. A new catalogue
  part or a passing scalar cannot answer all four.
- avoid next time: compare the whole power/protection arrangement before
  adoption, keep unsupported states explicitly open, and take one named
  candidate to bounded source-part review. Do not spend repeated simulations
  merely confirming the newly generous common-mode margin.
- candidate-canon: no — project-local application of the existing bounded
  decision protocol. No rule, threshold, history budget or release gate changed.

## 2026-09-12 22:36 UTC — candidate process learning: delivery closure reserve

MEASURED: completed engineering handbacks again arrived at root after their coordinator deadline; all three zero-replacement attempts correctly remain TIMED_OUT. Root observation time cannot authenticate an earlier completed-host event. Packaging success is not delivery admission. The failure records do not isolate provider delay from coordinator context scheduling.

PROPOSED: predeclare a work cutoff with a ten-minute closure reserve for future recovery reviews, close actual host FINALs immediately, and avoid beginning long root work while review delivery is due. Any replacement allowance must be declared or separately authorized before use. Do not relabel an exhausted task, alter timestamps, or expand geometry-investigation limits. This is a project-local process proposal; no shared skill or runtime policy was changed.
