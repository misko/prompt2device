---
schema: 1
kind: pcb-human-report
report_id: 2026-09-20-transcript-cost-retrospective
title: Crow transcript time, token and bottleneck retrospective
subtitle: Three Terra-medium audits of the available September 10–20 conversation
project: crow-roof-array-v1
date: 2026-09-20
status: DRAFT
evidence_status: INCOMPLETE
---

## Executive conclusion

**INFERRED:** The largest avoidable cost was repeated work across the boundaries
between source geometry, native CAD, router constraints, review evidence and
publication. Routing was a major technical bottleneck, but many reruns were
caused by late requirements, incomplete preflights, stale review subjects or
packaging changes rather than the routing search itself.

**PROPOSED:** Freeze high-impact assembly/interface decisions earlier; prove
complete local pin-field feasibility before routing; compile deterministic
rejections into router constraints; stage publication metadata before the final
replay; and run reviewers against compact, answerable, stable packets. Preserve
independent checks and the zero-via/fabrication floors.

## Question and scope

The user requested next_steps.md and affordable Terra-agent review of the full
conversation, including where time/tokens went and what repeatedly blocked
progress. Three gpt-5.6-terra agents at medium effort independently covered:
September 10–13 causal history; September 14–20 causal history; and the parent
session's per-response usage records. Root reconciled their findings, checked
additional zero-via/publication events, and separated observed counts from
interpretation. No paid OpenRouter calls were made for this retrospective.

## Evidence boundary

**CITED:** Session `01a08bc2-6c45-7760-91fc-4a15c0a34eba`, titled
“Finish board and mint release”. Local raw rollout is under
`~/.codex/sessions/2026/09/10/` with that session ID. The sanitized conversation
extract contains 2,675 user/assistant records (196 user, 2,479 assistant),
covering nine UTC dates, totaling 1,374,153 bytes. Agents read all those supplied
messages. Original tool-output/reasoning bodies were not part of that semantic
extract; the quantitative audit independently stream-parsed the raw session.
The original session can contain events not emitted as user/assistant messages.

**CITED:** Endpoint daily message files and hashes were retained locally in
`/tmp/crow-retrospective/transcript_manifest.json`; agent analyses and the usage
extraction script are in that same local directory. No raw transcript or
credentials are committed into the project. Project journals and review
receipts supplement the transcript; older context before September 10 is not
claimed to have been recovered in full.

**INFERRED:** Counts of tokens, commits, tool calls or calendar hours alone do
not measure useful engineering or waste. Costs cannot be assigned precisely to
individual root causes when several causes share a day or context. Root-session
usage is not a complete inventory of separately stored child-agent usage.

## Findings

### Recorded usage

**MEASURED (session accounting, not hardware):** Frozen immediately before
2026-09-20T17:07:48.344Z, the user request initiating this retrospective.
18,157 distinct response records sum to **2,513,916,418 total tokens**:
2,505,348,742 input, including 2,442,516,480 cached input (**97.49%**);
**62,832,262 non-cached input**; and **8,567,676 output**. Reasoning tokens
(2,423,249) are a subset of output and must not be added again. Cumulative
`token_count` status events were excluded. All 131 completed-turn counters
checked against their response sums matched, with zero discrepancies.

These are repeated model-processing quantities, not unique conversation words,
active labor hours, or a Codex bill. Separate child-session logs are outside
this total. The approximately 242.5-hour calendar envelope is not active time.
196 context compactions occurred. Model context attributes 1,259,947,297 total
tokens to Sol and 1,253,969,121 to Astra; model totals do not establish comparative
model efficiency because the assignments and engineering difficulty differed.

The following daily values use the same pre-audit cutoff. M = million tokens.
Work descriptions are transcript synthesis, not exclusive token attribution.

