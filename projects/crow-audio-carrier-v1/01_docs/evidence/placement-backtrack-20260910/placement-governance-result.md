# Placement governance result — source boundary

Run: placement-governance-20260910T184551Z

MEASURED outcome: source repair validation and durable evidence governance PASS.
Current PCB remains unregenerated and unaccepted. Frozen prelayout/schematic/
sourcing checkpoints are stale forensic inputs; no resume, independent-review
adoption, route, seal or order is admitted.

Source commit: 0a2ee381aca8d195d6c3f2c0ba70bd49a0bf72a5.
Baseline: ac7ec0c9e26301ff16d8575a087457f75454d26a.
Launch HEAD: 6be2615b1cbf5d11cbf2a76014bde99c1ba60b7b.

## Launch and causal diagnosis

MEASURED strict TaskEnvelope validated through pipeline_execution.TaskEnvelope;
SHA256 1fb40cef26050bc8217062538ff00149bc8cf69a2d3bb7c5a19fe77bbc62198a;
600/600 packet members matched exact size/hash before writes. Fresh judgment
owner, exclusive authorized writer; root remained read-only. Hard deadline
2026-09-10T19:01:51Z, 120-second return reserve, one governance candidate,
no replacement or extension.

Independent git-ls-files census and actual full project auditor established
exactly 47 C-ALLOW paths added at ea90042734b2182720c9662be76a50807fa9d13d,
all under 06_build/placement-dback-20260910T180147Z and governed by the nearest
06_build/contracts.md. The contract has no pattern for that directory and
forbids irreplaceable author observations in disposable build storage.
Initial audit rc 1: 17,097 files / 2,920 violations vs 2,873 recorded legacy debt.
The source author inherited that unrelated index defect; changing source-test
expectations could not fix it.

Repair: one exact dated durable 01_docs/evidence child with its own narrow
contract and parent admission; archive/member/relocation manifests preserve all
historical bytes. No auditor, debt ceiling, disposable-tree exception, gate,
source schema, shared template, or electrical requirement changed. Shared
01_docs / 06_build templates were audited: existing durable-docs/disposable-build
policy already owns this project-local retention correction; no generic new
obligation needs a template change. See PROVENANCE.md.

## Preservation

MEASURED original preimage archive: 463/463 files / 94,665,796 bytes; unchanged
manifest SHA256 76c1b6e67c6889c1e8a39926a2d27bd066fa16a1f81b41a7e9f05315c26921fa.
The original ignored archive directory remains locally intact.

Durable archive: f451678d0ca60990de947a7898cbaea952f79f3deb5bb081fed2ab0ddf5a6883.tar.gz

- Archive SHA256: f451678d0ca60990de947a7898cbaea952f79f3deb5bb081fed2ab0ddf5a6883.
- Compressed bytes: 73,221,110; reopened regular members: 540/540, totaling 109,852,061 bytes.
- Cohorts: 463 preimages, 1 unchanged preimage manifest, 47 diagnostic files, 21 original execution files/packets, 8 source-repair snapshots/patch.
- Every regular member reopened and checked against exact name, size, SHA256; no duplicate, symbolic-link or hard-link members.
- Two absolute diagnostic symlink facts retained as metadata only. Old actual source bytes are in the preimages; links do not masquerade as portable source.
- Original reports and TaskEnvelopes remain byte-identical, with original failed statuses and path bindings. Separate archive-manifest.json maps each original path/hash/source commit to its durable member.
- All 47 diagnostic paths were removed from the index only after full archive byte verification; all 47 local file hashes remain identical and git check-ignore confirms they are ignored.
- The source-author result is copied verbatim under this directory as well as inside the archive.

## Exact source and test delta

The applied source is unchanged from the inherited reviewed patch SHA256
51c4a5e511f8bf6d7427848022888638ebcbaccb29697a427336432a17c5e1a9.
Independent reconstruction used git-show of the exact baseline into isolated
06_build/tmp, GNU patch rc0, then byte comparison of both outputs to live
source. Both exactly match base plus reviewed patch and candidate snapshots.

