subject: crow-audio-carrier-v1 1353d04766617721cf97ffbd80e7bf87c0055bdd
date: 2026-09-08
reviewer: fresh-context agent, topology equivalence-rebind lens
context-given: exact-current-and-baseline-artifacts; baseline acceptance metadata only
source_commit: 1353d04766617721cf97ffbd80e7bf87c0055bdd
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
netlist_sha256: ac2b772d357bf4c6e8e962a63fbc5cb5535e3770accaa3ce82a42b28520c227b
parts_sha256: da40483f53767ef34e8d0b561eea11d36e6bc6c10162dcae50a9078cf5373e0d
design_rules_sha256: 14603bc34e244ce702e97a3b14251090eeb88377107e26293fb6ace4d1d26fd9
schematic_pdf_sha256: 72fd0f97d190af75c5c26b06c39ce34b17433ba95afe7956f6700501f53bda3e
inherited_topology_witness: projects/crow-audio-carrier-v1/08_reviews/2026-09-08_77d25f0d_fresh_topology.md
inherited_topology_witness_sha256: e5adbcb9bf5060a7a73b1b9b81bd613ee28f4b8a1ff03b1522e124f07c9eea36

# Independent electrical-equivalence rebind

## Verdict and claim boundary

SOUND specifically as an electrical-equivalence rebind to the INHERITED full topology judgment for baseline commit `77d25f0dd1a44ca5139be80310e65417c17a2ec6`. This is not a newly derived full topology/ratings acceptance. The admitted scope remains the ADR0007/0009 conditional laboratory prototype, not physical qualification. No electrical difference was found after exhaustive comparison; no baseline qualification or finding is closed.

The exact current normalized netlist hash above remains authoritative. It is different from the accepted baseline hash; I have not changed the owning normalizer, substituted a new baseline hash, or created a waiver. The difference is completely explained by serialization order in two component-unit pin lists. The complete net/node records and other electrical fields are unchanged.

This witness grants no PCB generation, bridge promotion, placement, routing, release, purchase, energization, or production authority by itself. The independent PDF/readability lens is separate and was not duplicated here. Order verdict remains DO-NOT-ORDER.

## Identity, timing, and independence

Repository: `/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901`.

Administrative packet HEAD: `5efc042747f04f20d310d4f8c7b6df81570e839b`. An independent Git name-status comparison from the engineering subject to that HEAD found only the ten files of this handoff packet added under `06_build/handoffs/2026-09-08-render-review-1353d047/`; it did not alter the engineering subject.

Actual clocks observed:

- First tool clock: 2026-09-08 02:06:56 UTC.
- Initial strict packet/full-census measurement: 2026-09-08T02:08:54.204109+00:00, before the electrical comparison executions.
- Post-comparison strict packet/full-census measurement: 2026-09-08T02:16:57.100317+00:00.
- Final post-report strict packet/full-census measurement: 2026-09-08T02:20:20.075789+00:00; 7/7 packet items and 368/368 census files still exact, same HEAD and the same two administrative-only modified paths.
- Hard deadline supplied by the commission: 2026-09-08T02:21:32Z.

These are real clock readings, not reconstructed TaskAttempt telemetry. No TaskAttempt, token count, process-containment, hermeticity, or runtime-supervisor claim is made. Short diagnostic CLI calls were bounded with `timeout 60s`; no conductor was invoked. All created analysis, diagnostic, and report files are in the new directory `/tmp/carrier-topology-rebind-1353d047.L3rkTC`. This reviewer made no repository writes, opened no PCB for geometry work, delegated no work, and used no accounts, uploader, vendor contact, or ordering workflow.

The complete PCB-design and KiCad SKILL.md files were read, together with selected execution-graph, execution-runtime, review-and-publication, early-boundary, schematic-generation, tscircuit-folder, and design-policies references, the complete project `08_reviews/contracts.md`, and the commissioned task/envelope. The skills enforced the exact-artifact boundary and measured-versus-inherited distinction; they did not expand this commission into a ratings or layout review.

No prior review body or source-correction report was read. The baseline witness file was opened only by a byte-hash operation; its SHA-256 matches the declared witness identity. Baseline acceptance came only from `baseline-identity.json`. The six specifically named TOP77 disposition rows were read to preserve their limitations, not to adopt their calculations as fresh proof. Root/author assertions and source-authored tests were not used as equivalence evidence.

The first Git status observation was clean. At initial census and post-comparison census, Git status reported exactly two modified files outside the census: `01_docs/STATUS.md` and `01_docs/journal/schematic.md`. Independent numstat showed 3 additions/3 deletions and 18 additions/0 deletions respectively. Root identified these as launch/deadline bookkeeping; that attribution is coordinator-reported, not forensic proof. Their existence and exclusion from the frozen 368-file set are measured. I preserved them and did not claim a globally clean worktree. All frozen engineering/packet bytes independently remained identical.

