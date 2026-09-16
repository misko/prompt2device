# Placement/source backtrack — 2026-09-07

Scope: project-local; candidate lessons, not automatic shared-policy changes.

1. Requiring installed connector measurements before the first prototype's
   layout creates a separate coupon procurement dependency. Make that a
   deliberate project choice. ADR-0007 permits this user's unqualified
   prototype with typed physical risks; it does not fabricate qualification.
2. Syntactically plausible route YAML is not an executable route contract.
   Layer roles, topology net identities, conductor ownership and per-wave
   widths must be preflighted as soon as the candidate exists. The first actual
   run found three source-contract groups and later caught sub-floor widths.
3. Pin/net parity cannot prove a logic default against leakage. The independent
   reviewer found three 1 Mohm clock pulls unable to sink the selected buffer's
   worst-case input leakage below VIL. Budget leakage, resistor tolerance and
   driven-state loading explicitly before selecting a replacement.
4. An earlier primary-agent SOUND label was not an independent review. Fresh
   five-page visual inspection found real VMID and ADC-label occlusion despite
   matching source/netlist identities. Retain DEFECTIVE witnesses and correct
   source; do not refresh a hash and reuse the old verdict.

Next writer: preserve the current exact rejected subject, fix the three clock
pull-downs and the ADC/VMID TSX layout, then deliberately regenerate schematic,
public BOM request and checkpoints. Compare the intended pin/BOM delta before
adopting replacement reviews. After SOUND source admission, resolve the logged
model, local-clearance, thermal and silk findings before first routing spend.

## Missing model assets are not the same as missing bindings — 2026-09-08

- what happened: the first current 299-component board stopped at P-MODEL
  252/299. Root independently reopened all 299 rows: 35 references declared
  six missing library files; 12 references had no model in four custom
  source footprints. The generated project contained only Default because
  the downstream rules generator had not run.
- root cause: source/library model completeness was not closed before the
  first modeled placement boundary. A valid footprint name and successful
  board save do not establish a resolvable body, registration or complete
  project rules. The exact failure is retained in the first-board report.
- avoid next time: inventory missing files separately from absent bindings;
  pin public asset provenance and project-relative attachments in source.
  Reopen bound checkpoints after source changes and regenerate downstream;
  never route the partial snapshot or treat old DRC as a current result.
- candidate-canon: no; project-local application of existing P-MODEL,
  MODEL-REG and R-RULES, not a proposed new policy.

## Regional placement is not local circuit placement — 2026-09-08

- what happened: read-only saved-board72f4b136 diagnostics resolved41 named
  bypass/filter refs to their owner ICs. C_OPA4 supply pads were44.39mm apart,
  C_ISO5 28.13mm and C_LDO_IN23.17mm. These are pad-centre lower bounds, not
  routed length or loop-area measurements. The unchanged placement policy
  returned PASS4/N-A1 but graded only one inductor keep_short budget.
- root cause: broad regions seed floaters centrally; the generic legalizer
  preserves geometric legality but has no implicit electrical-owner objective.
  Prose-only local-layout guidance supplies no machine-graded distance row.
  The narrow C_LDO_A/D region-selector correction therefore cannot close the
  wider placement issue. No repeated failed conductor was needed to establish
  this separate source hypothesis.
- avoid next time: local pin-owner clusters and supported machine-readable
  budgets must be authored before the next review/board cycle. Repeated parts
  on a shared rail need exact-ref pairing; footprint-ID-based keep_short can
  otherwise let the nearest wrong sibling satisfy an intended local check.
  Separate centre-span and pad-edge metrics, declared coverage and return-loop
  review; a budget count is not full299-ref layout acceptance.
- candidate-canon: no; project-local application of existing placement-and-
  proximity and P-LAYOUT/P-ADJ, not a new checker or vendor gate. Preserve all
  electrical/connector/model identities and require actual later PCB checks.


## 2026-09-10T21:04:19Z — candidate-dependent rules invalidate monotone width search

