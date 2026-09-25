# Layout precedents — finding how others routed the same local circuit

For every selected IC, search for layout/application guidance before placement.
Dense, switching-power, high-current analog, and RF ICs usually need an
inspectable routed precedent; ordinary ICs still need a recorded search and
datasheet layout read. Consulting it is cheaper and safer
than deriving the local layout from first principles. A manufacturer's routed
example has the strongest precedent authority only after its package, mode,
stack, return path, and rules are reviewed as applicable. This doc is the
source catalog, with what to extract and the rules that keep it canon-clean.

## Contents

1. Study-then-rederive contract
2. Sources in authority order
3. Transfer and licensing caveats

## The contract: STUDY, THEN RE-DERIVE

- Extract DECISIONS, never copper: adjacency (which passive hugs which
  pin), package orientation, escape pattern (which pins drop vias, where,
  staggered how), hot-loop shape, sense/feedback dress, layer-drop points,
  corridor reservations, thermal via counts.
- The decisions land in OUR sources: `part.yaml` `gotchas:` +
  `layout_refs:`, `floorplan.yaml` placement, `route.yaml` config. Never
  import board files, never trace over someone's copper (canon M3:
  everything regenerable from our source — the same line ADR-0002 draws
  for tscircuit's own PCB output).
- Record discovered references in the exact-MPN/package dossier's `layout_refs:`
  ladder. Reuse discovery for identical MPN/package, but never assume it
  transfers across an instance's mode, footprint, stack, reference plane, or
  route rules.

## IC research packet

Before P1, `03_src/rules/ic_reference_research.yaml` maps the source-derived
selected-IC census to per-MPN/package `parts:` records. Each record has
`mpn`, `package`, `artifacts`, `docs_fallback`, `applications`, `state`,
`research_owner`, and `next_action`; its artifacts must name the matching
dossier `layout_refs` `artifact` and `tier`. Each application's
`applicability.reviewed_for` snapshots exact `mpn`, `package`, `mode`,
`circuit_sha256`, `stackup_sha256`, and `route_rules_sha256`. `inspected: true`
requires `inspection.sha256`, `locator`, and `notes` from examined contents; a
URL or `inspected: false` only records discovery. A failed or inaccessible
design-file download is missing evidence assigned to the research owner. An
inspected documentation fallback may complete research, but leaves the
engineering result INCOMPLETE.

Publisher authority, ability to inspect, and editability are distinct. An
editable file can improve measurement, but neither editability nor a higher-tier
publisher transfers a layout across unreviewed package, mode, or stack
conditions. The packet is research evidence only. Constraints enter source
through normal review, and native P3 critical-route proof remains owned by the
board.

Before locking a critical package and stack for full placement, join that
research to a small native feasibility screen: the actual footprint pads,
intended trace/pair/via dimensions, generated project rules, nearby obstacles
and reference-plane access must fit together. For a controlled pair, inspect
both endpoints and every intervening protector/connector transition; a vendor
cross-section solve alone does not prove a pad escape. Run applicable native
process checks at this point so a rule-generator/process-checker conflict is
found before a full-board trial. Record the result in the existing IC research
and source decision, with unresolved route/SI/physical work explicitly deferred.
Reuse one dossier across identical ICs and prioritize native trials by interface
risk; this is not a requirement to build a separate coupon for every IC.

## Sources, in authority order

### 1. The datasheet's Layout Guidelines / Layout Example section
Nearly every power/analog IC carries one (often with a routed figure and
a layer-by-layer description). This is the part maker's own answer for
the exact local circuit. ALWAYS read it — the pin-map extraction habit
stops at the pinout table; the layout section is later in the document
and routinely skipped. What to extract: the hot loop, which ground is
quiet vs power, Kelvin connections, "place X within Y mm" rules, thermal
via guidance.

### 2. Any OPEN-HARDWARE reference design with PUBLISHED LAYOUT
TI / ADI / onsemi / MPS publish complete EVM layouts — schematics,
board files or gerbers, and assembly drawings — for most converters.
An EVM is a TESTED, routed instance of the local circuit at a known
current. Find it from the part's product page ("Design & development" /
"Evaluation boards"). What to extract: the escape pattern at the real
package, component orientation relative to the inductor, where they
accepted vias in sense lines, stitching density.

**THIS TIER IS WIDER THAN "EVM", AND MISREADING IT AS EVM-ONLY IS HOW IT
GETS SKIPPED FOR NON-CONVERTERS.** It is any reference design whose LAYOUT
is published — a vendor's own reference board, a chip maker's minimal
design example, a foundation's open board. MCUs, radios and codecs have
these as often as converters do.