| UTC date | Responses | Non-cached input (M) | Output (M) | Total incl. cached (M) | Dominant observed work |
|---|---:|---:|---:|---:|---|
| 2026-09-10 | 1,099 | 4.71 | 0.74 | 151.97 | Native schematic and review setup |
| 2026-09-11 | 1,806 | 6.83 | 1.13 | 248.55 | Review closure and connector evidence |
| 2026-09-12 | 2,126 | 9.63 | 1.31 | 293.43 | RJ45 migration, footprints, geometry |
| 2026-09-13 | 2,024 | 7.42 | 1.16 | 277.68 | Placement, top-side assembly, ADC corridors |
| 2026-09-14 | 3,044 | 9.79 | 1.34 | 424.02 | Routing topology, exits and replay |
| 2026-09-15 | 4,027 | 12.19 | 1.47 | 553.79 | Zero-via restoration, ADC/MCH corridors, analog routing |
| 2026-09-16 | 3,500 | 10.41 | 1.23 | 486.72 | Final gates, publication, sourcing and assembly |
| 2026-09-17 | 410 | 1.27 | 0.11 | 62.00 | Release freshness, manifests and publication |
| 2026-09-20 | 121 | 0.58 | 0.07 | 15.75 | Order preparation and external adversarial review |

**INFERRED:** September 14–16 dominates recorded volume (58.3% of total tokens).
This supports prioritizing geometry/route/replay/publication process fixes, but
does not justify assigning that entire volume to routing or to wasted work.

Exact daily values are preserved in the [usage CSV](assets/2026-09-20-transcript-usage.csv),
extracted from the session and frozen at the cutoff above.


### Comprehensive causal table

Each row is **CITED** for the event/outcome and **INFERRED** for avoidability and
relative effort. Date ranges are UTC observation windows, not active hours.
The daily usage table is the quantitative attribution boundary: no fabricated
per-issue token percentages are assigned.

