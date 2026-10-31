# MacBook handoff — complete JLC quotation, no purchasing

**Current scope, OR13:** use `quote-draft/r3-1c8p-home/README.md` and its unsent
`JLC-SUBMISSION-NOTES.md` on `codex/crow-jlc-source-review-20261030`. Target is 1 carrier
and 8 pods; 5+8 is a separate unapproved comparison. All THT/Pico/acoustic parts
are home-installed. The older 5/10 and JLC-manual instructions below are
historical and must not be applied to the current job. No purchases or automatic
submissions. R3 publication is authorized; its README contains the current
MacBook continuation and copyable prompt. Verify with `home_assembly_plan.py verify`.

## Historical OR12 handoff — do not execute for the current scope

**OR12 update, 2026-10-31:** quote-only files are now prepared and locally
validated at `quote-draft/r1-20261031/`. Start with that folder's README and run
`python3 -B projects/crow-array/order-readiness/quote_files.py verify`.
Do not rebuild the prepared packet or repeat stock research. Section 1 below
describes its derivation/revision requirements; next action is section 2's
manifest/permission boundary, then the non-binding quote flow. Full BOMs include
manual operations not in SMT CPL; the packet README explains the SMT-only
alternative and mandatory separate manual pricing. No JLC ingestion is claimed.

Prepared 2026-10-31 PDT. This replaces the completed availability/pricing passes.
Goal: one itemized, non-binding quote package for **five carriers and ten pods**,
with explicit exceptions. Do not repeat broad stock research. No payments,
parts purchases/reservations, manufacturing commitments or substitutions.

## Start from the current branch

Repository `misko/prompt2device`, branch
`codex/crow-jlc-source-review-20261030` (not main). Check `git status` before
updating. In a clean checkout already on that branch:

```sh
git fetch origin codex/crow-jlc-source-review-20261030
git merge --ff-only origin/codex/crow-jlc-source-review-20261030
```

If the Mac checkout is dirty/incomplete, preserve it and use a fresh sibling
clone into an unused directory; do not reset it or commit missing-file deletions.
Read local vNext PCB/orchestrator entrypoints and resume instructions, then
`STATUS.md`, `PROCUREMENT-PROPOSAL-20261030.md` and its 38-row CSV beside this
file. Use OR9's pricing evidence and OR7's named identity reconciliations.
Dates and limitations remain attached; observations are not reservations.

## 1. Prepare and check quote-only files locally

**The proposal CSV is not an upload BOM. Released factory BOMs are empty.**
Prepare new drafts under `projects/crow-array/order-readiness/quote-draft/`
(use a new revision directory if it already exists); never edit the release.
Before deriving assembly data, read the applicable local vNext assembly
contract and source population policies. This is quote preparation, not a new
engineering acceptance or permission to regenerate the board design.

Input release root:
`projects/crow-array/releases/crow-prototype-v3-first-run-5c10p-public-v1/`

| Quote input | Retained source under release root |
|---|---|
| Carrier fabrication | `fab/carrier/carrier-gerbers.zip` |
| Pod fabrication | `fab/pod/pod-gerbers.zip` |
| SMT references/placements | `fab/assembly/carrier-consigned-bom.csv`, `carrier-consigned-cpl.csv`, and corresponding `pod-` files |
| Complete population/locations | `fab/assembly/population.csv`, `demand.csv`, `positions.csv` |
| Process limits and open holds | `README.md`, `historical/ORDER-INSTRUCTIONS.md`, retained assembly evidence |

Derive separate carrier/pod BOM and SMT CPL quote drafts plus a manual-assembly
schedule and a short manifest of source hashes/files/settings. Preserve native
position, side, rotation, units, datum and refs; catalog codes come from the
reviewed proposal, not guessing or suffix stripping. Verify against native
boards before calling drafts reviewed. Do not treat economic/standard defaults
or a vendor file preview as acceptance of the source requirements.

Keep procurement route distinct from installation method: a Global Sourcing
ADC remains SMT, while a Global Sourcing RECOM remains manual/THT. Do not omit
unavailable parts or silently replace them to make a quoting screen proceed.
If a manual part must appear in a vendor BOM, retain its manual designation;
never fabricate a machine CPL position to force a match.

| Installed scope | Carrier batch (5) | Pod batch (10) |
|---|---:|---:|
| JLC SMT | 635 | 280 |
| JLC RJ jacks | 40 | 10 |
| JLC power jacks | 5 | 0 |
| JLC RECOM modules | 5 | 0 |
| User Picos | 5 | 0 |
| User microphones + buzzers | 0 | 20 |

Checks: 1,000 installed parts = 975 JLC + 25 user; exact refs once each; no
user/manual parts in machine CPL; no accidental DNP; manual operations explicitly
priced; preserved user-installation paste/hole exclusions. Retain the original
915-SMT process classification pending compatible CTS installation review.
Document vendor-specific adjustments as reviewed draft differences, never edits
to released bytes or automatic acceptance. An unresolved mismatch blocks upload
of affected files; it is not a reason to restart the whole design.