- MEASURED: the native18-station matrix in evidence/pland-backtrack-20260910 accepts a0.400mm track that intersects a width-relaxation area but rejects its0.200mm version; a second station activates stricter clearance on the wider capsule. The rejected clearance-to-width fixed point can oscillate. A global maximum from one pad-wide clearance is not the native predicate.
- Candidate shared-method correction: compile rules once, partially evaluate fixed pair facts, and validate finite declared-width candidates at their final width/type/layer. A retained witness proves one launch; failed finite search is unresolved. Numeric maximum/deficit claims must migrate deliberately. Native exact shapes avoid measured polygon-gap overstatement, and spatial bounds must include local item clearances.
- The private prototype and complete diagnosis are evidence, not production authority. Actual public-path RED/GREEN, supported-language guards, full checker tests and contract synchronization are owed. This records the upstream algorithm decision without changing electrical requirements or crediting CAR-F12 progress.


## 2026-09-10T21:29:06.607701+00:00 — candidate prevention: regression fixture admission

A checker test that fails before its intended graded subject is reached is not
behavioral RED. This attempt used ephemeral pcbnew netclass assignments which
were lost on save/reload; both captured specimens had zero graded pads. Future
fixture construction must reopen exact native files and record classes, declared
floors and denominator before attributing a CLI failure to geometry. Preserve
full subprocess output, not only a harness exception tail. Sampling parameter
names are not sample-count authority: inspect actual grid math before editing.
This is a candidate method improvement, not hardware progress or canon adoption.


## 2026-09-10T21:44:52.802600+00:00 — candidate prevention: required native data before optional APIs

All three native census attempts read pads through exercised bindings, then
failed before emitting the buffered result while exploring unbound C++ class
containers. A required observation must not depend on optional introspection.
Persist scalar/native polygon records first; isolate compound-class semantics as
a supported or explicitly unsupported rule feature. Model escalation alone does
not repair this dependency. Production work is decomposed at native fixture,
rule/candidate semantics and public regression boundaries. Candidate learning,
not canon adoption or electrical progress.


## 2026-09-10T21:55:55.121654+00:00 — candidate prevention: producer owns the transaction directory

A bootstrap that precreates an output directory conflicts with a producer that
requires absent-path atomic creation. The freshness guard correctly stopped before
native work. Use an existing private parent and let the producer atomically allocate
and report a unique child. Keep old outputs and all admission assertions intact;
do not repair this mismatch by accepting an arbitrary existing output directory.


## 2026-09-10T23:11:26.501386+00:00 — candidate canon: parser admission and native proof closure

A useful native fixture matrix does not validate syntax that the rule loader
silently discards. Validate the entire rule structure before per-constraint
scope filtering, and bind an explicit candidate layer/search contract. Native
local/footprint overrides require both value and optional-presence controls.
Preserve each child fixture and its actual process receipt; a harness return
value must reach the process exit status. Evidence and exact failed WIP:
../evidence/pland-backtrack-20260910/native-kernel-adoption.md. Proposal only;
no gate or threshold is waived, and no electrical finding closes from this work.

## 2026-09-11 — source orientation contract missing after accepted schematic

- Measured cause: the first normal placement continuation reached P-ORIENT in90.685s. Model paths resolved333/333 and pad-launch677graded0fail, but model_registration.yaml was absent. Resolving model files does not prove connector mouth geometry or mating direction.
- Project-local remedy: give the source owner the complete11-connector census and manufacturer datum/model evidence; author the missing source contract and required geometry, then regenerate and regrade affected subjects. Do not ask the user to approve absent or unregistered views.
- Candidate prevention: inventory model/orientation source dependencies when preparing the first placement handoff. The two-minute post-handoff close budget and actual-output preflight worked; root still needs to commit the tracked compact handoff before enforcing a clean-tree dispatch. No gate or skill change is adopted by this entry.

