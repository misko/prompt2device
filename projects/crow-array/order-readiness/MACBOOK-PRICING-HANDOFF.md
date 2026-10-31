# MacBook handoff — seven exact JLC procurement offers

**Completed; next action updated 2026-10-31:** use
[MACBOOK-QUOTE-HANDOFF.md](MACBOOK-QUOTE-HANDOFF.md). OR9's pricing results are
published and OR10 consolidates procurement. Do not repeat the pass below.

Current task: check JLC replenishment and Global Sourcing **prices and arrival
times**, using the signed-in MacBook browser. User explicitly requests no
purchases. The previous 35-identity availability pass is complete; do not repeat
it. This handoff supersedes the next-action section of `MACBOOK-HANDOFF.md`.

## Get the published inputs

Repository: `misko/prompt2device`. Branch:
`codex/crow-jlc-source-review-20261030`. Do not assume these additions are on main.
Check local Git status first and preserve all Mac work. The prior browser report
described an incomplete/dirty checkout; do not reset it or commit its deletions.
If necessary use a fresh sibling clone (choose an unused directory):

```sh
git clone --branch codex/crow-jlc-source-review-20261030 --single-branch https://github.com/misko/prompt2device.git prompt2device-jlc-pricing
cd prompt2device-jlc-pricing
git status --short --branch
```

Read in order:

1. Local `vnext/skills/workflow-orchestrator/SKILL.md`, its resume instructions,
   and `vnext/skills/pcb-design/SKILL.md` / part-recheck procedure as applicable.
2. `projects/crow-array/order-readiness/STATUS.md`: current state and journal.
3. `SOURCING-COMPARISON-20261030.md` and `sourcing-comparison-20261030.csv`
   beside this file: priced routes, exact links and freshness limitations.
4. `SOURCING-DRAFT-20261030.md` and `JLC-BROWSER-20261030.json` only for relevant
   identity/process history. Do not rewrite the original observations.

## Exact job and query quantities

Five carriers and ten pods, not five complete arrays. These are installed need
and **illustrative query quantities**, not approved buy quantities. Capture
factory-required attrition/minimum assembly quantities separately for each job;
do not invent them or assume shared attrition across carrier and pod orders.

| Manufacturer / exact MPN | C-code | Carrier batch | Pod batch | Regular replenishment starting query |
|---|---|---:|---:|---:|
| CTS / CB3LV-3I-12M288000 | C17275161 | 5 | 0 | 5 |
| Littelfuse / 1206L010/30WR | C2153988 | 40 | 10 | 50 |
| Murata / GRM21BR71A105KA01L | C97917 | 10 | 10 | 407 |
| RECOM / R-78E5.0-0.5 | C5199916 | 5 | 0 | 5 |
| TDK / C2012X7R1V225K125AE | C2167593 | 0 | 10 | 62 |
| TDK / C3216X7R1V106K160AC | C2182140 | 10 | 0 | 14 |
| TI / PCM1864DBT | C2863172 | 10 | 0 | Global Sourcing: start at 10 |

Keep the complete maker and suffix. **PCM1864DBTR is not authorized as a
replacement.** Current public minima and prices can change; record the actual
account values. No credit for two unallocated public-stock fuses is assumed.

## One bounded browser pass

1. Verify browser control; ask the user to handle login/MFA. Never copy credentials,
   cookies, addresses, payment details or account tokens into the repository.
2. In Parts Manager → Order Parts, inspect the six exact regular replenishment
   offers. Inspect Global Sourcing for exact PCM1864DBT. Compare a global offer
   for any other line if its regular offer lacks a practical price/date or is
   unavailable. No broad alternative-part search or design change.
3. Record per offer: timestamp/timezone; maker/MPN/package; C-code or global
   supplier identity; stock pool and available quantity; minimum/order multiple;
   requested quantity; unit/extended price and currency; all displayed fees/tax;
   required packing/attrition; dispatch versus warehouse-arrival date; business
   versus calendar days; assembly eligibility; URL and redacted evidence.
   Missing information stays unknown. Public stock is not allocated stock.
4. Stop at read-only detail screens. Do not add to carts, create orders, submit
   requests, accept purchasing terms, pay, reserve inventory, upload BOMs, or
   contact vendors. If obtaining a quote requires any of those actions, record
   the exact boundary and return it to the user. Do not pay to reveal a price.
5. Finish after one pass or 30 minutes of active browser work, whichever comes
   first. On a lookup failure, try at most one ordinary page reopen, then report
   it as an access failure, not out of stock. Do not loop around login, payment
   or absent quotation information. Preserve OR6–OR8 history and attempt counts.

Published Global Sourcing times and public catalog prices are benchmarks, not
job quotes. The desired date is **usable stock at JLC**, not merely supplier
dispatch. Board manufacture/assembly/shipping remain separate. Do not mix
incompatible JLC/global/consignment inventory pools for the same part.

JLC still owns the requested 60 connector/regulator installations; the user owns
20 acoustic parts and five Picos. No ownership change, substitutions or renewed
Pico-relief investigation. JLC's Wave Soldering label means manual assembly per
its FAQ; it alone is not evidence of literal wave exposure. Preserve compatible
CTS SMD installation as a matching/process question, not a redesign task.

## Return one decision, not seven research loops

Save a new dated `JLC-PRICING-YYYYMMDD.md` and CSV/JSON beside this file; use a
unique suffix rather than overwrite an earlier pass. Include both successful
and failed offers, timestamped sources, quantities and limitations. Update the
existing STATUS journal with measured progress, blockers and the stop boundary.
Do not modify the sealed release or historical stock evidence.

Return a seven-row table and two ranked complete-route recommendations:

1. **Preferred:** JLC replenishment for six + exact ADC Global Sourcing, adjusting
   the sourcing route where an actual offer is better. Identify any missing line,
   itemize charges and report the slowest confirmed arrival. Do not total mixed
   currencies or turn missing fees into zero.
2. **Fallback:** exact external purchase/consignment only for unresolved lines,
   using retained distributor leads. Explain any still-unquoted shipping and
   consignment costs; no external ordering or shipment preparation in this pass.

This pass produces a reviewable proposal, **not ordering approval**. If prices
cannot be revealed without a submission/payment, return partial results and
that specific missing authority. Do not claim a complete quote or closed hold.
Publishing the returned results is separate from placing any vendor order.

## Validation

From a clean, complete checkout, Python 3.11+:

```sh
python3 -B projects/crow-array/publication.py verify
python3 -B -m unittest discover -s projects/crow-array -p test_publication.py
python3 -B -m unittest discover -s projects/crow-array/order-readiness -p 'test_*.py'
git diff --check
```

Current baseline: 256 preserved payloads, 15 publication tests and 18
order-readiness tests. `DO-NOT-ORDER` is expected. On macOS only, if tests fail
because `/var` resolves to `/private/var`, retry the test commands with
`TMPDIR=/private/tmp`; do not alter preserved engineering files to pass tests.

## Paste into the MacBook task

> Read projects/crow-array/order-readiness/MACBOOK-PRICING-HANDOFF.md on branch
> codex/crow-jlc-source-review-20261030 and follow local vNext. Use my browser
> for one read-only pass checking the seven exact shortage lines: JLC
> replenishment and Global Sourcing prices, quantities, fees and usable-stock
> arrival dates for five carriers and ten pods. Reuse the completed availability
> pass; do not repeat all 35 identities. Save dated evidence and update STATUS,
> then present the two ranked complete procurement routes. Stop if a quote
> requires an order, payment or submission. No cart changes, purchases,
> substitutions, uploads, supplier contacts, reservations or order submissions.