- floorplan.yaml SHA256 9222b1d54568b9bd6b9e35cab94b77d99e8983d5ee5c07828a4637b80b3a519d: add exactly C_VMID1_EXT_1U.2, R_ADC_PD1P.2, U_TDM_SCH.3 to guarded solid GND selection; quiet-components mask ymax 75.3 → 75.8 mm; explicit MAIN caption at [32.5, 73.3], size 0.50, nudge false.
- generate_board_generic.py SHA256 fb6113b1d021ba812d400110a600ad6fa8a28615bbd8c7c7ec2cd9350950fe60: preserve native manufacturer/supplier identity strings, decode escaped values, override stale library fields and hide emitted fields.
- Maintained generator regression reopens a saved native board: source MPN overrides STALE-LIBRARY-MPN, escaped supplier JSON round-trips, adjacent J1 retains absent identity fields. The actual old-producer RED log reports stale library MPN; repaired producer 59/59 PASS on identical current producer/test bytes.
- Three source fixture files only update intended expectations: exact ten guarded GND targets and precise explicit MAIN caption. Retained negative controls reject omitted pads, wrong nets, broad selectors, extra fields and quiet-return shortcuts; other captions/model constraints remain checked.
- tests/README.md documents identity round-trip coverage. No further fixture or source edit was needed by this D-BACK.

## Actual validation

| Check | Result | Actual duration / limitation |
|---|---|---|
| Final full source discovery after last inherited expectation edit, bound 360 s | rc 0, 325 tests / 0 failures | unittest 130.707 s; bounded wrapper 131.001875950 s |
| Staged-index contracts battery, bound 180 s | rc 0, 17 passed / 0 failed; 13 known-bad controls | 4.185759120s; final source staged denominator 17,065 files |
| Generator battery | inherited author rc 0, 59 passed / 0 failed; 35 known-bad controls | complete original log reopened; current producer/test bytes unchanged, so not repeated |
| Original reviewed patch reconstruction | patch rc 0, both target byte comparisons PASS | exact base+patch in disposable temporary tree |
| Generated and frozen packet protection | all 33 protected entries rehashed | includes current generated/checkpoint/sourcing entries and retained diagnostic generated members |
| git diff --cached --check for newly authored source/docs | rc0 with exact historical receipt exclusion | original receipt line 3 has preserved Markdown two-space hard break; no global whitespace setting changed |

Full raw logs and telemetry are source-suite.log/source-suite-result.json and
contracts-staged.log/contracts-staged-result.json. The final source index tree `b7c18a5ed025480c5ca3dfbb4f057351711ac472` was
staged before that battery and verified unchanged before the source commit.
A terminal documentation commit records the actual source hash and telemetry;
its exact staged index receives the same battery before commit. Raw terminal
telemetry remains in `06_build/verification`. No producer was launched here.

Historical limitations remain visible: original generator attempt 58/1 failed,
then 59/0 passed; original 325-test source attempt failed two precise stale expectations.
Its interrupted full rerun has 411 log bytes, no terminal verdict and unknown
wrapper return code; it remains INCOMPLETE. The original source-author contract
battery 14/3 failure remains unchanged in its historical receipt. None of these
partial attempts is rewritten as success by the current passing result.

## Protected current generated hashes