## 2. One explicit quote-session boundary

Present the validated file manifest and intended actions to the user before
external upload/submission. Current instruction prepares/publishes this workflow;
it does not itself perform those actions. Ask once for scoped authority to upload
the listed files and use non-binding quote drafts for these two jobs, including
temporary carts only if required and expressly permitted. User handles login/MFA.
Do not ask for payment details. Distinguish a quote draft from an order submission.

After that authority, use the normal signed-in quote flow for five carriers and
ten pods. Record PCB settings from the retained release (including carrier
7628A / pod 7628 construction requirements), actual quantities and selected
services. If JLC cannot match those requirements, report the mismatch and a
conditional estimate; do not pick a different stack/process silently.

Use 28 catalog candidates + five regular replenishment lines + Global Sourcing
of exact RECOM R-78E5.0-0.5 and PCM1864DBT. Capture final quantities/packing for
each job. RECOM's observed minimum is 10 for five installed; ADC installed need
is 10 before any assembly allowance. The prior $227.71 is only the seven-line
benchmark; do not add it again if JLC's quote already includes those components.

Inspect exact part matching and placement previews, including pin-1/polarity,
side and rotation. Collect manual-installation scope, exclusions, stencil and
stack/rails/DFM compatibility. Existing mechanical/controlled-assembly holds
remain explicit, not waived by a priced quote. Do not reopen the user-accepted
Pico-fit risk without new contrary evidence.

## 3. Capture the complete cost and schedule

Return separate carrier, pod and shared procurement columns:

| Cost bucket | Required evidence |
|---|---|
| Bare boards | Actual 5/10 quantity, settings, unit and extended prices |
| Setup / stencils / feeders | Each charge and which job it belongs to |
| Components | All 35 JLC identities; installed versus purchased quantities; route, packing, attrition and surplus |
| Assembly | SMT plus all 60 requested manual operations; any excluded operation clearly named |
| Procurement extras | Replenishment/global fees, duties, deposits and whether included elsewhere |
| Delivery / tax | Destination-dependent shipping, currency, tax, expiry and exclusions |
| Schedule | Parts-ready date/range, PCB/assembly duration and final shipping separately |

No mixed-currency totals, assumed zero fees, shared-stock double counting or
double charging of minimum-order surplus. Distinguish refundable deposits from
permanent costs. Ask the user for delivery country/postal code if required;
keep personal addresses/account details out of Git. User-installed parts are
outside JLC's quote: report their separate procurement status, never assume
they are free or already owned. Enclosures/roof supports remain outside scope.

Stop before payment, stock reservation, purchase or any manufacturing commitment.
Do not buy parts to unlock an assembly quote. If JLC requires prepayment or owned
inventory first, preserve the available partial quote and label the missing
costs/arrival dates. Do not describe it as complete. Do not send supplier support
messages without separately scoped authority; save a focused exception instead.

## 4. Return one package and stop

Save a new dated `JLC-QUOTE-YYYYMMDD.md` plus structured observations and redacted
screenshots/exports under order-readiness. Bind quote IDs/timestamps, exact file
hashes and settings; omit credentials, address and payment data. Update the
existing STATUS journal, preserving OR6–OR10 history. Use one bounded session:
at most 45 minutes of active browser work after local draft validation; stop
earlier on an authority/payment boundary. One ordinary retry per failed screen,
then report the evidence gap rather than loop. No new full stock search.

Return the orchestrator's top two paths: (1) preferred JLC-managed quote, with
all exceptions and commitments exposed; (2) exact external/consignment fallback
only for failed lines, with unquoted costs identified. If only a partial quote
is possible, say why and name the single next decision. Neither path authorizes
spending. A priced quote and engineering/order acceptance remain separate.

Validation from repository root:

```sh
python3 -B projects/crow-array/publication.py verify
python3 -B -m unittest discover -s projects/crow-array -p test_publication.py
python3 -B -m unittest discover -s projects/crow-array/order-readiness -p 'test_*.py'
git diff --check
```

OR12 baseline: 256 preserved payloads and 44 tests; DO-NOT-ORDER remains expected.
On macOS, if `/var` symlink resolution breaks tests, use `TMPDIR=/private/tmp`
for those test commands. Do not alter released files to pass.

## Suggested MacBook prompt

> Read projects/crow-array/order-readiness/MACBOOK-QUOTE-HANDOFF.md on branch
> codex/crow-jlc-source-review-20261030 and follow local vNext. Verify the
> prepared quote-draft/r1-20261031 files for five carriers and ten pods, preserving the
> JLC/user installation split. Show me the exact upload manifest and ask for
> scoped non-binding quote-session permission before any upload or submission.
> Then collect one itemized JLC quote with quantities, fees, process exceptions
> and schedule; report partial results honestly if payment or inventory purchase
> is required. No purchases, payments, reservations, substitutions or commitment
> to manufacture. Do not repeat the completed stock/pricing research passes.