- 2026-09-11 MEASURED candidate prevention: authoring-frame vectors can make an orientation checker agree with itself while the encoded model uses the opposite Y. Native model vertices/renderer transforms need independent qualification before an axis receipt carries authority. No checker change adopted.
- 2026-09-11 MEASURED coordinator correction: output preflight passed but outer agent closure rejected root scratch/helpers outside declaredwork. Future commissions must name exact helper/scratch homes and verify the filesystem delta beforeFINAL, in addition to output validation. Preserve original failure; no retroactive scope broadening.

## 2026-09-12 — candidate prevention: mounting-side source dependencies

Moving a reviewed component to B.Cu also changes its registration authority and the mounted-side Fab/courtyard datum. Resolve both before renewing schematic reviews. A source collector that only looks for front artwork falsely reports missing body geometry on a legitimate bottom component; simply choosing bottom artwork is insufficient if render projection, signed-side proof or cache identity remains front-only. Test an asymmetric native flipped body and opposite-side decoy outlines, preserving wrong-model/side rejection. Current source repair remains pending; no gate or threshold waived.

## 2026-09-13 — reusable guidance adopted after user process question

The user asked how to save time on the next use of this skill. Two existing procedure references now carry three focused diagnostic lessons: census the full affected population when a first-refusal checker leads to serial repairs; verify the geometry actually constructed by a native consumer before attributing a synthetic-fixture result to a checker; and grade via drill/annulus extent separately from centre-point membership and same-net clearance. No new gate, schema, threshold, review battery or retry allowance was introduced.

MEASURED: skill authority passes; disclosure14/14 with2known-bad and2declared blind spots; documentation15/15 with2known-bad; both edited skills pass quick validation. These checks establish documentation/authority consistency, not future speedup. Archive9d055c22f92ae5d6903ed51258e47d23ca7a8ad1609ef9e55d1b66323de31c12 retains exact guidance and runtime evidence17603bytes/14reopened members. Active engineering reassessments still own candidate-specific judgments. This procedural change does not accept either board or waive a failed checker.

## 2026-09-13 — complete the source and assembly dependencies around a geometry trial

- what happened: The sole admitted candidate4 generated and prepared both boards without clearance, hole, silk or thermal DRC violations. The later export correctly refused two stale hidden-reference exceptions, and the full source governance check found a new pod ADR without structured provenance for its retained probe-route budget. Two historical whole-layout test assertions and one missing test fixture also surfaced after generation. None required a second native construction.
- root cause: The initial source preflight covered selected geometry consumers rather than every cheap source prerequisite used by the full conductor. Native reference de-collision also changes the exact locator exception set; retaining the previous set does not prove current assembly coverage. The isolated test packet omitted a transitive fixture, and the model resolver needed the actual installed model directory.
- avoid next time: Include the conductor's schema and numeric-bound checks in source preflight, freeze transitive test assets and resolved model roots, then run the ordinary assembly export immediately after the single generated candidate. Keep documentation, test-scope and locator-only corrections separately hashed and review them against unchanged native bytes. Preserve original failures and distinguish missing release paperwork from an SMD-side failure.
- candidate-canon: no; this is a project handoff checklist proposal using existing gates, not a new rule or retry allowance. Root source qualification and the proposed pod provenance addendum are preserved in pod journal archive8c034deaaa9c8cd7e82d439ef76d31ffd19e0fed96853de22d671fe3db10e2de. Independent final-composition acceptance remains owed.


### 2026-09-13 — validate locator membership through its complete consumer

Project-local process lesson: successful assembly export and native locator identity did not exercise the policy-waiver membership check. When two formerly hidden refs became visible, locator23/native23 passed while policy25 survived; the next schematic topology review caught the stale set. Before another source handback, invoke the ordinary project-level locator consumer on the composed source. Record its exact stopping cause: a stale visual receipt is an explicit later boundary, while policy/source set mismatch is a source defect. Check all source consumers even when they feed the same displayed count. Do not relax exact equality, synthesize visual acceptance, or treat a lower-level export PASS as whole consumer coverage.


## 2026-09-13T21:07:47.438061+00:00 — project-local: grade each actual conductor subject