**PREFER AN INSPECTABLE DESIGN FILE TO A RENDERED FIGURE FOR MEASUREMENT.**
A figure is read by eye at its available DPI; a board file or Gerber can expose
geometry. This is an inspection capability, not a publisher-authority ranking:
record both tier and format, and review applicability before extracting a
decision. Typical measurement access is KiCad (open and measure) > Gerbers
(measure, no netlist) > Allegro/Altium (only with a usable tool) > rendered
figure.

WORKED CASE — RP2040 (canon P-PREC; verified 2026-07-30 at
`raspberrypi.com/documentation/microcontrollers/rp2040.html`). Raspberry
Pi publishes a **"Minimal Viable Board" reference design in KiCad** —
schematic AND PCB layout — plus the full Pico and Pico W designs in
Cadence Allegro and a VGA carrier board in KiCad. All are free and carry
"Raspberry Pi grants permission to use, copy, modify, and distribute the
following designs for any purpose, with or without fee". `pluto-rx2-8way`
read the *Hardware design with RP2040* Figure 6 raster at 200 dpi
instead — a careful consult that stopped one tier short of a free,
editable, permissively licensed layout for the exact part.

Licence and access are separate: a publicly provided file may be opened and
studied under its access terms even when reuse is restricted. Record any reuse
restriction; study-then-re-derive remains canon M3 regardless of licence.

### 3. OSHWLab / EasyEDA open projects — SEARCH BY LCSC CODE
The highest-leverage source for THIS pipeline: we select parts by LCSC
code, and oshwlab.com search accepts the same code — returning real,
usually JLC-FABBED boards using the exact orderable part, with copper
viewable in the browser. Ground truth for "what actually manufactures at
JLC at which tier." Quality varies: prefer projects with fab photos /
order history, and treat a lone hobby board as a hint, not an authority.
NEVER import the EasyEDA board file — view, extract decisions, close.

### 4. Open KiCad projects (GitHub, Kitspace)
`filename:*.kicad_pcb <MPN>` on GitHub code search, or Kitspace's part
index. Weakest tier: unvetted, often unfabbed, sometimes wrong — use
only when 1–3 come up empty, and weigh a project by evidence it was
actually built (photos, fab outputs, issues discussing bring-up).

## Caveats

- License hygiene: EVM files and OSH projects are for study; we re-derive
  into our own config, which keeps us clean regardless of license. Do not
  vendor anyone's board files into the repo.
- A precedent at a DIFFERENT current/tier transfers only partially — a
  7A EVM's escape pattern may assume vias our standard tier forbids;
  re-check every via against `fab_tiers.yaml` floors (the ADR-0008
  lesson: hole-to-hole is the binding constraint at fine pitch).
- **DOES IT TRANSFER? THE REFERENCE'S SURROUNDINGS ARE PART OF ITS
  EVIDENCE.** A reference proves its local pattern works IN ITS OWN
  NEIGHBOURHOOD. Compare neighbourhoods before adopting it: how much free
  space does the reference leave on each side of the part, and does this
  board leave the same? A reference with open room on four sides, adopted
  onto a board that pushes the part to an edge or fills the middle with an
  RF star, can hand you a LOCAL pattern that still holds while the ESCAPE
  BUDGET does not — and the escape budget is what bites at stage 6, not
  the decoupling. Do the arithmetic at placement: escapes per side x
  (track + clearance) against the band actually left. MEASURED on
  `pluto-rx2-8way`: 8 escapes on the north 0.400 mm side into a 3.2 mm
  band is exactly 8 x (0.25 + 0.15), and that board carries 28 unconnected
  nets and 21 via-clearance findings in the MCU field. The RP2040 consult
  was right about the flash corner and the decoupling rows; nothing asked
  whether the FANOUT survived a different surrounding.
- RECORD THE SEARCH IN THE GRADED FORM. `layout_refs:` entries take a
  mapping form — `{tier:, artifact:, reached:, why:}` — graded as canon
  **P-PREC** by `policy_audit.py`. THE LADDER MUST NAME ITS CEILING: if
  the best tier reached is below 4, name the stronger artifact you did NOT
  reach and why. Stopping at tier 1 is often right; it must be a STATED
  call. The bare-string form stays legal and is counted OWED, never
  failed.
- Precedent disagreement: datasheet beats EVM beats OSH beats GitHub.
  If our derivation must depart from the datasheet figure, that is an
  ADR-worthy decision, not a silent choice.
