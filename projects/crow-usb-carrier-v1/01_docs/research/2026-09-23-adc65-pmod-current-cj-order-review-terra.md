# Independent P-MOD conductor-order source review

review_verdict: SOUND

patch_adoption: ELIGIBLE

producer_retry: NOT_AUTHORIZED

## Scope, integrity, and authority

This is a fresh, READ_ONLY review of patch SHA-256
`41b058bc6e97a5b3d77756cc0681e600468c59933909dd94dc14a5074c114905`
against base commit `5a198c2619dbb9b121e8c2538442e4a7b8902a88`. The schema-2
envelope SHA-256 is
`e1600e500b339f4710859ae9f8e24f8782e9fb71d672ea7511ff2872c3083dbd`;
the detached manifest SHA-256 is
`3c3d1583384f3844c74670bf114de93a899144df2649b087aff8becc7ac8a69f`.
All **11/11** envelope inputs match both their stated SHA-256 and byte size
(**0 mismatches**):

| Input | SHA-256 | Bytes |
| --- | --- | ---: |
| `README.md` | `8ee954fefbca51c0bd76586abed4b3e41d2e43b703ba6f621e1e1314182c1630` | 2005 |
| `attempt.json` | `acd2c1d6616f11cc5c3c96d87f36338ef311fc2879e3da065075da9314c8faed` | 3436 |
| `attempt.json.log` | `6fe247cb52d1d384ef818a3bdafc4d8ff16b2bc3f82554d8d771ee8bf233b23d` | 931 |
| `current_stale_pmod.log` | `a039376fa36307d0b996e876150342ecc5a9d7c7145009c75d5fe1f35283e1f6` | 264 |
| `pmod_current_cj_order.patch` | `41b058bc6e97a5b3d77756cc0681e600468c59933909dd94dc14a5074c114905` | 1767 |
| `prior-adc65-source-review.md` | `9e5e055be68c28605a30929fed3db1c9c0479edbc1b7209a2f1018be3393d93a` | 5849 |
| `qualification.json` | `bf79c3fd84cadee72f015400ae722b1f9c86593e56569aff69c9c1640ec00395` | 47269 |
| `rebuild_all.proposed.sh` | `e85e4d5d3f8926e05e64966888f29cad0cbac1b3808860b55948ae5563d246e2` | 37229 |
| `test_pmod_order.log` | `3b636cf869300f137bc69b32e6c6c8d84e1954aab0e44f35055f924480d72b5a` | 360 |
| `test_pmod_order.py` | `194b7a393fdaab6ee464a3cf08054a85062db3f7e0f159db0fb2a3e06059eff3` | 1763 |
| `formal-review-prompt.md` | `44883a5b96603cff99281a3707e292a091612e240625b7c0e63487a30187f67c` | 2303 |

The prior ADC65 review remains authority only for its separate six-file,
568-to-569-component ADC bypass source subject. It does not judge this
one-file conductor patch and does not authorize a producer attempt, retry,
resume, schematic admission, routing, release, or push.

## Original failure and exact patch scope

The preserved original producer receipt is a failed first attempt: return code
1, `P-MOD FAIL`, **4/7** complex subsystems graded, with
`C_ADC_3V3X_OK_VDD` absent from the historical 568-component `circuit.json`.
Its failure occurred at pre-generation `[0a]`, before the TSX producer could
copy the current 569-component JSON. Its handback is also incomplete
(`missing=['result.json']`); this is a no-handback failed attempt, not a
retryable partial success.

The reviewed patch has **1/1** file target and **2/2** hunks, solely
`projects/crow-usb-carrier-v1/03_src/rebuild_all.sh`. Base content at the
specified commit agrees with the patch's removed `[0a]` block. The exact
mandatory invocation remains `$PY "$S/module_first_check.py" .` with the same
fail-on-nonzero `|| { ...; exit 1; }` behavior. Only the phase label changes
from `[0a]` to `[1m]` to identify its new location. There is no added skip,
waiver, fallback, conditional bypass, or checker-argument change. The
proposed shell parses with `bash -n`.

All **9/9** required pre-producer gate classes remain before `tsci build`:
RF (contract/context/solver/source), TSX preflight, source schemas,
electrical prebuild, rules, policy/precedent, schema-reader, ADR-bound, and
M-FRESH stamp. P-MOD remains inside the same non-resume full-build path as
before, so the relocation does not weaken resume behavior.

## Ordering and fixture assessment

The proposed full-build order is: fresh Circuit JSON copy, `TSX-DIAG` PASS,
P-MOD, fault-envelope comparison, render, M-FRESH verification, KiCad
conversion/netlist, semantic and ERC gates, checkpoint, then independent
schematic admission. Thus P-MOD consumes the diagnostics-clean artifact from
this producer run and fails before fault-envelope comparison, rendering,
conversion, or review. The required ordering relations are covered **7/7**:
copy, diagnostics, P-MOD, fault envelope, render, conversion, and admission.

The supplied fixture covers **3/3** non-vacuous branches. It asserts the old
ordering falsely returns `P-MOD FAIL stale` when a generator would create the
new ref; it asserts the new ordering returns `P-MOD PASS current` when the
fresh JSON includes it; and it asserts the new ordering returns
`P-MOD FAIL actual-missing` when that fresh JSON omits it. Its recorded result
is PASS and its structural positions establish
`generate < diagnostics < P-MOD < render < checkpoint` for the proposal.

That is structural/simulated regression evidence, not an execution of the
foreign TSX producer or the real `module_first_check.py` against a newly
generated artifact. A real producer rerun is intentionally outside this
review and remains missing evidence for a later, separately admitted campaign.

## Findings and boundary

- **P0: none.**
- **P1: none in the reviewed project patch.**
- **P2: shared-template follow-up.** The shared template retains the former
  stale P-MOD ordering. Project-only scope is acceptable for this bounded
  repair because the failure and conductor under review are this project, but
  the template defect needs a separate consumer inventory, patch, and review;
  this patch must not expand into that work.

Missing evidence is a fresh producer receipt using the adopted combined source
and conductor change, a new diagnostics-clean Circuit JSON/component census,
fault-envelope result, rendered schematic, conversion/netlist/ERC results,
checkpoint, and independent schematic review. The historical 568-component
checkpoint and the failed first attempt remain immutable evidence only.

The next boundary is source adoption followed by a newly qualified, bounded
first schematic campaign. This review authorizes no source application,
producer retry or resume, native admission, routing, release, or push.