Candidate4 preserved the exact failing placement bytes but only graded DRC after route preparation. Its prepared result could not certify the earlier normal P-DRC gate. Before renewed source acceptance, the bounded candidate method must exercise every affected normal conductor predicate on the matching stage artifact, in order; keep placement and prepared copper identities separate. Do not weaken the earlier gate or infer its result from later fill. A single full-ground override must still earn electrical/assembly review and exact native confirmation. This is a project-local prevention requirement, not a shared checker change.

Observer setup also repeated a known console-tail/limit mismatch before dispatch. Mechanical successor wrappers should use shared runtime defaults or an already validated options set. Preserve setup failures without inventing a board run or resetting engineering budgets.


## 2026-09-13 — project-local: qualify zone-connection semantics, not reservation intent

The fifth candidate faithfully generated the reviewed full pad-clearance pour reservation, but the ordinary pre-prep thermal check still reported the same one-spoke failure. The corrected stage order stopped the candidate in9.762s before preparation could hide that earlier refusal. Source geometry containment and61 passing source methods established their actual properties; they did not establish the assumed thermal-consumer behavior. The failed native bytes and all500 individually bound raw rows are preserved in journal/98247be38fc8aee17cf51e51ef69fae095efcb87b8a3d9d28d385f37143505d7.tar.gz.

Candidate prevention proposal: when intended current return depends on a pad having no direct zone connection, inventory the actual per-pad connection modes and their generator/validator support before selecting a geometric workaround. Confirm native consumer behavior on the owning subject; do not equate a pour prohibition with pad-connection semantics. Current generator supports full/thermal strings, and the project override regression assumes32full targets. A new mode would need explicit source ownership, serialization/known-bad qualification and preserved existing target sets. Independent diagnosis is pending; this entry does not authorize a setting, new trial, gate change or lower spoke minimum.

A separate root test inspection caught conflicting polygon/rectangle authority in the newly added source helper. Actual RED and corrected23-method GREEN now reject that ambiguity. Qualify helper identities using their lexical scope: root's first bare-name AST dictionary conflated two unrelated nested walk functions and failed before copying source. Preserve original exact run subjects before composing supplemental receipts, rather than reconstructing them afterward. These are local process corrections; no new mandatory review battery or retry allowance is introduced.


## 2026-09-14T00:34:05.955742+00:00 — candidate canon: use owning stage contracts in temporary proofs

Candidate6 cleared the actual ordinary thermal gate, then a temporary proof stopped on `visible_refs = not invisible`. The board had exactly the 23 source-owned locator exceptions. Independent review confirmed that the assertion was overbroad, but also confirmed that exact membership does not replace the current locator bundle and independent usability review. Separately, a temporary DRC classifier handled dangling tracks but omitted dangling vias; all 21 omitted rows mapped to declared seed owners. Original failures remain preserved in 127c30182250fb001b2ec627247e0452cd1e0f86a97e7067eaf1c529d9fd6531.

For the next task, map each temporary proof assertion to its canonical owner and due stage before running a native candidate. Keep electrical source-to-native binding separate from assembly usability. Exercise the full closed set of expected prepared-stage row types, retaining a refusal for unknown types. Use canonical A-LOCATOR plus current render acceptance for reference exceptions. A source-intent census is not a waiver and a prepared routing obligation is not a completed route failure. This is a prevention proposal, not a changed skill or relaxed gate.


## 2026-09-14T01:16:42.962600+00:00 — inspect every mounting-side consumer before a top-only continuation

The top-only floorplan and assembly population were coherent, but the native registration source still declared the eight Littelfuse bodies on the back. This stopped the canonical conductor after thermal/placement progress. Before another mounting-side change, enumerate every registered reference and compare actual/source mounting side, model transform and declared orientation; validate every unchanged tuple cache. This incident has a complete6-group/28-instance census with exactly8 stale declarations. Copper on B.Cu is not bottom-side component assembly. Refresh only changed evidence through its owner; do not restamp old side renders. Proposal for an earlier batched preflight, not an implemented skill/checker change.