- `projects/crow-audio-carrier-v1/03_tscircuit/build/circuit.json`: `78c7ffbf7defc297dfa6ca88d5b24e2ae9bd4e2de96931c0f8cb91ba1488bb3f`.
- `projects/crow-audio-carrier-v1/03_tscircuit/build/schematic.pdf`: `194529d5a49eda59bfeeb7f028acda030c8916f670518ca241c12e440a282a8e`.
- `projects/crow-audio-carrier-v1/03_tscircuit/bun.lock`: `ec4d9604ff7f7f165c515e4ecac75d4ec3a9d2b6f7fb1be33030f6223218828f`.
- `projects/crow-audio-carrier-v1/03_tscircuit/contracts.md`: `7ce45cb2b09e89c49a34bafadad503aa3883033002eb527395811cab99c81379`.
- `projects/crow-audio-carrier-v1/03_tscircuit/kicad/crow_audio_carrier_v1.kicad_sch`: `43eaaa45fb16a68ee45f910765976f443a4070aafd86d67c9039f3b02bf9a0ef`.
- `projects/crow-audio-carrier-v1/03_tscircuit/manifest.yaml`: `3af1dbfa7630f329bfed20ee4b8965fecd99617cbdb58eb199c0cac1ef379ba2`.
- `projects/crow-audio-carrier-v1/03_tscircuit/net_aliases.txt`: `311a411fce5e0f054be9f387ac634871c45b15f6b5411b4ab09f8d337ff2dd0f`.
- `projects/crow-audio-carrier-v1/03_tscircuit/package.json`: `27c670885b6bb15d4ecc917d6ee1601cc352f79114ae3888910d3de21b4c55da`.
- `projects/crow-audio-carrier-v1/03_tscircuit/parity_padmap.txt`: `3c50042368cc904ddd03ee71abe6a17af9835f8db095beeb052e026c281cd2d5`.
- `projects/crow-audio-carrier-v1/03_tscircuit/src/crow_audio_carrier_v1.tsx`: `96c0efc60c634a9c0a5ac2ed9cec58b0cab4b6170476da46fc4210ba0aa9196f`.
- `projects/crow-audio-carrier-v1/03_tscircuit/src/schematic_presentation.tsx`: `4c62912af9260086c5fd110f2f85b3d512e1f3ca806284e75c29e2f02bebdaf7`.
- `projects/crow-audio-carrier-v1/04_kicad/crow_audio_carrier_v1.kicad_dru`: `94251d1c7cb043c66d402d55b5cf89bac74f7ae0927b012556113ae56d7a2471`.
- `projects/crow-audio-carrier-v1/04_kicad/crow_audio_carrier_v1.kicad_pcb`: `dd348351660637ec04671a764c2bda369896758bb362829ec7fe90cc7a6bb292`.
- `projects/crow-audio-carrier-v1/04_kicad/crow_audio_carrier_v1.kicad_pro`: `4a1040e34967d6610bd5032e46b3c2d0e24863370106f7e220d88d4dd633c61d`.
- `projects/crow-audio-carrier-v1/04_kicad/crow_audio_carrier_v1.kicad_sch`: `43eaaa45fb16a68ee45f910765976f443a4070aafd86d67c9039f3b02bf9a0ef`.
- `projects/crow-audio-carrier-v1/04_kicad/fp-lib-table`: `74d263c3fd8c21dcd597750eee4aea45b00f7b7ef7d5fdd73d81da6043abe50d`.
- `projects/crow-audio-carrier-v1/04_kicad/refdes_waiver.json`: `1e9621ad12f0e020f83ec3f9964d229cded2ea3f7f8786c9d0b85cbb565c06f1`.
- `projects/crow-audio-carrier-v1/06_build/checkpoints/prelayout-inputs.json`: `9a24686299cd11f0703f86bd0813030c8f8537d8428b674d9808bf59bc568b25`.
- `projects/crow-audio-carrier-v1/06_build/checkpoints/prelayout.json`: `30b51954763fe85f5cf4945cf819245d39019dad2581d7e86b78ee1a9e7e84a7`.
- `projects/crow-audio-carrier-v1/06_build/checkpoints/schematic.json`: `a856acc5eb47d4d394ce6758bb27531d0debc210c7f581b0ea0d7d8a7cdef0cb`.
- `projects/crow-audio-carrier-v1/06_build/sourcing/prelayout_request.json`: `c78db993b7d9bb7e34d41960dcf6c6a08c061b425947aa2b363a1dfda099b0c4`.
- `projects/crow-audio-carrier-v1/06_build/sourcing/prelayout_response.csv`: `2f7426cf5d959bd3fb9e4e0c944c03d7be3371ac2e64235fe36768ba8aa33d32`.
- `projects/crow-audio-carrier-v1/06_build/sourcing/public_catalog_stock.json`: `84b0349aa562cfd2052b094c809c43dc16d727b12aadf8df1e355cd79a27b81c`.
- `skills/pcb-design/templates/contracts/04_kicad/contracts.md`: `28c1ace226b6806d482fd3e2243b1c27ee010ee3dcb3c97503fb5a1d19174764`.

