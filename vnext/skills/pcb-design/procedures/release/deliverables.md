# Recipient-facing release contract

Use at staging, independent review and seal. This is an output/evidence contract,
not another execution graph. The existing orchestrator and stage owners remain.

## One discoverable package

Provide a root index with the release/version, every board/version/quantity,
current design and order verdicts, source/seal provenance, and direct links to
the editable native entrypoints, PDFs, fabrication files, 3D assembly and checks.
Group by board and artifact role; never require knowledge of recovery-attempt
names to find the authoritative schematic or PCB. Convenient copies must match
the retained authoritative bytes and remain in the complete hash inventory.

Make one record authoritative for current status. Retained draft/review snapshots
must be labeled historical and linked to the current acceptance, not presented
as competing live status. No self-referential hash cycle is required: a later
acceptance record may bind an earlier candidate manifest, and the final seal
binds both. Validate the relationship and the human index, not just each file.
Do not rewrite a previously sealed snapshot to make its status look current.

## Required roles per board

| Role | Required evidence/artifacts |
| --- | --- |
| Editable design | Native schematic, PCB, netlist, settings/libraries, author source and reproducible tools |
| Human documents | Schematic PDF, layer PDF, readable assembly drawings and reference locator when needed |
| Fabrication | Copper/mask/paste/silk/outline, PTH/NPTH, Gerber ZIP, separate BOM/CPL and population policy |
| Mechanical | Registered populated STEP, six 3D views, same-camera bare top/bottom, applicable mating closeups/sections |
| Assembly checks | Nonzero mounted-model coverage, per-reference identity/registration, body/board/access collision and clearance reports, polarity/rotation/lead or hole fit and substitution limitations |
| Electrical/layout checks | Fresh ERC and all-severity DRC, explicit final native schematic parity, source/export identity and complete connectivity/NC accounting |
| Engineering reasoning | Indexed design calculations and bounds, inherited assumptions and current deficiencies; links to actual derivations rather than verdict summaries |
| Supply/assembly data | Exact maker/MPN and supplier mapping, observed quantities and dates, population exclusions, manual/consigned instructions, machine BOM identity and encoding/legibility checks |
| Independent review | Exact-subject pin, schematic/render readability, topology/ratings, layout/power, mechanical/assembly and integrated completeness judgments |
| Reproduction | Complete inventory/hashes, tool/runtime versions and isolated standalone replot/recheck evidence |

The final native parity run must actually execute with both native files present;
an empty report field without `--schematic-parity` is not evidence. An alternative
comparison requires independent acceptance of equally complete reference, value,
footprint, pin/net and isolated-NC coverage, not merely matching net counts.

Use explicit review-scope records tied to actual board/reference/artifact
denominators. Initial release review assigns independent focused engineering
lenses for pin/electrical, visual/mechanical, and layout/power, followed by
integrated completeness. They may share a packet and produce one indexed report,
but must not disappear into an unscoped generic PASS. Delta reviews justify
inherited coverage from unchanged exact subjects and review all affected scopes.

BOM checks reopen the actual CSV, compare per-reference maker/MPN/value/package/
supplier codes against retained authorities, test quoting and the destination's
declared encoding, and reject omissions, substitutions or unreadable text.
Do not imply a vendor matched a part merely because our own parser accepts it.

## Separate order and publication boundaries

Expose every active order hold on the first screen, with evidence and a closure
owner/action. Actual allocation, uploader matching, vendor rotation preview,
consignment acceptance, fabrication process selections, assembly capability and
purchase authority remain order-time requirements. Firmware and physical first
article/qualification remain separate unless included in the user's goal.

Publication additionally checks the intended repository delta, complete release
inventory and third-party redistribution rights. A sound local design release
does not authorize upload, supplier messages, ordering or pushing to main.

## Verification and migration

Test the package as a recipient: from the index open both native designs and
their real images; re-export fabrication and compare; reopen populated STEP;
inspect substantive reviews and unambiguous status. Negative controls must reject
missing boards/roles, stale/misbound models or reviews, incomplete coverage,
contradictory statuses, changed source/fabrication and extra unlisted files.

This is the upgraded contract. Version1 remains historical; version2 is an
explicitly adopted pilot with these additional roles. Explicitly record the
migration in the graph/project status; a new instruction file alone is not a pass.
