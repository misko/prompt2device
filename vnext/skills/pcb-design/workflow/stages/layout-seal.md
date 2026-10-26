# KICAD-LAYOUT-SEAL — finish, verify and freeze the complete layout

Local native-source pilot. After explicit resume from routing reflection, read
the [tooling contract](../../procedures/layout-seal/tooling.md). Preserve the
accepted routed boards and their toolchain. This stage produces `layout_sealed`,
not fabrication payloads, ordering authority or a release.

## Complete candidate and acceptance

Start with all board types and the current owning routing receipt. Capture
inherited engineering obligations with their requirement authorities before
finishing: stack/material assumptions, loading or other deferred design proof,
and manufacturing/marking constraints relevant to this layout. Distinguish a
chosen design stack from a fabricator's actual process commitment. A nominal
model or clean DRC does not close a missing physical/electrical proof.

Produce one complete finishing candidate: readable board identification,
connector/polarity/orientation markings, usable assembly references, retained
native libraries/settings, individual layers and assembly views. Repair related
marking problems together, not a new pipeline per warning. Local libraries must
retain provenance; a snapshot of authored footprints is not proof of agreement
with a manufacturer's land pattern.

The pilot permits only non-copper silkscreen/Fab/document presentation changes.
Reference/value identities remain fixed. Full pads, positions, copper, zones,
mask/paste, courtyards, models, stack/setup and rules stay unchanged. An explicit
layout comparison and new independent markings review replace only the cosmetic
portion of the old identity for this downstream candidate; old receipts are not
rewritten. Unknown or engineering changes return to the appropriate owner.

Require strict fresh DRC with zero findings, zero opens, no ignored checks or
exclusions; exact source/output replay for every board; independent review of
markings, identity, manufacturing geometry and every inherited obligation. A
build may report incomplete work. Only owning `issue` then `check` accepts it.
Do not hide all references or suppress warnings to obtain a pass. Physical fit,
order-day checks and first-article measurements remain separate claims.

New final acceptance also requires explicit native schematic-to-PCB parity with
the exact schematic present. Keep original native net namespaces and isolated
no-connect identities through placement/export, and classify true board-only
mechanical footprints at source. A blank parity field without the CLI comparison
does not qualify. `tools/native_parity.py` produces diagnostic evidence; admission
must bind/replay it before this upgraded requirement is considered implemented.
The layout adapter's version2 contract now binds and replays that comparison for
the adopted flat imported producer. The [portable replay component](../../procedures/fabrication/native-replay.md)
version2 independently repeats it downstream. Neither operation bypasses this
stage's upstream re-adoption or independent review; historical receipts remain
bound to their original toolchain and do not gain this coverage retroactively.

## Recovery and checkpoint

Use the existing orchestrator, journal and retry history. Cosmetic failures stay
here; copper/return failures reopen routing; component geometry reopens placement;
circuit/part contradictions reopen schematic/sourcing. Stack changes require
affected electrical revalidation, even when connectivity is unchanged. Preserve
the last accepted board while evaluating alternatives. Stop for missing external
authority or evidence; a user preference cannot substitute for engineering proof.
At acceptance, record phase reflection and stop before fabrication preparation.
