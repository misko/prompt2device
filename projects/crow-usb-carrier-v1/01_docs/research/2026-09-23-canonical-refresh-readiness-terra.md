# Canonical refresh readiness — composed Crow source

Reviewed root: `d71a01847bf002acb8df3746b929d37c2c243c75`. This is a
read-only execution plan: no producer, pin review, source change, PCB generation,
or campaign admission occurred.

## Readiness conclusion

One canonical regeneration is appropriate only after a single writer has adopted
a coherent, reviewed regulator/USB/floorplan/model source set. Do not compose a
canonical circuit while either isolated candidate is still provisional. The
normal (non-resume) arm of `03_src/rebuild_all.sh` is the conductor: its
`--resume-after-schematic-review` arm is invalid after either TSX, footprint,
parts, floorplan, rules, connector contract, or source-model change.

The present canonical `03_tscircuit/build/circuit.json` is
`cf78dcb8…`, and `power_tree.yaml` binds that exact raw hash through
`external_source_fuse.circuit_sha256`. It is stale evidence for a changed
composed source, rather than usable input for the next build.

## Finite execution order after adoption

1. **Close source composition before the conductor.** Merge the reviewed
   TPS62822 DLC candidate, the USB4215 candidate, the island reservation and
   landed library/model repairs in one source transaction. Resolve shared
   `floorplan.yaml`, `route.yaml`, connector-contract, parts, TSX,
   `parity_padmap.txt`, exact-parts CSV, and power-rule edits together.
   Re-check that the USB footprint's aliases, edge datum and connector contract
   all name the same replacement.
2. **Make the source inventories internally coherent.** The TPS62825
   directories that are no longer selected after the three DLC substitutions
   are retired dossiers, not an E-TOPO failure by themselves. Remove them from
   active selected/manifest/CSV inventories only when no composed TSX reference
   uses them; retain historical research in Git. An actual inconsistency is a
   surviving TPS62825 reference, stale DMQ footprint/pin mapping, or a
   `power_tree.yaml` rail still naming it while the selected parts inventory
   names TPS62822. The source E-TOPO census is the authority that must detect
   this, not a manual dossier deletion.
3. **Use the required two-stage E-FAULT bridge.** First, in an isolated
   composed-source view, produce and preserve the initial fresh producer
   Circuit JSON and its provenance; do not copy it over canonical `build/`.
   Independently compare its source-component, port, net, trace and internal-
   connection population with the accepted source intent, assess every real
   electrical difference, and retain the raw/semantic comparison receipt.
   Only if that assessment supports the exact candidate bytes may
   `external_source_fuse.circuit_sha256` advance to that raw digest. Then make
   that source edit before the canonical provenance stamp and run stage two:
   the canonical producer must reproduce the same bytes and E-FAULT must grade
   them. A raw digest update alone is never approval. If an eligible TSX input
   changes after stage one, preserve its initial artifact as evidence, repeat
   the semantic/electrical assessment for the new bytes, and restart the
   bridge; never copy an old `build/circuit.json` or weaken the digest check.
4. **Run the normal `03_src/rebuild_all.sh` once, through its schematic
   checkpoint.** Its source gates run
   first (connector source phase, module/RF, TSX preflight, source
   electrical/design/rules/layout/schema checks), then M-FRESH stamp, fresh
   `tsci build`, the required dist-to-build copy, diagnostics, E-FAULT,
   regenerated human PDF, M-FRESH verification, KiCad schematic conversion and
   netlist export. It then runs S-NETMERGE, E-INV/E-ADR, E-TOPO, E-MARGIN,
   E-OFF, count parity, electrical closure, selection/prelayout sourcing,
   ERC and the schematic checkpoint.
5. **Stop at the schematic-review boundary.** Fresh independent topology and
   human-readability witnesses must bind the new PDF, schematic, netlist,
   circuit, manifest and rule bytes. Existing schematic reviews and their
   accepted CJ/parts bindings become historical once the composed source
   changes. Passing reviews are necessary evidence for, but do not authorize,
   the subsequent campaign reassessment or conductor resume.
6. **Explicitly reassess the exhausted placement campaign before any resume
   or board generation.** The source and schematic reviews provide inputs to
   that decision; they do not themselves admit placement. The reassessment
   must state whether a fresh bounded campaign is authorized and which prior
   attempts, corrected source facts, connector holds and P1 defects govern it.
   A negative or incomplete decision stops here.
7. **Only after a positive reassessment, treat the generated board as a new
   placement candidate, not a repair receipt.** The resumed conductor performs native board generation, pin-map,
   connector FULL, placement/model/pad/DRC checks, rules/prep, and placement
   review prerequisites. The existing 19 connector FULL holds, fresh model
   coverage, corrected footprints/courtyards, USB edge/mate fit, and the
   island-exclusion geometry all need exact-board evidence. No routing or
   physical acceptance is implied by regeneration.

## Stale versus real blockers

The old canonical CJ, its matching E-FAULT hash, old generated schematic/netlist,
old placement trial, and prior human witnesses are stale dependencies after
source adoption. They are retained forensic/review records and should not be
rewritten or presented as current proof.

The source blockers identified by this plan are coherence of the final composed
inventory and a fresh semantic/electrical assessment bound to the stage-one
E-FAULT candidate digest. The isolated regulator candidate already recognizes
its electrical/pin/footprint/rule implications; the USB candidate has the
analogous alias/connector-contract implications. Neither candidate's isolated
success proves their combined source is coherent. A successful canonical
conductor will determine that under the existing gates; failure must return to
the owning source, not trigger an unreviewed P1 retry.

The untracked `03_tscircuit/dist/` in the root is producer output. It is not
adoptable source or a substitute for the conductor's fresh dist-to-build bridge.
