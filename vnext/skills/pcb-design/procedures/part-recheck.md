# New or changed part — design availability recheck

New whole-system exploration runs may draw provisional components in marked
unaccepted drafts. Critical availability screening still applies; this full
guard applies when adopting an exact part for dependent implementation and at
final sourcing acceptance, with common-passive timing below. It is not a
prerequisite to drawing or repairing generic passive positions. This policy
does not silently change old project bindings or accepted evidence.

## Common passives: design now, source at the end

During schematic development, specify common resistors and capacitors by value,
tolerance, voltage/power rating, technology and package, not mandatory exact MPN.
Keep them in the existing circuit/BOM source; do not open a stock-search task or
user substitution prompt merely to fill these identities. An unavailable draft
MPN may revert to an explicit generic requirement without changing the circuit;
never leave its old availability claim attached. Retain earlier research for
reuse, but it must not force early exact-part selection.

At the final BOM/sourcing check, batch-select and verify exact stocked parts
against those requirements before schematic acceptance or placement. A generic
position is not `checked` and cannot satisfy exact-part sourcing admission.
There is no new stage or per-passive review gate.

Regression tests must accept both generic development positions and valid exact
final identities while enforcing the same electrical requirements. At final
sourcing, generic/unverified identities must fail. Do not encode a draft's lack
of MPN as an invariant, or hard-code one board's preferred MPN in generic tests.

Deferral is about exact-part procurement qualification, not electrical design.
Check feasibility-critical properties when consumed: effective capacitance/ESR
for regulator stability or hold-up, timing accuracy, precision matching,
protection pulse energy, and unusual package/voltage/power constraints. An
ordinary bypass or pull resistor normally stays generic. A passive whose
specific construction determines feasibility needs evidence then, even if its
nominal value is common. Use the existing engineering review; do not turn every
passive into a special case or demand guarantees beyond the circuit requirement.

The exact-part helper below still evaluates exact supplied subjects only; do
not call it for a deliberately generic passive or fabricate a dummy MPN.

PCB-owned cross-stage guard, including commissioning proposals and repairs.
Before starting dependent part-specific pin/footprint/interface integration,
the coordinator compares the proposed exact manufacturer, MPN, package,
quantity per assembly and assembly count with the last checked subject.
A new identity or any quantity change starts `provisional`; old checks do not
transfer even when the total happens to be unchanged. Abstract topology work
and unrelated tasks can proceed; mark unverified candidates explicitly.

For a new design, screen manufacturer lifecycle before investing in a detailed
candidate. Prefer active/current-production parts; do not carry NRND, EOL or
obsolete parts into the default design without an explicit project exception.
Record the dated manufacturer status and any conflicting supplier status in
the candidate report. Unknown lifecycle is not proof of active production.
Remaining stock can clear availability without resolving lifecycle suitability;
keep those conclusions separate. The helper below evaluates availability only.

Calculate build need = quantity per assembly × assembly count, including all
repeated assemblies. State additional authorized spare/attrition needs if any;
do not invent them. If the quantity basis is unknown, resolve it before claiming
`checked`. Record subject and arithmetic in the candidate report, not a second
parts ledger. Exact maker matters: a same-named part from another maker or a
different package is not evidence for this candidate.

Check JLCPCB first, then make a brief Western fallback search if needed. Retain
the dated supplier product URL, exact identity/package, explicit present-stock
statement and count when published. An exact matching in-stock page with count
unknown is sufficient for design availability. A published count below build
need is not sufficient, even with an in-stock badge. Incoming/backorder counts
are not present stock. Do not sum duplicate storefront inventory. One adequate
supplier suffices; there is no two-distributor requirement or default minimum
inventory cushion. Follow explicit project overrides, surfacing conflicts.

### Concrete lookup route

From this vNext package root, use the read-only structured discovery adapter:

`python3 tools/stock_lookup.py EXACT_MPN --need BUILD_QUANTITY --output /absolute/new-observation.json`