## Strict packet and exhaustive input census

The unchanged owning `pipeline_execution.TaskEnvelope.from_json`, `envelope_sha256`, and `verify_input_packet` functions strictly parsed and reopened the envelope and every packet item. The packet content address was independently reconstructed from the sorted canonical packet-item JSON, not accepted from the string in the envelope.

| Measurement | Result |
|---|---|
| Canonical envelope SHA-256 | `2388945742c0271a9cce01c60c7b926ed62b1b19cd98b15239e04c84eeb085e6` |
| Canonical packet SHA-256 | `db20176e1093177e932cd1f22db4c313f0e2c35b04dfba0ed8a04dbfca0f3405` |
| Packet reopened before/after | 7/7 exact sizes and SHA-256 values; no escapes or missing files |
| Frozen census before/after | 368/368 exact sizes and SHA-256 values, totaling 54,729,254 bytes |
| Current native schematic SHA-256 | `044c0cea6504fc08b0115a60a30e4076d96ea8ae2c05e83159a40b936755acf6` |
| Current raw netlist SHA-256 | `c4ded19290cfcd88744a49fe4e9f5f380b755974937acf3d3d2474ee0fdd5b1a` |
| Baseline raw netlist SHA-256 | `84bf1202fa7af5b77c3d52961f3cba81da3c6e688e202e6d7b4216e71440698b` |
| Baseline owning-normalizer SHA-256 | `32353f2259a5b903725e25bf54d192f9b2b5bc3a290e89d145a90e65400aba70` |
| Current circuit.json SHA-256 | `99f3d38e3b471ad7eb0592c7f6fbe4d64f8f061003b7f2d7cc9f34e839be23bb` |

The 368-file statement is exact coverage of the declared census, not an OS-level read/write trace. I additionally reopened every tracked file under current `02_parts` (131 files), `03_src` (47 files), and `03_tscircuit` (11 files) against the corresponding immutable engineering-subject Git object. All 189 files matched. Git comparison of baseline versus current engineering/source/library/rule domains identified only the six changed/added files described below; no rule, part, shared tool, or external-hardware authority changed.

## Complete netlist comparison and actual delta

Both netlists were parsed completely using an independently written, balanced S-expression parser preserving every atom, field, nested list, and duplicate occurrence. It did not rely on same-line regex extraction, equal counts alone, or selected pin samples. The owner's normalized digest was called directly and an independently transcribed normalization was checked against that exact hash on each input before it was used to expose the remaining tree delta. All normalization code is temporary diagnostic code; no owning function was modified.

Owning normalization removes only export date, instance UUIDs, the single design source pathname, Sheetname/Sheetfile properties, and project-derived netclass labels. The separately bound design-rule digest still owns class policy. The complete raw parsed-tree comparison contained exactly 330 changed scalar positions: one export date, 299 component instance timestamps, and 30 pin-list positions. There were no other raw parsed-field differences. The export dates were `2026-09-07T16:50:16` and `2026-09-07T18:50:07` as stored in the files; these are not this review's clock readings.

After owning normalization, exactly two unit pin lists differ:

```text
U_ADC.A baseline:
40 39 42 41 46 45 48 47 14 13 16 15 20 19 22 21 1 12 43 18 6 5 8 9 17 31 30 33 44 49 2 3 4 10 11 7 32 23 24 25 26 27 28 29 34 35 36 37 38
U_ADC.A current:
40 39 42 41 46 45 48 47 14 13 16 15 20 19 22 21 1 12 43 18 6 8 17 5 30 9 44 31 49 38 4 35 36 37 2 3 10 11 7 32 33 23 24 25 26 27 28 29 34

U_RST2.A baseline: 3 1 2 8 4 5 6 7
U_RST2.A current:  3 2 1 8 4 5 6 7
```

U_ADC has all 49 distinct physical symbol-pin numbers exactly once in the same unit; U_RST2 has all eight exactly once. U_ADC changes 28 sequence positions and U_RST2 changes two. Sorting only those membership lists, after explicitly asserting no duplicate numbers and equal complete list contents for all 299 units, makes the entire parsed normalized netlist tree equal. This is a diagnostic equality proof, not a replacement review hash. No pin moves between units or between nets.

Exhaustive comparison denominators:

| Electrical class | Measured equality |
|---|---|
| Unique component references and complete non-normalized component fields | 299/299 |
| Units and their complete physical pin membership | 299/299 units; 868/868 pin entries |
| Complete library-part definitions and library records | Entire parsed subtrees identical |
| Complete nets, including codes, names, classes, and node records | 205/205; unchanged order as well as contents |
| Unique `(reference,pin)` node ownership | 868/868; zero missing, duplicate, or reassigned owners |
| Node pin functions and types | Entire records identical; 828 passive and 40 passive+no_connect |
| Sanctioned NC records | 40/40, same pins and separate unconnected net names |

The 40 NC pins are J10.1,3–8; J11.3–12; U_ADC.26–28; U_DUMP.1; U_ESD1–8.1,2; U_LDO.5; U_LDO_EN.1; U_OE.1. They are not omitted from the 205-net/868-node denominator.

## Independent source, native, parts, and alias cross-check

An independent union-find reconstruction connected every `source_trace` endpoint and every declared internal port group in both baseline and current circuit.json. Named nets were assigned by the actual source-net endpoints; producer connectivity-key metadata was checked against that reconstruction rather than trusted as the sole connection authority. Each connected component resolved to exactly one named electrical net or a sanctioned isolated port.

All 299 source component identities/values/sourcing fields and all 868 port number/name/hint fields are unchanged after separating the explicitly non-electrical source-group identifiers. All other source-port fields were also compared. All 165 named source nets and their electrical flags are identical; adding the 40 isolated NC nets produces the native denominator of 205. Every reconstructed source port was checked against the native-exported `(reference,pin)` owner and pin function, including the converter's ordinary leading-N digit-rail convention and pin-name suffixing. Native values were compared using the actual declared passive display value or the existing supplier-code/MPN precedence; no MPN substitution was inferred from a visual label.

Source traces increase from 1,227 to 1,244. The 17 extra records create no new electrical ownership: the full independently reconstructed graph remains identical. Component source-group identifier changes are only `233→240` for 291 components, `168→169` for four, and `172→173` for four. These are producer container IDs, not component, pin, or net identities.

All 77 part.yaml files were compared byte-for-byte to the baseline Git objects, not merely compared as selected ratings. Their exact aggregate digest independently matches both current and inherited hashes. The current 299 references use 58 distinct dossier MPNs. Every component footprint equals its selected dossier footprint. Every dossier physical pin is represented: 871/871 physical-pin occurrences reduce to 868 symbol/source pins only through the three explicit, unchanged Q_IN fused-drain aliases, physical 6,7,8 to schematic/footprint identity 5. Each alias retains `fused: true`, its reason, and its manufacturer/package citation; its function remains DRAIN_COMMON. There are zero undossiered pin occurrences. No independent package-figure re-derivation or physical land inspection is claimed here.

All 14 adopted rule YAML files and route.yaml are unchanged from the accepted baseline. The owning rule-digest implementation was read and recomputed without modification; its semantic projection (including the documented flow-only exclusions) yields `14603bc34e244ce702e97a3b14251090eeb88377107e26293fb6ace4d1d26fd9`. Because the complete underlying rule files are unchanged as well, the digest projection cannot conceal a new rule-byte delta in this rebind.

A fresh KiCad 10.0.4 export read the exact current native schematic and wrote only `/tmp/carrier-topology-rebind-1353d047.L3rkTC/current-native.net`. Its raw hash is `884b25b5b370e74daf1a410ad6a3734545a9ca33fbb28d5d8b9d29eda1c7e95e`; its owning normalized hash exactly equals the current subject `ac2b772d...c227b`. Its complete normalized parsed tree equals the current netlist, without any additional unit-order sorting.

The native file was also parsed directly: 489 symbol instances with unique references comprise 299 electrical components and 190 power symbols; 301 embedded library definitions exist. Every electrical component is unit 1, in_bom=yes, on_board=yes, dnp=no. All 868 unique instance/library pin identities, values, footprints, and pin functions agree with the current source and netlist. Each of the 40 distinct native no_connect coordinates was mapped to the actual transformed symbol-pin tip; its exact `(reference,pin)` set equals the source and exported NC set. The independent 299-reference manifest also equals the native/source/netlist reference set.

## Source-delta review

The complete supplied 11,631-byte patch was read and independently regenerated with Git over baseline→current `03_tscircuit/src`; its bytes exactly match SHA-256 `d9a1b8799cea1a1369e515e959182e565c8232f6b9fe564905496f9f28d04e19`.

The patch changes two source files: `crow_audio_carrier_v1.tsx` adds the resistor return-net argument to a presentation helper; `schematic_presentation.tsx` changes poses, pin-side arrangements/spacing, ground/rail label placement, configuration labels, and the FSYNC_BUF output marker. The pin-side and shared-label changes are potentially electrically consequential and were therefore not accepted from their names: the complete reconstructed graph, native NC map, and netlist ownership comparisons above establish their equivalence.

