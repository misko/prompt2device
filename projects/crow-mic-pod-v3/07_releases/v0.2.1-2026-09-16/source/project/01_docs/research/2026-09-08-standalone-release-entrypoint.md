# Standalone pod release — use the packaged native project

Date: 2026-09-08. Scope: an independent, offline open/replot check of
`07_releases/v0.1.0-2026-09-03`, not a new seal, order authorization, or
physical qualification. No sealed file was changed.

## Result and correction to the initial diagnosis

**MEASURED:** The archive already contains a runnable native project at
[`source/project/04_kicad/crow_mic_pod_v3.kicad_pro`](../../07_releases/v0.1.0-2026-09-03/source/project/04_kicad/crow_mic_pod_v3.kicad_pro).
Copy or extract the **whole release**, then open that project. Its sibling
`../03_src/lib/` contains the required custom footprints and two local models.
Opening this project in a fresh temporary copy gives native DRC **0 violations /
0 unconnected / 0 schematic-parity issues**, without any library repair.

The earlier statement that the *whole archive* needed missing-library repair
was too broad. The extra flat `source/crow_mic_pod_v3.kicad_pcb` copy does produce
seven `lib_footprint_issues` warnings because its relative library/model paths
resolve differently. Those warnings are real, but do not describe the nested
native project. The sealed order README does not explain this distinction.
The shared policy auditor's existing `release_artifact_root()` explicitly
prefers `source/project/04_kicad` over the flat convenience copies.

**MEASURED:** Replotting the unchanged nested board with the release export
settings produces all nine Gerbers and both drill files. All **11/11** match
the sealed fabrication files after removing only the plot's dated headers.
No copper, coordinates, apertures, silk, mask, drill content, or net attributes
were normalized away. This is a replot proof, not a full source-conductor
rebuild or an order-side preview.

## Exact subject

- Release seal commit: `95a1903fc941a4e0d76a465fa940556029cb256c`.
- Manifest source commit: `043e365b0f71adcafb08a8429e8747b15be7b835`.
- Manifest SHA-256: `5be954c46b9ecc1166fd2eda9efd854aa8c57ef3702d087983710dad41c6ae32`.
- Board SHA-256, identical in live, flat, and nested copies:
  `a932200e0976418383fae0c131dfe2a5768c00ef261b611762ccd3507f05ca8f`.
- KiCad: `10.0.4-10.0.4~ubuntu24.04.1`.
- Checked against repository HEAD `a17ede026cceabb821738884857e99b6823e056f`.

## Measurements

| Check | Result | Scope |
|---|---|---|
| Original manifest and payload | 223/223 file hashes match; no unlisted payload files | Entire sealed archive |
| Required-artifact checker | 37 required entries present; conditional GLTF absent | Membership, not runnable-path validation |
| Design freshness | PASS | Not sourcing clearance |
| Publication diagnostic | 1 project / 1 board PASS | Explicit pod-only scope, not both-child or main admission |
| Realized-route checker | 22/22 PASS | Exact sealed board |
| Flat-copy native DRC | 7 library warnings / 0 opens / 0 parity | `source/<board>.kicad_pcb` |
| Unmodified nested-project native DRC | 0/0/0, exit 0 | Fresh copy, `source/project/04_kicad/<board>.kicad_pcb` |
| Exact-settings replot | 11/11 fabrication files match, dated headers excluded | Nine Gerbers plus PTH/NPTH drills |
| Deliberately wrong replot control | 10/11 match, exit 1 | One Edge.Cuts coordinate changed by 1 mm in a separate scratch copy |

The first causal experiment copied the already-bundled library to the path
expected by the flat copy; its warnings then cleared with the board SHA
unchanged. That experiment was **diagnostic only**. It was not adopted as a
release layout, was not applied to the sealed archive, and is unnecessary for
the packaged nested project.

## Reproduce the native open check

In a temporary copy of the whole release, run:

```bash
kicad-cli pcb drc --severity-all --refill-zones --schematic-parity \
  --exit-code-violations --format json --output /tmp/pod-standalone-drc.json \
  source/project/04_kicad/crow_mic_pod_v3.kicad_pcb
```

Run from the copied release root. Keep reports and KiCad runtime droppings
outside the immutable original. No special environment override, added
library, network lookup, account, or waiver was used in the passing check.

For fabrication reproduction, retain the sealed board's plot settings and
apply the export settings in the source-commit version of
`skills/jlcpcb-fab/scripts/export_jlc_package.py`: Protel extensions, Gerber
attributes, no frame/mirror/autoscale, and solder-mask subtraction from silk.
The independent comparison uses `fab/artifact_index.json`'s 11 fabrication
members and removes only lines beginning `%TF.CreationDate,`,
`G04 Created by `, `; DRILL file ... date `, and `; #@! TF.CreationDate,`.

The initial plain CLI replot did **not** match those export settings. It omitted
the saved drill-mark plot setting and mask subtraction; `--board-plot-params`
restored the former but used the saved no-subtraction setting. These were
classified command-setting differences, not differences to discard from the
comparison. Replaying the actual export settings matched 11/11 without
changing the board. The Python KiCad binding printed three property-enum
assertion messages, exited 0, produced all expected files, and left input bytes
unchanged; the separate comparison and negative control graded the outputs.

## Evidence locations and identity

Disposable raw captures are under
`/tmp/carrier-fresh-build-20260908.4RBsSy/`; each named run has its own `.log`
and `.result.json` with command, start/end, exit code, timeout and log digest.
The native-project scratch archive and replot scripts/outputs are under
`/tmp/pod-native-archive-recheck-20260908.wd19LB/`. The flat-copy experiment is
separate under `/tmp/pod-release-recheck-20260908.eqjfj3/`. Temporary paths are
diagnostic evidence, never design or release authority.

The actual capture logs/results, three diagnostic scripts, and native/flat
DRC reports are also retained under the project's disposable
`06_build/verification/standalone-release-recheck-20260908-a17ede02/`.

| Run | Exit | Log SHA-256 |
|---|---|---|
| `pod-standalone-drc-recheck` | 5 | `153ccb08ad217ec2c6cd005e9f0fde1082a7b17d47affb57330d804535ff1a01` |
| `pod-standalone-drc-path-proof` | 0 | `8c867ff9d1964db4b5112a77074949dcf7293068dfc272eff6bed059c933733d` |
| `pod-native-project-drc-recheck` | 0 | `36697943d64f3382fd4d8d5a0d3d6e7a5869e04835e357e6a47015dc364b66e0` |
| `pod-native-project-exact-replot` | 0 | `b91267efcd81207cc3ee529fc3dc98cba0c0aac247d7cb3220bdf5628727b195` |
| `pod-native-project-replot-comparison` | 0 | `4377f41ec723287c0366d7c93c4bf608e9a22553f87e0744d0891fb8c0f33363` |
| `pod-native-project-replot-known-bad` | 1 | `54050551cda9ca7e8bc8a6dbd26c4f61c73f63aac0c4a19609b63b1fcc1662ba` |
| `pod-manifest-post-recheck` | 0 | `0345fb608261c9209d59062677464e85a2fbe1b31d40c21734f4527754f0bc2c` |

## Disposition

Do not modify or withdraw the sealed design based on the initial flat-copy
test alone. The native project has now been independently reopened and
replotted successfully. Keep the flat-copy warning and missing README entry
point visible; carry explicit native-project opening instructions into any
successor documentation release, which must follow the normal immutable seal
and review procedure. This working note is not a replacement release review.

Authenticated assembly allocation and preview evidence, connector/cable and
enclosure qualification, and first-article measurements remain absent.
The public 22/22 catalog observation is dated **2026-09-03**, not refreshed by
this offline check. **BLOCKED-SOURCING / DO-NOT-ORDER remains unchanged.**