It calls `https://jlcsearch.tscircuit.com/api/search?q=...&limit=5`
([API documentation](https://github.com/tscircuit/docs/blob/main/docs/web-apis/jlcsearch-api.md)),
retains returned data, retrieval time and response hash, and matches the full MPN
without dropping suffixes. API `mfr` is the MPN, not the maker. Check manufacturer
and package on the exact supplier page; do not assume aliases match automatically.
An empty result means no exact match in this search, NOT zero JLCPCB inventory.
The result is bounded to five hits, not an exhaustive catalog search. Keep exact
matching even when the service returns unrelated rows; never accept the first hit.

Use an observed public JLCPCB product URL for confirmation, optionally passing
`--jlc-url URL` to collect exact-identity page fields. This lightweight extractor
fails closed if the page format changes; it does not certify stock. Do not guess
search URLs or interpret page navigation's generic "In Stock" text as an offer.
Keep overseas stock, presale quantities and PCBA stock distinct. Do not sum them.
The aggregate count is a discovery snapshot: retrieval today does not prove the
underlying inventory was updated today. An explicit exact supplier in-stock
statement still suffices under the policy above; an unpublished count stays null.

Bound lookup recovery to this API and one exact supplier-page check, then the
brief Western fallback. Preserve separate outcomes: reported sufficient stock,
reported insufficient/zero stock, no exact match, stale evidence and failed
lookup. A timeout, inaccessible page or unknown inventory is not unavailability.
If unresolved, ask for help verifying availability, not substitution as a proven
necessity. Existing user-approved candidate authority is unchanged.

For `part_recheck.py`, mark `check.lookup_issue` as `lookup_failed`, `stale`,
`no_exact_match` or `inventory_unverified` when that is the remaining obstacle;
it remains provisional with `resolve_lookup_evidence`, even after a fallback
search. Do not set this field to hide confirmed insufficient stock. Annotate
snapshot/snippet offers with `evidence_kind=aggregate_snapshot/search_snippet`;
they cannot clear the guard. A verified independent adequate supplier can still
clear it. These fields qualify evidence; they do not replace the exact identity,
quantity, lifecycle or engineering review checks.

- `provisional`: check missing, stale, identity/quantity unresolved or bounded
  search still underway. Hold this candidate's dependent integration.
- `checked`: exact current subject has adequate dated availability evidence.
  Only this sourcing guard clears; electrical review and existing phase holds
  remain binding. This does not mean accepted parts, assembly allocation or
  order approval.
- `needs_user_decision`: short search finished without adequate evidence,
  including known insufficient stock. Stop searching and ask the user with the
  exact part, build need, observations and options (for example authorize
  qualification of an equivalent, change quantity or defer). Do not substitute,
  procure, or continue affected integration while waiting.
  If the obstacle is a lookup failure or unverified inventory, retain provisional
  and escalate that evidence-access issue instead of asserting a stock shortage.

Append the trigger, previous/current subject, state, dated observations, affected
task/artifact IDs and next action to the existing stage journal through its
coordinator. Preserve failed attempts and accepted history. On a changed subject,
reopen only its affected architecture interfaces and transitive dependent
schematic/review evidence; unrelated work remains accepted. A fresh availability
check alone cannot reaccept those engineering artifacts. A user-approved
substitute starts another provisional check and the applicable electrical review.

Optional deterministic check from the package root:

`python3 tools/part_recheck.py /absolute/candidate-facts.json`

The JSON carries `part_id`, `subject` (manufacturer, mpn, package,
`quantity_per_assembly`, `assembly_count`), optional `check` (the same `subject`,
`jlc_checked`, `western_search_complete`, `offers`), and `dependencies`
(artifact/task ID → IDs it consumes). Offer fields are `manufacturer`, `mpn`,
`package`, `supplier_url`, ISO `checked_on`, boolean `in_stock`, and nullable
integer `stock_count`. The helper covers repeated identical assemblies only;
if mixed assembly types or separately specified spares change the total, record
and check that complete aggregate manually instead of understating it here.

This read-only helper evaluates supplied facts and returns state, next action,
build need and affected dependency closure. It does not browse, discover changes,
verify page truth/freshness, infer dependencies, edit records, approve circuits
or admit a stage. The coordinator owns those checks; retain the observation date
and assess whether a new lookup is needed before reuse. `tools/task.py` hashes
this instruction in every supported task packet, but remains disclosure only.
Graph guard metadata is procedural routing, not an executable scheduler. No
unsupported production stage becomes executable through this guard.
