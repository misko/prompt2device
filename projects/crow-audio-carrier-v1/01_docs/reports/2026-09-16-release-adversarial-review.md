---
schema: 1
kind: pcb-human-report
report_id: 2026-09-16-release-adversarial-review
title: Crow carrier and pod release adversarial review
subtitle: Deficiency triage, public stock census, and independent release evidence challenge
project: crow-audio-carrier-v1
date: 2026-09-16
status: REVIEWED
evidence_status: INCOMPLETE
---

## Executive conclusion

**INFERRED:** Carrier v0.1.2-2026-09-16 and pod v0.2.1-2026-09-16 remain
engineering releases with explicit DO-NOT-ORDER / FIRST-ARTICLE-ONLY holds.
This bounded adversarial review found no new demonstrated copper/topology
defect, but it did find procurement omissions, incomplete archive-local
review/bring-up context, stale deficiency wording, and a reproducible difference
between native and portable locator checking. It is not a new full electrical
design acceptance or permission to order.

**MEASURED (software/API):** All 73 machine-BOM rows resolve to their exact
MPNs. Carrier public stock covers 49/51 rows for five boards; pod covers 22/22
for ten. The two carrier shortages remain LT3041 and TMUX2821. Manual parts
are outside those totals: the film capacitors and Samtec header introduce
additional catalog shortages. Distributor routes exist for several shortages;
exact LT3041 procurement remains the first sourcing priority.

## Question and scope

Review the latest Crow releases, their deficiency records, public part numbers
and stock quantities, and challenge the evidence behind previous passing claims.
Reviewed repository head: `1b72b4ec42eb0affa03c523747d241e922c3e3fc`.
No sealed bytes, board sources, assembly dispositions, or gate implementation
were changed. No purchase, allocation, or substitute was authorized by this review.

Public quantities below use the existing contracts: five carriers and ten pods,
without attrition/spares. This is a partial system lot: five fully populated
eight-channel systems would require forty pods. Shared machine codes were also
aggregated across both lots: 68 unique codes, with the same two shortages.

## Evidence boundary

| Subject | Immutable identity |
|---|---|
| Carrier | [v0.1.2 manifest](../../07_releases/v0.1.2-2026-09-16/MANIFEST.txt); seal `182e1e72293816028b590cbdc5dfb0da629d1622`; board SHA-256 `0776f364424282a7924266450f899ce69bf28cf95a602ca74d92b86fd91c164d` |
| Pod | [v0.2.1 manifest](../../../crow-mic-pod-v3/07_releases/v0.2.1-2026-09-16/MANIFEST.txt); seal `2c54a56647b470587809becb4ed5491dc8cfcfc4`; board SHA-256 `2685281fdb8dac636e16334c2d4eca679300bfa5322a368ac2685b59f48e3dd1` |

**MEASURED (software):** Explicit-project P-PUBLISH replay passes 2/2 boards.
Full native carrier A-LOCATOR replay passes 333 references, 1051 pads, 23
exception pages and 26 manifest members. Independent read-only Sol Medium
review `/root/adversarial_release_audit` inspected native board populations,
digital copper, spoke implementations and the sealed review/contract text.
Carrier has 309 SMD-marked footprints including fiducials, zero flipped; its
assembly receipt counts 306 fitted SMD. Pod has 31 SMD, zero flipped. All 13
governed carrier digital nets have zero vias and only F.Cu segments. Spoke
implementation checks pass carrier 8/8 and pod 1/1.
The pod's exact sealed critical-path checker also passes 22/22: 13 short
F.Cu/no-via paths plus nine required path-dominance targets.

**OWED / scope limits:** No fresh full datasheet/topology analysis of all
components, independent Gerber/CAM replot, full DRC/routing replay, complete
visual inspection of every PDF/render, analog simulation, or physical testing
was performed in this review. Historical DRC/analog/via-capacity acceptance
remains inherited evidence. Catalog stock never establishes authenticated
JLC assembly allocation or acceptable ordering economics.

## Findings

### Public stock and identity census

**MEASURED (API):** The existing `jlc_stock_check.py` queried the public JLC
catalog endpoint serially with build quantities 5 and 10. Snapshots completed
on 2026-09-16 around 17:52–17:53 UTC. The complete 73-row census, release BOM
hashes, timestamps and public URLs are in [machine BOM stock](assets/2026-09-16-release-adversarial/machine-bom-stock.csv).
No returned MPN mismatch occurred. Counts are observations, not reservations.

