# PCB-RELEASE-REVIEW — judge the complete staged release

New releases must satisfy the [recipient-facing deliverables](../../procedures/release/deliverables.md),
including registered 3D artifacts, explicit native parity, complete indexed
review scopes, BOM readability/identity and an unambiguous current status.
The v1 adapter remains historical; the explicit v2 pilot implements upgraded
roles and runtime packaging but requires complete archive replay and independent
admission. Do not equate component tests or an earlier receipt with new acceptance.

Local execution pilot: explicitly adopt the [archive/review tooling](../../procedures/release/tooling.md).
Requires
`assembly_verified` plus applicable RF fabrication clearance. Explicitly exclude
RF stages only from a verified non-RF applicability contract. No graph edge or
STATUS beacon substitutes for the owning acceptance evidence.

Prepare a self-contained mutable archive, attributed to each board/version:
`fab/`, `pdf/`, `source/`, `verification/`, mechanical exports where available
(otherwise a justified absence), order instructions and complete manifest.
Include the exact authoring source/tool dependencies, schematic/netlist, board,
libraries/settings, process/assembly policy and all substantive review evidence.
No links back into mutable work directories. Reopen/replot/DRC from the archive
offline and compare to its actual manufacturing payload.

Initial release review covers pin identity, readable schematic/render,
topology/ratings, layout/power integrity and integrated completeness on exact
staged subjects. Fresh independent reviewers own verdicts. A fix-pass scopes
reviews to changes plus one integrated fresh lens; preserve invalidated history.
Require explicit design verdict SOUND/DEFECTIVE/INCOMPLETE and a separate order
verdict. Unknown or contradictory design evidence prevents SOUND.

Order holds may coexist with sound design, but must be visible in the manifest
and first screen of order instructions, backed by actual evidence, with a named
closure action. Do not invent unavailable stock or hide a missing design proof
under DO-NOT-ORDER. Local tests must reject missing boards/files/reviews,
stale evidence, ungraded denominators and source/fab identity changes.

Only a current independent review of the complete archive can produce
`release_reviewed`. Next: [release seal](release-seal.md).