| ID | Observed period / anchor | Issue and why we got stuck | Progress / resolution | Avoidable repetition and next-time change |
|---|---|---|---|---|
| R01 | Sep 10 14:49–17:44 | Native schematic label crossings, short shafts, clipped pages and ambiguous identities emerged one review at a time | Schematic review reached SOUND | Complete native-export readability/connectivity census before packet dispatch; batch related exporter repairs |
| R02 | Sep 10–13; expired handbacks Sep 11 and 12 | Reviews completed technically but failed closure/deadline/path contracts; zero retry allowance required user intervention | Replacement reviews and startup qualification improved delivery, but the loop recurred | Automate reviewer delivery/closure, preflight paths, reserve closure time and distinguish execution retry from a new engineering candidate |
| R03 | Sep 11–13 | Connector pictures passed direction checks but hid targets; rerenders and layout changes repeatedly invalidated approval | Elevated/exact views and user approvals closed successive valid subjects | Use one immutable visible-target bundle; bind geometry/model/camera identities; do not regenerate during approval |
| R04 | Sep 12–13 | Cable migration proceeded through Cat cable with Molex, then factory RJ45; multiple footprints, pin maps, shielding and contracts changed | Exact RJ45/cord source adopted | Legitimate user change; reduce later cost by freezing complete connector/cable/assembly dossier before placement |
| R05 | Sep 12–13 | Retired Micro-Fit pin coordinates, conflicting physical footprints and missing model transforms survived interface migration | Footprints/model registration and route anchors corrected | One migration census for pins, drills, model side, shell, seed endpoints, and retired terms before rebuilding |
| R06 | Sep 12–13 | ADC corridor, local returns, drill/annulus contacts and thermal semantics were checked with incomplete geometry predicates | Channel permutation and integrated source corrections advanced placement | Diagnose all affected native objects before consuming a geometry trial; verify the actual CAD stage and geometry semantics |
| R07 | Sep 13 17:01 onward | Top-only SMD requirement arrived after mixed-side placement; carrier repacking and pod protection changes reopened reviews | All fitted SMD moved to top; subsequent thermal work remained necessary | Explicit per-reference assembly-side policy before placement; user scope change is legitimate, late invalidation is predictable |
| R08 | Sep 14 | Pod/analog copper overlapped physically but graph endpoints did not describe the same connections | Same-net chain canonicalization and exact topology checks repaired representations | Define physical-contact graph semantics once; independent native checks and known-bad topology fixtures |
| R09 | Sep 14–15 | Power and analog waves trapped later source pads; local exits and stricter neighboring clearances were omitted from early proof | Source launch corrections, wave reordering and local crossings resolved classified cuts | Reserve real exits/corridors before wide power routes; enforce the strictest applicable clearance during search |
| R10 | Sep 15 01:31–02:00 onward | AUDIO_CT/AUDIO_EN single-net fixes consumed each other's only escape | Coupled front-copper CT and off-pad EN correction supported replay | Review the package neighborhood as a group, then replay from earliest changed source wave |
| R11 | Sep 15; hard stop 11:58:44 | Digital no_vias contracts/regression had to be restored; earlier apparent progress was inadmissible under the required constraints | Strict F.Cu clock/TDM reroute; later reviews confirmed 13 governed nets with zero vias | Treat safety/architecture constraints as locked inputs; reject a candidate that changes them before any expensive replay |
| R12 | Sep 15 after hard stop | Four ADC F.Cu exits, then long MCH pulldown branch walls created mutually blocking routes | Passive relocation, short pulldowns and joint six-clock/TDM corridors solved the geometry | Stop retrying once physical cut is proved; co-design the whole constrained bundle before routing |
| R13 | Sep 15–16 | AUDIO_P1 topology, analog capacitor order, branch matching and DCR checks exposed differences between intended and realized copper | Final analog audit reached 155/155 electrical paths | Grade topology, branch order, matching and resistance together before full stitch; report exact endpoints |
| R14 | Sep 15–17 | Import inherited wrong setup/rules; stitch recipe phase order and late ground/thermal contacts required replays | Rules/source fixes and ground links led to native DRC 0 violations/0 opens/0 parity | Assert source-to-import settings and rules; preflight stitch dependencies; preserve final independent native DRC |
| R15 | Sep 16 | Via aspect ratio, capacitor-land intrusion and protected-via movement appeared late in broad tests | Source repaired; 380 source tests and renewed acceptance reported | Run absolute whole-board manufacturing census before reviews, not only delta checks |
| R16 | Sep 14–16 | D1 hot leakage/polarity proof, J9 identity, U2 model side and missing primary evidence delayed acceptance | Exact part evidence and renewed pin/model reviews closed subjects | Packet answerability matrix plus substitution impact analysis before dispatch |
| R17 | Sep 16 04:06 onward | Two Astra reviewer calls failed with provider 401; partial handbacks could not be accepted | Retries succeeded and reviews completed | Authentication smoke test, distinguish execution failures from verdicts, bounded retry preserving packet |
| R18 | Sep 16 16:12–16:53; final verification 17:10 | GitHub rejected >2 GiB push; recursive frozen review archives dominated outgoing history | LFS migration and bounded batches enabled remote publication | Content-addressed shared evidence plus manifests/deltas; prohibit nested archive recursion; preflight blob and pack limits before seal |
| R19 | Sep 16 18:03 onward | Stock surplus was not consistently source-owned; public inventory was confused with authenticated JLC allocation | Configured 150-unit surplus and exact public-source evidence supported successors | Separate public part selection, live assembly fulfillment and payment; propagate one quantity/surplus policy through all paths |
| R20 | Sep 16–17 | User required all SMDs machine placed; ADC and other excluded SMDs needed BOM/CPL, sourcing and rotation changes | Carrier v0.1.8 specifies 306 top SMDs plus 27 manual THT; pod v0.2.7 specifies 31 top SMDs | Freeze assembly owner for every reference before layout; generate BOM/CPL/order instructions from one matrix |
| R21 | Sep 17 00:43–01:28 | Sourcing metadata and review-header digests changed late, invalidating checkpoints/replays; rehearsal caught provenance/package defects | Final release gates and remote state verified | Stage all metadata and run a release rehearsal before final expensive replay; renew only evidence whose dependency actually changed |
| R22 | Sep 17 01:24–01:28 | Explicit artifact paths, subject headers, ignored manifest member and generated whitespace needed serial publication fixes | Tracking/manifest corrections passed | Validate a clean recipient-view tree and exact Git/manifest membership before seal |
| R23 | Sep 20 | OpenRouter output ceilings produced truncated reasoning/reports; one rate-limited request and fragile content extraction added retries | Completed bounded reports plus rebuttals obtained | Persist raw response first, validate finish reason/report schema, reserve answer budget, bound retries; stop accepting reasoning as a finished report |
| R24 | Sep 20 | Model claims confused CLR behavior, CFG modes, source versus load resistance, path versus pin distances, and steady versus transient budgets | Primary-source checking refuted or narrowed claims; no new fabrication blocker confirmed | Include primary mode tables and metric glossary; adjudicate claims using independent evidence, not reviewer consensus or optimistic header normalization |
| R25 | Sep 20/current | Current-limit contradiction, 13.2 V card coverage, unsigned audio thresholds and stale operator wording remain | Collected in next_steps.md; physical qualification still owed | One reviewed procedure correction before first power; keep order, first-power, first-article and deployment states explicit |