| Part / role | Required units | Public observation | Assessment |
|---|---:|---|---|
| LT3041ADE#TRPBF, C7452883; carrier LDO | 5 | API 0; [LCSC](https://www.lcsc.com/product-detail/C7452883.html) out of stock | Existing order blocker; exact packaging identity remains locked |
| TMUX2821DSGR, C53283916; carrier analog isolation | 40 | API/LCSC 16; [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/TMUX2821DSGR/28738833) displays 2449 | Catalog short by 24; exact-part external sourcing candidate, assembly acceptance owed |
| R82DC4100DQ60J, C183545; manual carrier film capacitors | 80 | API/LCSC 0; [DigiKey](https://www.digikey.com/en/products/detail/kemet/R82DC4100DQ60J/1930840) displays 183184 | Additional shortage outside machine BOM; distributor candidate exists |
| TMM-106-01-L-D, C7362125; carrier header | 5 | API 3; [LCSC](https://www.lcsc.com/product-detail/C7362125.html) exact catalog listing | Additional shortage outside machine BOM; regional Mouser search returned 332, but direct reopen failed, so treat that alternate count as unconfirmed |
| 615008160221 RJ45, C6461980 | 50 (40 carrier + 10 pod) | API 0; [DigiKey](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/615008160221/11627337) displays 991 | Manual exact-part procurement candidate |
| EEEFK1A471P, C178530; four manual carrier electrolytics | 20 | API 668; [LCSC](https://www.lcsc.com/product-detail/C178530.html) displays 518 | Exact public catalog identity exists; both observations cover the lot, but differ and are not additive |
| 2920L260/33DR, C22870534; carrier fuse | 5 | API 28; [LCSC](https://www.lcsc.com/product-detail/C22870534.html) exact catalog listing | Public quantity sufficient; manual/consign process still owed |
| Molex 43650-0200 / 436500200, C192562 | 5 | API 4313 | Normalized-MPN candidate; verify manufacturer identity and process before adoption |
| Molex 43650-0400 / 436500400, C277684 | 5 | API 2340 | Normalized-MPN candidate; verify manufacturer identity and process before adoption |
| CS5308P-DN; manual carrier ADC | 5 | Public JLC search returned only CS5308P-DNR, stock 0; direct US DigiKey page exposed no numeric stock on reopen | Exact -DN current stock unresolved; do not substitute -DNR silently |
| AOM-5024L-HD-R; off-board pod microphone | 10 | [DigiKey](https://www.digikey.com/en/products/detail/pui-audio-inc/AOM-5024L-HD-R/7898328) displays 12322 | Public exact-part candidate, manual mounting/qualification still owed |

**CITED:** Distributor webpage figures were retrieved during this review;
pages/search indexes can be cached and differ by region or packaging. They
are leads for a current cart/quote, not guaranteed live allocation. For example,
older film-capacitor snippets showed stock while both the direct LCSC page and
fresh API returned zero. Do not choose the more convenient observation.
The [manual catalog search](assets/2026-09-16-release-adversarial/manual-catalog-candidates.csv)
retains all candidates, including wrong suffixes and unrelated search hits;
only the exact/explicitly normalized identities above are relevant.

### Prioritized adversarial and deficiency findings

| ID / priority | Evidence and impact | Disposition / closure |
|---|---|---|
| REV-01 / P1 process | **MEASURED:** Portable `check_sealed_archive` skips native frame/pad/body/CPL geometry and PNG/PDF projection checks, yet prints the same A-LOCATOR PASS as native validation. Synthetic wrong-frame data with consistent hashes and synthetic review metadata passes portable replay while native rejects `native board frame`. | Repair before relying on portable PASS as geometric acceptance: run native validation in CI, or explicitly distinguish integrity replay and require a verifiable native acceptance witness. This is not a demonstrated defect in the released locator, which passed native replay. |
| REV-02 / P1 order preparation | **MEASURED:** Machine BOM stock excludes 33 manually fitted carrier parts and the pod jack/capsule. Carrier's `not_in_catalog` disposition for EEEFK1A471P conflicts with its now-confirmed exact public listing. Film caps/header are additional catalog shortages. | Build a complete exact-MPN procurement sheet including manual parts, aggregate quantities and attrition. Retain manual disposition until a separate accepted assembly change; availability alone does not change sealed BOM/CPL. |
| REV-03 / P2 archive completeness | **MEASURED:** Carrier ORDER_README points to source-tree `01_docs/DEFICIENCIES.md` and `FIRST_ARTICLE_TEST_PLAN.md`; neither is inside the standalone archive. A release-only recipient lacks the detailed obligations. | Include both snapshots in a future documentation successor; retain current DO-NOT-ORDER. Use the pinned repository documents in the meantime. |
| REV-04 / P2 review traceability | **MEASURED:** All four pod successor reviews name `inherited_report: verification/<same filename>`, which resolves to the replacement report itself, while the stated hash belongs to v0.2.0. The reports also overstate unchanged verification bytes. | Preserve predecessor review bytes under explicit non-self-referential paths in a successor and accurately enumerate changed reports. Predecessors remain available in the repository; this is not evidence of changed copper. |
| REV-05 / P2 reproducibility limitation | **MEASURED:** Carrier archive includes final native design but not full route/rule authority; review rebind appendices cite reports without archive-local member paths, including a future-tense `will be archived` note. | Complete a navigable provenance index and preserve required review members. Do not infer globally missing evidence from text search: compressed journal archives were not exhaustively inventoried. Standalone opening/replot and full pipeline regeneration are distinct claims. |
| REV-06 / P3 stale documentation | **MEASURED:** Carrier README heading says v0.1.1; pod says v0.2.0. Pod sealed deficiency snapshot still calls itself mutable/not released and lists final gates as unfinished. Carrier live deficiency list names v0.1.0. | Reconcile current status and next successor paperwork; do not reroute for these labels or edit immutable archives. |
| POD-D001 / P3 inherited | **CITED:** Pod D1 rationale says 1N4007 although fitted/BOM identity is S1M-E3/61T. Existing review classifies it as prose-only. | Correct rationale at next source revision and verify unchanged electrical assertions. |

**OWED:** Both boards retain authenticated allocation/economics, final uploader
mapping and rotation, physical connector fit, first-power rail behavior,
analog noise/gain/clipping, cable stability, thermal, fault and environmental
qualification. Carrier additionally requires confirmation of the 12 selective
filled/capped via sites. These are not minor deficiencies to waive.

## Recommendations

1. **PROPOSED:** Resolve exact LT3041 sourcing first; prepare a single combined
   procurement sheet including all manual parts. Use external exact-part stock
   where feasible, with explicit assembly handling and a current quote. This
   is the shortest path to a real first article without speculative redesign.
2. **PROPOSED:** Correct the portable locator evidence boundary with a hostile
   geometry regression. Keep full native validation for design acceptance;
   a hash-only replay must say what it proves.
3. **PROPOSED:** Bundle the missing first-article/deficiency documents and
   inherited review originals in a small documentation successor when order
   preparation proceeds. Correct labels in that same pass, not repeated
   cosmetic releases. Preserve existing immutable archives.

## Validation plan

- Re-query every exact part at quote time; record build quantities, spares,
  manual/consigned quantities, packaging, MOQ, fees and authenticated allocation.
  Reject suffix substitution and distinguish unknown from zero stock.
- Replay the synthetic locator contrast: use native LocatorTests fixture;
  change `frame` to `[0,0,999,999]`, update embedded data/member hashes and
  generate its synthetic review fixture; native `release_check` must reject.
  Today setting the imported checker's `pcbnew = None` accepts it. A correction
  must either reject the same geometry or explicitly restrict its acceptance
  claim and validate the separate native witness. Production reviews were not
  modified in this experiment.
- Open a candidate successor with only its directory available. Every cited
  first-article document and inherited report must exist and match its stated
  hash; no inherited-report path may accidentally resolve to the successor's
  replacement report. Re-run required, freshness and publication checks.
- Before deployment, execute the physical first-article plan with retained
  measurements; a successful public stock query cannot close those tests.

## Source register

- [Carrier order instructions](../../07_releases/v0.1.2-2026-09-16/ORDER_README.md), [assembly policy](../../07_releases/v0.1.2-2026-09-16/verification/assembly.yaml), [live deficiencies](../DEFICIENCIES.md), [first-article plan](../FIRST_ARTICLE_TEST_PLAN.md).
- [Pod order instructions](../../../crow-mic-pod-v3/07_releases/v0.2.1-2026-09-16/ORDER_README.md), [sealed deficiencies](../../../crow-mic-pod-v3/07_releases/v0.2.1-2026-09-16/verification/deficiencies.md), [topology review](../../../crow-mic-pod-v3/07_releases/v0.2.1-2026-09-16/verification/redteam_topology.md).
- [Carrier release contract](../../07_releases/contracts.md); [carrier layout review](../../07_releases/v0.1.2-2026-09-16/verification/redteam_layout.md).
- [Locator checker](../../../../skills/jlcpcb-fab/scripts/assembly_locator_check.py), [native hostile fixture](../../../../skills/jlcpcb-fab/scripts/tests/test_assembly_locator.py), [portable fixture](../../../../tests/t1_locator_publication.py).
- Public catalog method: `https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`; query exact code, read `componentCode`, `componentModelEn`, `stockCount`; catalog API and page observations remain separate from JLC PCBA allocation.
- Public distributor and manufacturer links appear with each stock observation above. [Panasonic exact part](https://na.industrial.panasonic.com/products/capacitors/aluminum-electrolytic-capacitors/series/88994/model/89455) confirms EEEFK1A471P identity.
