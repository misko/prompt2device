# FR12 independent immutable seal review — PASS / DO-NOT-ORDER

Reviewer: SOL6.1-high FR12 independent seal reviewer (release_integrated).
Author: Root first-run seal author. This review grades preservation, provenance
and committed replay; it does not re-author the accepted engineering or authorize
ordering, publication, firmware or physical work.

Source commit S: `08bd3a485c23039bb1c27bdcfb8521bf454c935a`.
Seal commit T: `a74470eaee97effcfab69fb43fdf302f0cac1865`.
Seal record SHA256: `c2b89fdaf364b7538cd58bf0e52a150c8bde3b9cd1f2b52f2010adfafc398a50`.

Actual full public seal check completed **08:06:18.773630 UTC**, exit 0, no signals.
I read its durable command/result and exact output. It confirms committed owning
replay; the earlier commit-only false flag was not treated as that proof.

| Scope | Independently inspected result |
| --- | --- |
| Provenance | S has no raw parents; T's sole raw parent is S; only the release is added |
| Complete committed content | 5,077 source files + 5,299 release files = 10,376 exact committed/checkout files |
| Reconstruction | All 5,298 non-seal release members regenerated exactly in reviewer scratch from source bytes proved equal to S |
| Accepted archive | All 5,293 reviewed files, review and receipt preserved; seal record exact |
| Recipient handoff | Both board versions/quantities, 834 resolved index/status/candidate links, authoritative current status and all nine holds preserved |

Repository: `09_release/crow-prototype-v3-first-run-5c10p`.
Recipient entrypoint: `release/INDEX.md`; authoritative design/order status:
`release/CURRENT-STATUS.json` and its human-readable companion. Carrier is
`rev-a-first-run-r3-d3` ×5; pod is `rev-a-first-run` ×10. This is not five complete
eight-pod arrays. SOUND is the accepted bounded prototype-design verdict, not
manufactured or working-qualified hardware.

The current-status records bind the exact accepted review/receipt and candidate
hashes. The original candidate's UNREVIEWED heading is historical and preserved,
not rewritten into self-acceptance. Dated supplier offers are not allocation;
stencil/process/precision/rails/DFM/manual-route/preview/quote and purchasing
closures remain required. The finite NVIDIA/Linux/Python/KiCad runtime is not
portable or an OS image. Physical thermal, firmware, bring-up and deployment
qualification remain unperformed. No order or publication is authorized.

Review diagnostics, including complete before/after committed inventories and
scratch reconstruction, are retained outside the repository under
`06_build/recovery/first-run-d3-release/review-seal/`.
Actual full-check evidence is outside it under
`06_build/recovery/first-run-d3-root-admission/seal-check1-{result,output}.json`.
No repository, source, native, archive, status, journal, receipt or tool was edited.
No owning replay/check/issue/certificate or native CAD was invoked by this reviewer.
Only root may issue and confirm the separate sealed-release receipt after this
settled review. Future corrections require a new version, not a hash refresh.

