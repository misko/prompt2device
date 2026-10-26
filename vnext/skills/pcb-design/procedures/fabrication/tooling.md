# Adopt joined fabrication staging

The inherited StageSpec retains its external/network classification because
collecting stock/process evidence may use public sources. This adapter itself
only reads supplied observations and writes locally. Catalog cost/work-class
metadata is not authorization for vendor actions; no automatic dispatcher is
introduced, and the original graph dependencies and selection semantics remain.

Use after accepted layout and the user's phase resume. This local pilot joins
the existing [population](population.md) and [portable replay](native-replay.md)
components; it does not replace their native checks. Supported scope remains
flat, trusted local imported schematic producers and the layout adapter's native
non-RF boards. Read [imported tooling](../schematic/imported-tooling.md) before
running an unfamiliar producer. Unsupported geometry/processes require a new
implementation or evidence-led backtrack, not a fabricated pass.

## Adoption and commands

Create `01_docs/fabrication-contract.json` with version1, project-relative
`authority`, its `authority_sha256`, current `layout_receipt_sha256`, and
`board_quantities` mapping every board type to its positive integer build count.
The authority records phase resume, quantities and permitted local staging. It
does not authorize ordering, vendor communication or upload. Preserve historical
receipts when inputs change; explicitly adopt the new upstream result.

```
/usr/bin/python3 tools/fabrication.py build --project ABS --manifest REL --output NEW_REL
/usr/bin/python3 tools/fabrication.py verify --project ABS --manifest REL --output REL
/usr/bin/python3 tools/fabrication.py issue --project ABS --review REL
/usr/bin/python3 tools/fabrication.py check --project ABS
/usr/bin/python3 PACKAGE/tools/fabrication.py replay --package PACKAGE
```

Build/verify/issue/check invoke the current owning layout check, not just its
receipt hash. Build copies accepted native outputs and the schematic contract's
declared producer inputs. Output is atomic and must be new. `replay` checks the
portable artifact only; it cannot establish current upstream acceptance or grant
an engineering verdict. Internal `produce` exists for isolated fixtures and
cannot issue a receipt. A package's own modified verifier is not an authenticity
proof; eventual release provenance must bind the reviewed tools and files.

## Inputs

The version1 fabrication manifest has exactly:

- `population`: path to the existing population manifest, including its explicit
  assembly mapping (even when all factory/consigned reference sets are empty).
  Its source paths and quantities must equal the adopted final board outputs and
  counts. Native and intent bytes must match the joined schematic/PCB package.
- `sourcing`: path to the observations described below.
- `boards`: the exact board-type mapping. Each entry has `source_sha256`,
  `process`, `mechanical_views` and `instructions`. The latter two are nonempty
  lists of retained project-relative files. Retain actual dimensioned/mechanical
  views, not a text claim that they exist. Instructions cover assembly sequence,
  manual/consigned modifications, exclusions, inspection and installation.
  Evidence presence is checked mechanically; independent review judges adequacy.
  `process` has `copper_layers`, `thickness_mm`, nonempty string-valued
  `selections`, and nonempty `evidence`. Layer count/thickness must match the
  native source; selections state the applicable fabrication/assembly process
  and its retained authority. They are planned selections, not invented uploader
  confirmation. Electrical stack soundness must already be closed at layout.
- `handoff`: nonempty retained files carrying original scope, upstream closure,
  remaining first-article/deployment qualifications and downstream obligations.
  Do not turn a known design contradiction into a test obligation.
- `order_holds`: list of `{id, reason, evidence}` records; IDs are unique and
  evidence is nonempty. Keep actual uploader choices and manual/consigned
  handling explicit. The tool always adds assembly verification, vendor
  matching/orientation/allocation, actual process confirmation and release
  review/seal holds, plus manual/consigned handling, execution and inspection
  confirmation when those modes occur. It cannot produce order-ready status.

Sourcing version1 contains ISO `as_of` and `parts`. Each part has exact
`manufacturer`, `mpn`, nonempty `package`, total `quantity`, `contributors`
(`{board, reference}` for every populated instance on one board of that type),
nonempty `jlc_evidence`, and `offers`. Identity coverage and summed quantities
must account for each declared board type's build count, including manual parts and excluding
justified DNP/mechanical items. Do not multiply every board by one common count.

