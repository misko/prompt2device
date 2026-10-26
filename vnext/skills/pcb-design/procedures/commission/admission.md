# Review upstream stage admission

This local route uses the independently reviewed upstream verifier and negative
controls. It is not a schematic-production route or an engineering verdict.
Keep the existing commissioning hold until commission, architecture and sourcing
are each accepted. Reports alone are not adopted source.

Use a dated independent Markdown review under `08_reviews/` and a generated
certificate under `06_build/checkpoints/`. These are evidence, not another
progress ledger. STATUS and the stage journal retain execution history.
The reviewer consumes exact adopted source and primary part facts, not an
author's assertion of readiness. Do not let the producer write its own verdict.

| Stage | Required review criteria | Minimum adopted subjects |
|---|---|---|
| PCB-COMMISSION | scope, input_envelope, applicability, qualification_boundary | BRIEF.md, capability-profile.json, rules/requirements.yaml |
| PCB-ARCHITECTURE | power, analog, digital, external_interfaces, budget, integration | ARCHITECTURE.md, DETAIL_DESIGN.md, rules/power_tree.yaml, rules/integration.yaml |
| PCB-SOURCING | exact_identity, pin_facts, availability, assembly, cost | sourcing/exact-parts.csv, every selected part.yaml and retained datasheet, sourcing policy ADR, root contracts.md, schematic-contract.json, capability-profile.json |

Paths above are relative to their ordinary `01_docs/` or `03_src/` homes.
Commission requires the preserved original prompt hash and a current agreed
brief with explicit bounded assumptions; unknown adapter identity is not proof
of compatibility. Architecture adopts reviewed choices into source/rules and
assigns physical qualification obligations without claiming measurements.
Sourcing applies the skill's current design-stage policy, not old two-pool
counts; the exact parts table must cover every required board type and its
instance quantities, including a single-board design when that is the scope.
Supply identity, assembly route and system budget are different questions.
Keep all required review criterion keys. For a concern that does not apply,
review its non-applicability against cited project evidence and explain that
disposition in the rationale; do not invent circuitry or treat unknown as absent.
The existing PASS/FAIL schema is unchanged: PASS means the criterion was reviewed,
not that every project contains every possible subsystem.

For a bootstrapped project, preserve BRIEF's exact path/SHA-256 provenance
entries and bind the original raw prompt, chronological decisions and capability
file as review subjects. No inline copy of the prompt is required. The intake
scaffold is not ready for admission: reconcile it and explicitly set the brief's
status before review. The verifier permits `agreed` or `in-progress` as lifecycle
labels; neither substitutes for the independent review's agreed scope and bounded
assumptions. Legacy inline provenance is supported only when no raw-input project
is present. Review the journal/source history before changing provenance modes.

The machine-readable review block is schema 1 with stage, author, reviewer,
verdict (`PASS` or `FAIL`), subjects (project-relative path to SHA-256), and
checks (the exact stage criterion keys, each with verdict, evidence paths and
nonempty rationale). The author and independent reviewer identities must
differ. Every referenced file is reopened and hashed; no path escape, missing
subject, empty evidence, failed criterion or changed input can pass. Identity
strings record independence; they do not cryptographically authenticate it.
The coordinator preserves the actual review provenance in the journal.

Every mandatory source must appear in the criterion evidence, not merely the
subject hash list. This minimum coverage is structural; the independent reviewer
still owns relevance, source sufficiency and physical reasoning. Exact-parts
tables use an explicit MPN column when present; Comment is only a compatibility
fallback, not an override for an explicit identity.
Use a `Dossier` column with the project-relative `02_parts/.../part.yaml` path
when an exact MPN contains path punctuation, or to separate identity from storage.
When that column exists every row must supply it; without it the historical
`02_parts/<MPN>/part.yaml` convention remains. Do not sanitize the MPN itself.
The dossier and its retained PDF still require exact-subject independent review.
Sourcing's assembly criterion must explicitly cite the root project contract,
schematic declaration and capability profile. The same declaration validator
runs here and at schematic dispatch, including supported producer and RF scope.

Certificates bind exact review bytes, subjects, verifier/instruction identities
and prerequisite certificates. Revalidation recursively reopens prerequisites
and current evidence. Commission has no predecessor; architecture requires
commissioned_brief; sourcing requires architecture_locked. Emit distinct graph
output roles, never infer a stage pass from STATUS or a missing hold.

Tests must reject stale subjects/reviews/prerequisites, missing criteria,
self-review, path escapes, empty coverage and a missing required source. A
passing verifier checks evidence completeness/freshness; independent engineering
review owns physical reasoning. No purchasing, placement or schematic production
follows until its own local stage contract is runnable and prerequisites pass.

## Execute on reviewed project source

Architecture reviews bind every JSON/YAML file under `03_src/rules/` as a
subject, including their transitive source references, and cover them in the
applicable criterion evidence. Live `path` references
and optional JSON `pointer` values resolve against that snapshot; do not embed
SHA-256 in references to other live `03_src/` files. Keep hashes for immutable
research/history and in external review/task maps. `tools/source_snapshot.py
--project /absolute/project` emits a candidate `subjects` map (requires PyYAML);
`--check snapshot.json` revalidates membership, content and explicit references.
Architecture admission runs the same check. Neither command supplies engineering
verdicts nor verifies all connectivity. Preserve old source and obtain owning
review on migration; changed instructions do not automatically upgrade receipts.

The coordinator first binds the project contract and instruction snapshot to
this route; do not silently apply it to an older frozen research-only project.
Prepare the required source and obtain the independent review above. On FAIL or
missing evidence, use orchestrator recovery; do not generate a substitute PASS.
After a PASS, issue and revalidate its exact role using the local tool:

```sh
python3 tools/admission.py --project /absolute/project issue --review 08_reviews/YYYY-MM-DD-review.md --out 06_build/checkpoints/ROLE.json
python3 tools/admission.py --project /absolute/project check --certificate 06_build/checkpoints/ROLE.json
```

ROLE is `commissioned_brief`, `architecture_locked` or `parts_locked`, in that
order. The coordinator is the promotion consumer: only after both commands
succeed, record the role, review/certificate identities and next permitted task
in the existing journal/status. Never infer a role from STATUS alone. Keep the
hold until all three roles are current; even then schematic production waits
for its own runnable route and project contract. Do not run a legacy gate.

Issuance refuses an existing receipt. On source repair, preserve the old review
and receipt in dated evidence history before issuing replacements at canonical
paths. Revalidate dependent roles recursively; a new parent does not automatically
reaccept its children. Do not change a review's verdict or hashes on its behalf.