```json
{
  "schema": 1,
  "stage": "PCB-RELEASE-SEAL",
  "author": "Root first-run seal author",
  "reviewer": "SOL6.1-high FR12 independent seal reviewer (release_integrated)",
  "verdict": "PASS",
  "result": {
    "boards": {
      "carrier": {
        "quantity": 5,
        "version": "rev-a-first-run-r3-d3"
      },
      "pod": {
        "quantity": 10,
        "version": "rev-a-first-run"
      }
    },
    "committed_owning_replay": true,
    "design_verdict": "SOUND",
    "files": 5299,
    "order_verdict": "DO-NOT-ORDER",
    "release_id": "crow-prototype-v3-first-run-5c10p",
    "role": "sealed_release",
    "seal_commit": "a74470eaee97effcfab69fb43fdf302f0cac1865",
    "seal_record_sha256": "c2b89fdaf364b7538cd58bf0e52a150c8bde3b9cd1f2b52f2010adfafc398a50",
    "source_commit": "08bd3a485c23039bb1c27bdcfb8521bf454c935a",
    "version": 1
  },
  "checks": {
    "provenance": {
      "verdict": "PASS",
      "rationale": "I inspected actual raw Git commit headers and streamed/hash-checked committed blob bodies with replacement objects disabled, not graft-sensitive history summaries or authored clean fields. Source S=08bd3a485c23039bb1c27bdcfb8521bf454c935a is the isolated root commit with no parents; seal T=a74470eaee97effcfab69fb43fdf302f0cac1865 has exactly S as its sole parent. All 5,077 committed source files equal the actual source checkout and source-files manifest, including reconstruction inputs, accepted archive record, exact independent design review/receipt, seal authority/contract and frozen tools. T preserves every source blob and adds only the exact 5,299 release paths. The retained seal tool hashes to the adopted 39690252... owner, authority to bbba94ea..., archive record to 97d98924..., design review to 5c8b7bc9... and release-reviewed receipt to 80e50a6f.... This is actual local Git provenance, not a signature or protection against replacing both trusted verifier and identity."
    },
    "completeness": {
      "verdict": "PASS",
      "rationale": "I inspected the actual committed recipient INDEX and CURRENT-STATUS, both exact board/version/quantity records and the complete artifact-role census. Carrier rev-a-first-run-r3-d3 quantity5 and pod rev-a-first-run quantity10 are linked as the current partial batch, not five complete arrays; full eight-channel capability remains. All 5,293 reviewed archive files are preserved byte-for-byte alongside the exact accepted design review/receipt and generated status/index records, giving 5,299 release files. Source and release contain editable native PCB/project/schematic/netlist/resources, PDFs, manufacturing plots/PTH/NPTH/ZIP/BOM/CPL/population, registered STEP/views/detail evidence, substantive current D3/R3 calculations and the exact runtime/tool closure. I validated 834 links across final index/status/candidate index. From source bytes first proved equal to S blobs, the unchanged deterministic constructor reconstructed all 5,298 non-seal release members exactly in reviewer scratch, including derived CURRENT-STATUS/INDEX, not merely a self-rehashed status assertion. Current authority is SOUND/DO-NOT-ORDER; historical candidate UNREVIEWED/DO-NOT-ORDER and diagnostic watermarks remain unchanged and explicitly noncompeting."
    },
    "replay": {
      "verdict": "PASS",
      "rationale": "I read the actual durable full public seal-check1 command completion and output, not the author's summary or the earlier commit-only result. The frozen public owner ran check on this exact repository from07:54:38.823465 to08:06:18.773630UTC, exited0 and received no launcher signals. Its actual result, copied exactly here, binds S/T, both board versions/quantities, 5,299 files, seal-record hash c2b89fdaf364b7538cd58bf0e52a150c8bde3b9cd1f2b52f2010adfafc398a50 and committed_owning_replay=true. The earlier commit result's false flag was explicitly insufficient and was not substituted. I read the frozen owner implementation: full check reconstructs from S and executes preserved owning acceptance in guarded read-only offline scratch, compares the exact accepted release receipt and owning result, and rejects source/archive mutation. The sealed owning-replay record retains offline/archive_readonly=true and exact RTX4090/NVIDIA550.144.03/EGL/vtkEGLRenderWindow profile. The schema2 capsule remains finite Linux/CPython/KiCad/fonts/library and enumerated GPU-node prerequisites, not an OS image or portable renderer; no fallback, tolerance change or hardware qualification is inferred. I did not duplicate the owner replay/check/certificate/issue."
    },
    "integrity": {
      "verdict": "PASS",
      "rationale": "I independently compared the complete 10,376-file working-tree census to actual T blob hashes and the 5,077-file source subset to actual S, including ignored/untracked coverage rather than trusting Git porcelain alone. Entries are regular non-executable 100644 files; no linked, missing, stale, extra or changed member was found. Release inventory is exactly seal.files plus seal.json; seal record hashes to c2b89fda..., and the actual Git delta is exclusively 5,299 added release files. Full original archive and accepted review/receipt equal their pre-seal inputs. Scratch reconstruction is byte-exact, including authoritative status/holds/index. Repository census before and after independent inspection is identical. All reviewer writes, reconstruction, logs, post-commit report and future project receipt are outside the sealed repository; no direct native CAD, source edit, deletion, inventory refresh, amended commit or seal operation was performed. Final read/hash-only review preflight rechecks preservation without invoking owner acceptance. Corrections must create a new release version, not modify this committed seal."
    },
    "handoff": {
      "verdict": "PASS",
      "rationale": "The actual final INDEX directly exposes both board native entrypoints and artifact groups, accepted review/status, candidate evidence index, ordering instructions and seal provenance. CURRENT-STATUS.json binds the exact accepted receipt/archive hashes and repeats all nine policy holds; CURRENT-STATUS.md exposes every hold's reason and named closure role/action. Historical candidate headings remain immutable evidence, not competing live status. All purchasing authority, dated offers versus usable allocation/MOQ/attrition, exact matching/orientation previews, JLC internal stencil optimization versus no automatic paste changes, precision/stack/rails/fiducials/fixtures/DFM/metrology, UNSELECTED manual route, controlled special assembly and actual quote/scope closures remain active. Installed demand stays915SMT+85manual=1000 across32/six identities, not inferred purchasing extras. PCB components plus bare fabrication/setup $530–1350 and separate assembly/manual $500–1400 remain UNQUOTED; external host/storage/PSU/adapters/cables/enclosures/roof hardware are outside that comparison, not free or waived, with no total cap. Qualified R3 restrictions, current conditional D3 thermal allocation/failing sensitivities and complete LS43/LS33/mission controls remain preserved. Unprogrammed prototype design is not working or physically qualified hardware; firmware/bring-up/thermal/audio/retention/deployment work is unperformed without inventing a universal firmware-before-order gate. No vendor contact/upload/purchase/publication/push is authorized, and no post-seal engineering guarantee or lifetime/yield claim is created."
    }
  }
}
```