Each offer uses the existing part-recheck facts: exact manufacturer/MPN/package,
`supplier_url`, `checked_on`, `in_stock`, optional `stock_count`, optional lookup
quality fields, plus nonempty retained `evidence`. One adequate exact offer is
sufficient. In-stock without a published count is acceptable; a published
insufficient count is not. Weak snapshots, failed/unverified lookups and identity
mismatches cannot qualify. Dates must not postdate `as_of` or the current date.
If supplied, `availability_verified` must be a JSON boolean; false cannot qualify.
An optional `lookup_state` qualifies only as `verified`; discovery/identity-only,
failed, stale and unverified states are retained but do not qualify. Unknown
states fail validation. Optional evidence/source kinds are `supplier_page`,
`exact_supplier_page`, `aggregate_snapshot` or `search_snippet`; the latter two
never qualify. Omitted quality annotations preserve the established exact-offer
schema, but do not remove the reviewer's obligation to inspect the actual page.
No generic stock freshness interval is invented: the independent sourcing review
must judge the retained observation's date and authenticity for this staging run.
The tool does not browse or reserve stock. Follow the existing JLC-first bounded
[part recheck](../part-recheck.md) when collecting observations; escalate a short
unsuccessful search to the user rather than silently substituting parts.

## Independent admission and recovery

Retain exactly one fenced JSON block in `08_reviews/YYYY-MM-DD-name.md`, matching
the existing review reader. Review JSON follows exact-subject conventions: schema1,
stage `JLC-FABRICATION`, distinct `author`/`reviewer`, manifest/output paths,
verdict PASS and subjects mapping every source/evidence/package file from
`verify` to its hash. `checks` has exactly `source`, `population`, `sourcing`,
`process`, `mechanical`, `instructions`, `handoff`; each needs PASS, substantive
rationale and retained cited evidence. These are engineering judgments, not
exporter-supplied checkboxes:

- Source: all board types, native plots/drills/PDFs and portable circuit replay.
- Population: actual per-reference identity/exclusions, whole-system counts,
  separate factory/consigned files, evidence supporting supplied centroid/datum/
  rotation mappings. Detailed mounted-body/fit/polarity acceptance is owned by
  assembly verification, not inferred from successful CSV translation.
- Sourcing: exact offers, measured demand, dates and JLC-first observations.
- Process: actual native measurements and applicable process constraints; no
  unsupported stack assumptions or false claim of uploader confirmation.
- Mechanical: actual source-bound dimensioned/mechanical views for every board.
- Instructions: executable handling and inspection, including manual/consigned
  modifications and DNP rationale. Do not imply modifications were performed.
- Handoff: preserved engineering/qualification distinction and explicit holds.

The source check must cite each board's schematic/PCB PDFs, exact Gerber/drill
ZIP and imported replay receipt, plus `fabrication.json` and `native/bundle.json`.
Population cites the generated CSVs and policy/mapping evidence; sourcing cites
retained observations, not only the summarizing JSON. Manual/consigned/DNP policy
evidence belongs in instructions too. Mechanical/process/instructions must cite
every board's declared evidence; handoff must include declared holds. A reviewer
must actually inspect these artifacts: citations are enforced coverage, not proof
of the judgment's truth. The certificate binds relevant guidance and tool bytes.

`issue` creates `06_build/checkpoints/fabrication_staged.json` exclusively after
replay and independent review; it never overwrites or renews a receipt. `check`
repeats the same predicates on exact subjects and tools. The next owner is
`JLC-ASSEMBLY-VERIFY`; stop at the user's checkpoint. DO-NOT-ORDER remains.

On failure the orchestrator records cause and affected dependents: export/policy
defect returns here; stock substitution to sourcing and its circuit consumers;
native markings/mechanical document errors to layout; actual copper/stack or
circuit changes to routing or schematic. Preserve accepted history and spent
attempt budgets. Regenerate derivative files from their owner, never patch an
export or refresh review hashes merely to obtain PASS.