## Complete 47-path disposition

All paths below are relative to the original diagnostic directory. Every row is
retained locally, index only removed, and durably archived under
`diagnostic/projects/crow-audio-carrier-v1/06_build/placement-dback-20260910T180147Z/`
with the same suffix. Full exact hashes and original commit are in
diagnostic-disposition.json; archive-manifest.json independently binds members.

- `candidate-1-source.patch` — preserved and relocated.
- `candidate-1/04_kicad/crow_audio_carrier_v1.kicad_dru` — preserved and relocated.
- `candidate-1/04_kicad/crow_audio_carrier_v1.kicad_pcb` — preserved and relocated.
- `candidate-1/04_kicad/crow_audio_carrier_v1.kicad_prl` — preserved and relocated.
- `candidate-1/04_kicad/crow_audio_carrier_v1.kicad_pro` — preserved and relocated.
- `candidate-1/04_kicad/crow_audio_carrier_v1.kicad_sch` — preserved and relocated.
- `candidate-1/04_kicad/fp-lib-table` — preserved and relocated.
- `candidate-1/attempt-notes.md` — preserved and relocated.
- `candidate-1/config.yaml` — preserved and relocated.
- `candidate-1/drc-before-project-restore.json` — preserved and relocated.
- `candidate-1/drc-before-project-restore.log` — preserved and relocated.
- `candidate-1/drc.json` — preserved and relocated.
- `candidate-1/drc.log` — preserved and relocated.
- `candidate-1/generate.log` — preserved and relocated.
- `candidate-1/p-drc.log` — preserved and relocated.
- `candidate-1/proof.json` — preserved and relocated.
- `candidate-1/proof.log` — preserved and relocated.
- `candidate-1/refdes_waiver.json` — preserved and relocated.
- `candidate-1/regression-execution.json` — preserved and relocated.
- `census.py` — preserved and relocated.
- `classify.py` — preserved and relocated.
- `connectivity.json` — preserved and relocated.
- `field_assert.py` — preserved and relocated.
- `fields.py` — preserved and relocated.
- `floorplan.candidate.yaml` — preserved and relocated.
- `full-residual-classification.json` — preserved and relocated.
- `generate_board_generic.candidate.py` — preserved and relocated.
- `launch.json` — preserved and relocated.
- `make_candidate.py` — preserved and relocated.
- `negative-original/04_kicad/crow_audio_carrier_v1.kicad_pcb` — preserved and relocated.
- `negative-original/04_kicad/crow_audio_carrier_v1.kicad_prl` — preserved and relocated.
- `negative-original/04_kicad/crow_audio_carrier_v1.kicad_pro` — preserved and relocated.
- `negative-original/config.yaml` — preserved and relocated.
- `negative-original/generate.log` — preserved and relocated.
- `negative-original/refdes_waiver.json` — preserved and relocated.
- `output-manifest.json` — preserved and relocated.
- `parity-census.json` — preserved and relocated.
- `physical-causes.json` — preserved and relocated.
- `physical.py` — preserved and relocated.
- `protected-before.json` — preserved and relocated.
- `protection-rehash.json` — preserved and relocated.
- `refilled-baseline.kicad_pcb` — preserved and relocated.
- `refilled-baseline.kicad_pro` — preserved and relocated.
- `rehash.py` — preserved and relocated.
- `verify_candidate.py` — preserved and relocated.
- `write_receipt.py` — preserved and relocated.
- `writer-scope.json` — preserved and relocated.

## Next fresh mechanical owner

Start from the committed source and verified compact handoff. Reopen the exact
463-preimage archive and preserved stale checkpoint bindings, deliberately
archive/reopen that frozen boundary under the owning conductor, and perform a
fresh canonical restart. Do not restamp or resume stale checkpoints. Regrade
native schematic/board identity, placement, all classified DRC/unconnected/
parity findings, and fresh independent reviews on newly produced exact bytes.
This task does not admit routing or convert source test success into board
acceptance. All protected generated, model, route and release authority stays
unchanged during this governance task.

Terminal result finalized at 2026-09-10T18:57:23+00:00. All authorized execution processes have completed; no further engineering work is admitted by this receipt.
