# Early lifecycle boundary composition

This reference owns the composition of three prevention boundaries. It does
not own their underlying electrical, placement, routing, or JLC predicates.

## Contents

1. Shared evidence and applicability
2. S-PART-FREEZE
3. E-CLOSURE
4. P-FEASIBILITY
5. Promotion rule

## Shared evidence seam

Domain gates keep their detailed measurement JSON. The current
`scripts/pipeline_stage_evidence.py` adoption seam deliberately does not
promote those bytes:

```text
legacy domain measurement -> exact-subject typed INCOMPLETE StageResult
                          -> outputs: []
                          -> accepted bundle/pointer unchanged
```

Writing an accepted bundle and a separate stage result cannot be one atomic
filesystem transaction. Promotion therefore remains disabled until both share
one content-addressed, pointer-last commit and the domain predicates can be
independently regraded. Failed, incomplete, timed-out, stale, zero-denominator,
or even legacy-accepted measurements cannot replace the prior bundle through
this seam. The legacy driver remains execution authority until canary traces
agree.

Applicability is compiled before these compositors run. The pure compiler
consumes the capability profile plus closed fact envelopes labelled for the
architecture, integration, power, and assembly owners. It emits `APPLIES`,
`NOT_APPLICABLE`, or `INCOMPLETE` with the exact determining hashes. Missing or
nonpassing required facts are `INCOMPLETE`; file presence, prose inference,
router disclosure selection, and an authored N/A flag are not applicability
authority.

The current applicability receipt is explicitly `SHADOW`. Exact-input
recompilation proves only structural consistency: an arbitrary authority
string, self-declared PASS, and caller-supplied requirements do not authenticate
the facts. Promotion requires a closed domain-to-producer registry, reopened
accepted owner receipts bound to their canonical subjects, and a pinned
requirements registry. Until
those exist, an authoritative consumer returns `INCOMPLETE` even when the
structural compiler emits APPLIES or N/A.

## S-PART-FREEZE

Run after the complete preliminary BOM and build quantity exist, before
placement. `jlcpcb-fab/scripts/manufacturing_readiness.py --phase prelayout`
owns the predicates. Its legacy domain receipt may be `ACCEPTED`, but an
optional `S-PART-FREEZE` stage request writes only a typed `INCOMPLETE` result
with no output or accepted bundle.

It composes exact MPN/LCSC identity, one dossier per used MPN, source-value
identity, assembly disposition, quantity-expanded availability, and
procurement exposure. Public catalog evidence remains a pre-layout negative
filter; final allocation/uploader evidence is still mandatory. Do not add a
second hand-maintained part-freeze file.

The preliminary catalog probe must apply the project's named absolute stock
surplus after aggregating all references on each LCSC line (for example,
`build_quantity * per_board_qty + 200`). The receipt records required quantity,
threshold, observed surplus, and timestamp. This volatility filter neither
authorizes MOQ cash nor substitutes for the hash-bound `AVAILABLE` response.

## E-CLOSURE

Run after fresh netlist export and before schematic review or placement.
`kicad-pcb/scripts/electrical_closure.py` composes, without reimplementing:

- net-label survival;
- electrical invariants and ADR coverage;
- design/protection/switching/fault/corner models;
- converter topology, output margin, and off-control;
- pre-board component/reference census; and
- source-value identity.

Every specialist must pass. Those specialist scripts remain the sole owners
of equations and limits.

Legacy authority remains byte-for-byte compatible at this boundary: projects
without `03_src/rules/operating_states.yaml` run nine specialists, while a
project that already authored that file retains the former tenth
`operating_state_check.py` call, verdict contribution, and receipt inputs. The
new compiled-applicability shadow never removes or replaces that opt-in. It
writes only a sibling pending request and adds no extra checker invocation to
the closure hot path. If that separate request later resolves to applicable, a
missing, empty, malformed, or evidence-free contract is `INCOMPLETE`, not N-A.
A separately budgeted runner may use the generic specialist to compare authored
producer and consumer intervals and reopen every cited file at its declared
digest. Such a run proves citation bytes, not numeric values at a free-text
locator, so its diagnostic remains `SHADOW` with evidence authority
`UNVERIFIED`.

Authoritative operating-state evidence needs typed part/config/corner
extractor receipts that name a machine locator and tool identity, reopen the
owning bytes, re-extract the source/default/negotiated/startup/steady/off/fault
intervals, and compare them with the receipt. Do not hard-code a device table
inside the generic containment checker.

During migration, `shadow` records only the pending request and preserves the
legacy E-CLOSURE denominator and verdict. A separately budgeted diagnostic is
not admissible stage evidence. The present `authoritative` mode fails
`INCOMPLETE` until both producer-receipt and typed-extractor prerequisites above
exist; clean/N-A/known-bad canaries are then still required. `legacy` remains
an explicit compatibility mode, including the historical file-presence opt-in;
replacing that rule requires its own reviewed authority migration.
E-CLOSURE stage promotion is independently disabled by the shared evidence
seam and creates no accepted bundle.

## P-FEASIBILITY