In particular, the consolidated U_ADC ground label owns the same ground pins; its supply labels retain 5,9,31,38 on 3V3_ADC; its 32/33 label owns the existing shared LDO_D_FILT net; configuration labels reuse existing resistor endpoint nets; and the explicit FSYNC_BUF marker joins the existing U_CLK.2/R_FSYNC.1 endpoints. These are explanations of the complete measured equality, not its substitute.

The full Git engineering-domain delta additionally contains the regenerated circuit.json/PDF and two new project-local tests, `test_schematic_ground_clearance.py` and `test_schematic_ink_clearance.py`. Both added test files were read completely. They are read-only presentation diagnostics, not changes to electrical generation or annotation authority, and were not run or used as acceptance evidence. No other source, part, rule, shared-tool, or external-hardware change was present in that comparison.

## Findings, inherited obligations, and exclusions

No new electrical-equivalence defect was found. The two unit-order changes are fully explained above and do not require a new ratings derivation. The full baseline design judgment is INHERITED, not remeasured.

The following baseline findings all remain open/recorded exactly in their admitted scope:

| Inherited ID | Preserved qualification |
|---|---|
| TOP77-Q1 (P1) | Startup, fall, partial-power and loop/reverse behavior remain conditional; physical POWER-COLD/START/FALL/LOOP/REVERSE evidence remains owed. |
| TOP77-Q2 (P1) | Threshold margins retain prototype-only resistor drift assumptions; POWER-DRIFT/post-reflow/hot measurements remain owed. |
| TOP77-Q3 (P1) | Isolation and noise/THD/phase performance are not physically qualified; typical charge injection is not a guaranteed maximum; signed numeric functional acceptance criteria and POWER-AUDIO testing remain owed. |
| TOP77-Q4 (P1) | Hot delivery, protection selectivity, thermal and pulse performance are unmeasured; no precision PPTC current-limiting claim is added. |
| TOP77-Q5 (P1) | First-power card/current-limit procedure reconciliation remains HOLD before energization. Prior calculated 135.12 mA conditional no-audio and 163.87 mA full-allocation figures versus the old 120 mA card are inherited calculations, not measured startup current and not permission to raise a current limit. |
| TOP77-N1 (P2) | Preserve the actual local-ceramic ownership in the FILT banks and the inherited 8.02→8.12 ms bookkeeping distinction below the declared 10 ms screen. This review did not recalculate or physically verify that fall time. |

All connector geometry/physical qualification, analog performance, timing, thermal, startup/power-down, fault/protection, delivery, sourcing, first-article, and order-day tests retain their existing holds. The table is not a new acceptance of the inherited numerical assumptions.

Diagnostic disclosure: fresh native export returned zero but printed `Warning: schematic has annotation errors, please use the schematic editor to fix them`. I did not suppress it or equate exit zero with all-purpose cleanliness. A separate fresh diagnostic ERC wrote `erc.json`, raw SHA-256 `7750c084de1aa27185fa7e9b60475d445d21ca9772d8aee1c1950a79dc1b3446`, with zero errors and 2,076 warnings: 1,587 endpoint_off_grid and 489 lib_symbol_issues. It contained no annotation-specific violation. The warning's broader root cause was not established. Unique native references, units, pin ownership and exact fresh export parity were independently verified, so the warning does not conceal an unexamined equivalence delta. It is not silently promoted into a waived ERC baseline. All exported electrical pin types are passive (or passive+no_connect), as in the baseline; thus ERC is a limited connectivity/document diagnostic, not a fresh active-pin electrical-compatibility proof.

Temporary checker-development corrections were confined to these independent scripts: initial probes assumed every node had pinfunction, omitted a Python Path import, or treated native pin names as already suffix-qualified. Those probes failed visibly, the correct artifact encodings were inspected, and the corrected checks passed. No subject bytes or owning gates were changed to obtain a pass.

## Reproduction evidence

All temporary scripts execute with `python3 -B` and write no repository files:

| Script | SHA-256 |
|---|---|
| verify.py | `821133a87cfb9b9b8be57540eb75751e89b1c8b37d888a956d71cd15a5d8cc67` |
| compare.py | `f0a169387f84421ff408a7b750bc3191b5371955369457e31f257e13ea6a5d4f` |
| source_bridge.py | `10951793ae5705a7f086cf713d5bff9a91e32e78785c8f1a375fa5b83bf981ba` |
| native_check.py | `58e381cdd9e0c1dbf59cb5fdf8fab59cea5368ff0996e2917c0ad71e831e544c` |

Root is responsible for reading and archiving this witness verbatim, recording disposition/adoption, and reopening the relevant gate against the exact bytes. Delivery of this report is not adoption by silence.