### Publication and external-review quantities

**CITED:** At Sep 16 16:17:43, the transcript reported about 7.97 GB of raw
outgoing blobs, including 377 carrier journal archives totaling 6.64 GB, with
15 archives of 118–493 MB. These are historical reported measurements, not a
fresh repository-size measurement. Publication failed at 16:12:14 and remote
state was verified at 16:53:06: approximately 41 minutes of elapsed recovery;
final release verification was reported at 17:10:40. The cost of accumulating
those archives spans earlier work and is not limited to that recovery window.

**MEASURED (API receipts, not hardware):** Nine retained OpenRouter response
receipts sum to $3.7880943646. Three length-truncated attempts account for
$2.40865025 (63.6%); partial material was reused, so this is spending on
incomplete attempts, not proof that every dollar was wasted. One error receipt
reports zero cost. The reported account usage $3.999660991 includes other or
unretained transactions and cannot be attributed entirely to these reviews.
DeepSeek's final packet receipt records 239 files, 2,949,795 bytes and 1,000,790
prompt tokens; earlier smaller packet counts do not describe that final run.

**MEASURED (text count):** 88 of the 196 extracted user messages match a broad
status/blocker/progress/ETA/continue keyword screen. This includes steering and
quoted instructions; it is not a count of complaints or wasted turns. It does
show the importance of clear persistent progress and blocker state.

## Recommendations

| Priority | Process change | Why it saves effort | Concrete completion test |
|---|---|---|---|
| 1 | Freeze interface, assembly owner/side and strict route contracts before placement | Avoids high-fanout redesign and inadmissible apparent progress | Per-ref responsibility matrix; connector/cable dossier; contract-diff rejection fixture |
| 2 | Complete geometry feasibility before repeated route attempts | Targets the largest technical loop | All local exits, branch topology, strict clearances, pad contacts, returns and manufacturing limits tested as one neighborhood; impossible-cut report stops retries |
| 3 | Move release/evidence preflight ahead of full replay | Avoids source-stable but metadata-stale replay loops | Clean candidate-tree rehearsal proves review identities, manifest membership, transport size and sourcing digests before final seal run |
| 4 | Make review jobs bounded, answerable and resumable | Saves tokens and preserves usable independent work | Validated source packet, primary evidence, output schema/finish reason, closure reserve, bounded execution retry; raw receipt always retained |
| 5 | Reduce repeated context and archive duplication | Addresses cached input volume, compactions and Git growth | Small current-state handoff with exact causal blocker, authoritative paths and next test; shared hash-addressed evidence, no recursive archive embedding |
| 6 | Keep first-article debt explicit and current | Prevents qualification work masquerading as release defects or being forgotten | next_steps.md rows close only with named evidence; active cards/docs agree; future revision owns cosmetic improvements |

**PROPOSED:** Use affordable bounded agents for extraction, counting and
consistency checks; reserve deeper review for a concrete unresolved engineering
question. No model should rewrite a circuit merely because another model
labels an unsupported suspicion P0. Likewise, a rebuttal is not a hardware test.

## Validation plan

Reproduce usage from distinct per-response records through the stated cutoff;
never add cumulative event counters or reasoning subsets again. Compare daily
sums to total sums and record any missing child-session coverage. Check all
causal entries against their UTC transcript anchors and journals. Use the report
audit for structure and link validity. Do not convert the calendar envelope,
clipped inter-event gaps or model latency into active labor hours.

## Source register

- [Current work plan](../../../../next_steps.md).
- [Original dated plan](2026-09-20-order-and-first-article-plan.md).
- [Carrier source journal](../../../crow-audio-carrier-v1/01_docs/journal/schematic.md).
- [Carrier routing journal](../../../crow-audio-carrier-v1/01_docs/journal/routing.md).
- [Pod routing journal](../../../crow-mic-pod-v3/01_docs/journal/routing.md).
- [External review dispositions](../../08_reviews/DISPOSITIONS.md).
- [Process improvement ledger](../../../../improvements.md).

Local audit source: raw session ID above; sanitized daily transcript slices,
three Terra reports, per-day CSV, usage summary and extraction script in
`/tmp/crow-retrospective/`. Raw local evidence may contain private context and is
not copied into the public repository. Retained OpenRouter receipts live in the
project's ignored `06_build/openrouter-*-review-20260920/` directories; complete
external report bodies remain in tracked `08_reviews/`.