Run the [controlled-pair footprint screen](../../kicad-pcb/references/placement-and-proximity.md#package-choice-is-a-placementrouting-decision)
before committing package/stack rules to full placement. Its early command
requires no routed witness and grants no stage admission. The same check is
repeated by the compositor below.

Run on the exact placed board before route preparation. The existing
`placement_routability_preflight.py` compositor records a typed
`P-FEASIBILITY` shadow result. It combines physical placement, critical
inventory, route ownership, endpoint topology, layer eligibility, ordered
connector lanes, explicit series power transitions, and the authoritative
`coupled_geometry` check when a combined neighborhood is declared.

```yaml
require_connector_lanes: true
connector_lanes:
  - ref: J_UP
    why: USB physical lane order
    lanes:
      - {pad: A6, net: USB_UP_P}
      - {pad: A7, net: USB_UP_N}

require_series_power_paths: true
series_power_paths:
  - id: protected_input
    why: input fuse cannot be bypassed
    transitions:
      - {kind: copper, from: J_PWR.1, to: F_IN.1}
      - {kind: component, from: F_IN.1, to: F_IN.2}
      - {kind: copper, from: F_IN.2, to: U_AGG.5}

coupled_neighborhoods:
  - id: clock_and_adc_launch
    nets: [MCLK, BCLK, ADC_D0, ADC_D1]
    why: these launches share one constrained escape corridor
coupled_witness: 06_build/coupled/combined-witness.kicad_pcb
```

`copper` endpoints must share one non-empty net. A `component` transition
must cross two different pads/nets of one footprint. Realized filled-copper
connectivity and ampacity remain post-route checks.

Each coupled-neighborhood row is closed to exactly `id`, `nets`, and `why`;
the ID is unique, `nets` contains at least two unique exact names, and `why` is
nonempty. `coupled_witness` is an optional project-relative `.kicad_pcb`; the
placement CLI may override it with `--coupled-witness`. The leaf command is:

```text
coupled_geometry_preflight.py grade PROJECT --prepared PREPARED \
  --witness WITNESS --workspace FRESH_DIR --json RECEIPT [--board-name NAME]
```

Its schema-1 `coupled-geometry-receipt-v1` has exactly `route_base`,
`candidate`, and `realized_policy` checks. Each attempt copies the prepared
board/project/rules plus the resolved current nets source into an immutable
`<workspace>-current-rules/` sibling, reruns `generate_rules_generic.py`, and
requires the regenerated board bytes to equal the prepared board. This closes
the placement-before-rule-generation ordering without trusting stale prepared
sidecars. Prepared bytes own placement, pads, and inherited seed copper; the
witness may add alternate legal copper but cannot move or delete that
authority. Candidate grading
reuses route-base, via-in-pad, physical-DRC and connectivity predicates, with
`tracks_crossing` blocking. Width and scoped floors come from the prepared
placement and freshly generated `.kicad_dru`; allowed layers come from class
policy, route defaults and any reference-plane narrowing; zero-via policy
comes from the resolved current `nets.yaml` length-match groups. Required nets
come only from the closed neighborhood declarations.

Missing or unreadable witness, tool or evidence is `INCOMPLETE`. Moved or
deleted prepared geometry, missing inherited copper, disconnected required
pads, native collision/width findings, forbidden layers or forbidden vias are
`FAIL`. A PASS admits only the exact combined witness and does not prove global
routability or impossibility. The receipt binds the rules generator, regenerated
board/project/rules, current nets, selected KiCad CLI/Python/pcbnew module and
native pcbnew runtime. It reports exact expected/observed check and required
net/neighborhood coverage. `verify` hash-reopens these inputs, independently
recomputes route-base and realized source/native policy, derives candidate
status from the verified child, and requires the placement status to agree.
Placement embeds
the child in `placement-routability-receipt-v2`; when the placement JSON is
`06_build/verification/placement_routability.json`, its omitted workspace
uses a fresh `attempt-<uuid>/` beneath the sibling
`placement_routability.coupled-workspace/`. Explicit `--coupled-workspace`
names one fresh immutable attempt and refuses reuse. Direct leaf use also
refuses a pre-existing `--json` path before mutating either output location.

Switching-loop adjacency, zone ownership, and service-part reachability should
extend this compositor as domain predicates, not new lifecycle stages.

Functional-cell evidence remains shadow until it is built from independently
observed ref-to-MPN identities, real pad geometry, board obstacles, and fab
facts. The authored placement snapshot may declare intent but cannot prove its
own orientation, corridor, ground-egress, or resistance claims. Missing
independent observations make the separately budgeted shadow request
`INCOMPLETE` without changing the legacy placement-routability runtime,
receipt, verdict, or identity. The placement command writes this request beside
its authoritative legacy receipt; it does not execute the shadow compilers in
the hot path.

Receipt reopening regrades the bound coupled child when that check passes.
The optional typed P-FEASIBILITY stage publication remains deliberately
`INCOMPLETE`, with no accepted output or bundle; the authoritative placement
receipt and final route acceptance keep their existing roles.

## Promotion rule

Promote one boundary at a time only after focused known-bad tests plus USB Hub
v4, Pluto v4, and USB-controlled-debug-hub canaries show equivalent order,
applicability, denominators, blockers, and backtrack targets. Remove replaced
duplicate invocations in the same promotion change.
