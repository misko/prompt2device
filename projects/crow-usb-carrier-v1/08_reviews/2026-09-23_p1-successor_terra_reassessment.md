# Crow P1 placement campaign reassessment — read-only proposal

**Decision proposed:** do not admit a run yet.  The original `p1_floorplan_all`
work item remains exhausted: its `max_attempts: 2` covers the two local trials
below.  A later, positive reassessment may authorize exactly one *new*,
review-bound placement campaign work item; it must not edit that old budget or
reinterpret either failed trial as unspent.

## History and authority

| Trial | Immutable native subject | Result | Status |
|---|---|---|---|
| P1-1 | `637e266594a8b89dc8ce93ed9dc38f2661dc250c8f593fcc2cd2a03c3be44d51` | 32 real different-net copper shorts (JTAG, DCK/DCT, LDO thermal vias) | consumed failure |
| P1-2 | `37b455203fcdae0c20880a94b17a4bcfb61103fa2b8b9df9ecf095c9c97aa519` | zero shorts, but 155 native violations, 45 parity findings, 499 unconnected; model/courtyard and hold-bank evidence incomplete | consumed failure |

`01_docs/findings.yaml` finding `USB-P1-placement-backtrack` is the current
history authority: it explicitly says both local P1 trials are consumed and
requires upstream review followed by campaign reassessment without resetting
prior spend.  A runtime/coverage record with a smaller delivery count cannot
create an extra attempt.  The finding is owned by `placement-and-process` and
closes only after the listed native and ownership evidence exists.

## Present packet is not launchable

The repository is at `856f8c6f6d79b75c0870d6cc94f1eafaf01ad7a8`; its canonical
artifact is still under independent review.  These are useful provisional
identifiers, not an admission packet:

| Input | SHA-256 |
|---|---|
| circuit JSON | `416d4f78a8ae2e7040c51194d97dee7af424580e4acf8dc0e36d9c7b975a20da` |
| native schematic | `779b791cbd29a9a692bdef4100f92dcbb1414503a9945e7aa9fac5ef84f70e4b` |
| netlist | `ee245feee512f4cece0f0e055b4495150c9b5f0f5218341756861f01ea2e921b` |
| floorplan | `b0049211eaf65ef55f57db06d99da1ccc7b54296a0dd4eafe9ea3955d30bea3c` |
| modular plan (currently stale) | `fbf342c2f0ce016365fd40f5ff514f904dae0f34b37941dff1d1ca2cefc2fe59` |
| nets rules | `c2de0a8645d156eb219f9ebe65f6978b8123965f7e112d56ee91d12d2d06e109` |
| route policy | `3c3d8deae57f358ec91675d679299fa5ee209be61958459584c703bf8bb61415` |

Before a reassessment decision, canonical electrical, E-FAULT semantic/electrical
bridge, and canonical schematic reviews must pass on one frozen composed source
packet.  The E-FAULT bridge must assess the fresh CJ, not merely write its
digest.  USB4215 source adoption, including its conditional `[230,22.995,180]`
anchor and explicit outstanding physical-fit requirements, must also be
coherently in that packet. Physical FULL is an UNKNOWN hold, not a precondition
for producing the one candidate below.

### Pending modular-plan correction

The read-only candidate patch `/tmp/crow-dlc-modular-plan.diff` has SHA-256
`60a9c24765142dc59cca98a7b8595d2ea19bc52496a9525f16ad984bf498d098` and its
candidate JSON has SHA-256
`050e9a98201958f6c3ae9d5e38198ca2751cd4a7bc9e5bafc09c57b3340ce874`.
It changes only the `digital_power` endpoints for the three DLC replacements:
old GND pin 4 becomes pins 3 (AGND) and 5 (PGND), and `N5V_BUCK` pin 6 becomes
pin 7 (VIN). That mapping agrees with the TPS62822 DLC pin authority, so the
patch is source-correct for this endpoint inventory. It yields 568/568
components and 59/59 interfaces versus the stale 57/59 ground-interface
representation. It still needs independent adoption with the composed source,
and native parity must remeasure it. It does not reset P1, create a candidate,
or change the 59-interface ownership denominator.

## Bounded successor proposal (only after the prerequisites pass)

Replace the active P1 definition with one schema-2 review-bound successor owned
by `placement-and-process`, with `max_attempts: 1`, a new envelope and a new
native-board subject. Archive the retired P1 plan and both consumed-subject
receipts as campaign history; do not add a parallel second P1 item or alter the
prior spend. Its input receipt must bind the final commit, clean source tree,
exact accepted CJ/schematic/netlist hashes, accepted modular plan including the
DLC correction, floorplan/route/nets/connector contracts, USB4215 and
TPS62822DLCR part/footprint/model hashes, generator and KiCad versions, and the
passing upstream-review receipt hashes. It must name both prior board hashes as
consumed failures and backtrack to the campaign reassessment if any input
differs.

Its sole candidate is a fresh generated, saved native board.  Measurements are:

1. Native-to-netlist pin/net comparison, including USB aliases and the revised
   DLC pins; no different-net pad/via copper contact.
2. Native DRC under the prepared owning rule profile, with every remaining
   violation classified by actual geometry rather than dismissed as a default
   profile artefact.
3. Footprint courtyard and 3D-model coverage for the full 568-reference
   subject, including the seven repaired courtyard definitions covering the
   previous 16 references.
4. Exact 16 hold-bank positions/polarity and forbid-island exclusion; verify
   the reserved support corridors, not routing completion.
5. Connector placement/edge geometry as evidence only; all 19 physical
   connector FULL targets remain incomplete and prevent acceptance/promotion.

## What the single measurement should prove or rediscover

The 155 P1-2 violations were 63 clearance (56 U_ISO TMUX-related, seven DMQ
regulator lands), 36 hole (32 U_ISO GND vias and four USB4105-to-stake), eight
via-diameter, eight annular, and 40 silkscreen.  The 45 parity findings were
37 USB numeric-versus-A/B/SH aliases and eight `U_SPOKE` Datasheet-field
differences.  The 499 unconnected nets are a later routing quantity, not P1
clearance to claim solved.

Expected-but-unproven changes are: the three DLC regulators retire the seven
DMQ land cases; USB4215 retires the four USB4105 stake cases; TMUX B2 rules and
source parity repairs target the U_ISO and 45 parity classes; and source
courtyard/model repairs target the old 16/73 gaps.  None is a waiver: new
native geometry must demonstrate each assertion.  U_ISO via diameter/annular
and silkscreen outcomes remain unknown, as do USB4215 edge/mating fit,
courtyard interactions, residual DRC, and all routing feasibility.

## Hard stops

Do not create the new work item or generate a board if canonical review,
E-FAULT assessment, source-model correction, connector source composition, or
campaign reassessment is missing/negative.  Once authorized, stop the one-run
campaign and backtrack to the named owner if the generated board has a native
source mismatch, real short, unresolved P1 DRC/mechanical/courtyard/model
defect, failed hold-bank geometry, or subject/hash mismatch.  No second trial
is implicit.  A passing placement measurement is still engineering
**INCOMPLETE** until connector physical FULL is completed; it cannot admit P2
or routing.

This document is a read-only reassessment proposal.  It applied no source or
PCB change and does not authorize a campaign.
