# Placement journal — carrier coordination

## 2026-09-08 16:41 UTC — finish: first carrier PCB generated and independently reopened

- did: Observed the same fresh worker through one16.347-second resume and
  terminal handback; lease released16:39:01Z, final JSON16:39:02Z. Root
  rehashed448 packet/445 baseline/1926 tracked/22 evidence/23 output bindings
  and reopened all five owning receipt validators at16:40:59Z.
- result: MEASURED carrier302 fitted/309total,936pads,877matching native
  pin-net entries,0segments/arcs,9source thermal vias,4GND planes/55rule areas.
  First failure is1/290 P-ADJ-PAIR: U_ADC.7→C_LDO_A.1 gap1.625mm>1.5mm;
  no current DRC, routing/import, placement acceptance or carrier release.
  Pod remains sealed and unchanged. Root local source probes rejected blind
  moves and found a narrowly feasible candidate, not an adopted source fix.
- next: Commit the generated failure and exact source-owner evidence, then
  implement/test the coupled placement correction without weakening limits.
  See child research/2026-09-08-generated-placement-adoption.md. Regeneration,
  fresh placement/pin/render approval and routing remain ahead; all physical,
  first-power, sourcing and publication holds persist.

## 2026-09-08 17:00 UTC — iterate: carrier source correction tested

- did: Corrected only C_LDO_A's pose and added a live-source adjacency/via/
  seed/body regression with real-old-pose and blind-east-shift controls.
- result: MEASURED202/202 carrier source tests PASS in73.240s, with the actual
  positive regression first verified red. Source gap1.495mm meets unchanged
  1.5mm allocation. Old421-input checkpoint rejects onlyfloorplan.yaml.
- next: Commit source boundary, archive stale checkpoint cohort and regenerate
  through the full conductor. Carrier PCB still unaccepted/unrouted; pod seal
  unchanged, all physical/sourcing/order/publication holds retained.

## 2026-09-08T12:17:00-07:00 — carrier silk source progress and report-cap correction

- did: Carrier source library/caption repairs tested against old failing geometry;
  archived old checkpoint cohort and independently compared disposable boards.
- result: MEASURED213/213 source tests;22silk findings removed,15clearance+8thermal
  remain. Native graph proves500opens, not the earlier capped499report total.
  All877pad component memberships and copper area on4/4layers unchanged.
- next: Source-owned electrical corrections, full regeneration/review and routing.
  Carrier remains unaccepted/unrouted; pod seal unchanged. No publication or order.

## 2026-09-08T12:28:50-07:00 — carrier ground-mode correction verified

- did: Eight exact source-pad solid connections, old-source RED/GREEN controls
  and independent saved native refill/copper/endpoint checks.
- result: MEASURED219/219 tests;0thermal/0silk/15clearance,498uncapped opens,
  0parity. Two CM ground islands join main GND; five quiet exclusions remain
  untouched and all dedicated quiet-return endpoints remain isolated for routing.
- next: Fifteen package-local clearance conflicts, full regeneration/review,
  remaining silk ownership, routing and release. Pod seal and all holds unchanged.

## 2026-09-08T12:59:21-07:00 — carrier package-pad correction verified

- did:15exact pad-pair areas/rules authored with strict pad-only guards;
  native pre-fix RED confirms tracks/vias would otherwise inherit the exception.
- result:224/224 carrier source tests; disposable refill0violations/498opens/
  0parity. Native geometry, all877pad component memberships and4filled layers
  unchanged. Shared52/52emitter,32/32preflight and18/18native control sites pass.
  Full repository contract suite13pass4fail is recorded, not waived or green.
- next: Full carrier regeneration/fresh reviews, silk ownership/readability,
  routing498classified connections and release. Canonical carrier still old,
  pod seal untouched. No main push or order; all physical/sourcing holds remain.

## 2026-09-13T05:19:54 UTC — both child schematic renewals accepted; placement handoffs active

- did: Adopted independently reviewed shared RJ45 Fab source atada576b0, normally regenerated both child schematics and adopted fresh topology/readability judgments at30bdc085pod/64619ce5carrier.
- result: MEASURED owning PR-REVIEW2/2PASS each;333carrier components/985terminals and40pod components/103pins, all23drawing pages inspected. The exact source retains Würth615008160221 jacks and factory Weidmüller8909650150 Cat6A cords, custom analog/DC, power-off mating. Source marks represent native free fingers; no model, pad, courtyard, copper or extraction-threshold change. Both required fresh EXCLUSIVE placement workers are live; root has no child writer ownership until their actual FINAL/closure.
- next: Reopen current normal placement/model/orientation results, preserve complete DRC classification and present final current native orientation images for explicit user approval. Then mandatory placement reviews/pilot, actual routing, layout/fab/release gates remain. Earlier orientation request is deferred. Existing parent system commissioning hold, child physical obligations23carrier/9pod and FIRST-ARTICLE-ONLY/DO-NOT-ORDER remain; neither child nor system release completion is claimed.

## 2026-09-13T05:33:31 UTC — current child model registration closed; orientation review pending

- did: Both normal placement successors completed and actual delivery closed PASS; root reopened current native results and independent supplemental geometry binding.
- result: MEASURED final native carrier0/499/0,pod0/58/0, all individual opens retained. Carrier model6/6 and machine orientation9/9; pod2/2 and1/1. All9 current native jack poses/pads/source shapes/models bind accepted supplemental geometry. Both former Fab mismatch groups removed by normal generation. Root sole writer; no active worker.
- next: User confirmation pending on current carrier3388c531a98d6bab/pod5e2631d88395ccb9 gallery16views. No approval inferred. Independent placement/pilot, fresh routing and both complete release lines remain owed; parent system hold and physical23+9obligations unchanged. FIRST-ARTICLE-ONLY/DO-NOT-ORDER.


## 2026-09-13T17:19:47 UTC — user requires top-only fitted SMD; source redesign opened

The verbatim user directive is appended to both boards and parent BRIEF. Accepted manufacturing decisions carrier0029/pod0008/parent0014 require all fitted SMD on F.Cu, including manual/consigned parts, with modest board growth authorized. Both assembly.yaml now declare sides:[top]. Existing native layouts remain unchanged and FAIL the new requirement: carrier306 fitted SMD has16bottom (F1–8,U_ESD1–8), pod31 has1bottom (U3). Top-only placement is not yet implemented or accepted. Bare fiducial/test copper and THT joints do not count as fitted SMD.

Both obsolete mixed-side source tasks delivered actual FINAL and closed PASS17:09:31.744577Z/17:09:31.942352Z (delivery only); engineering INCOMPLETE is retained. Carrier2/2candidates spent: VMID4/4 dominance,12thermals cleared,20/20silk ownership and R_PWR_PU2.472974mm gap were author-measured, but C_VDDA1_10N.2 isolated ground island and AP63205 module-type applicability remain. No source adopted. Pod one unqualified R13/C10 proposal was preserved; no candidate generation or routing pilot ran. Durable archives carrier b36e0248e8e7caa87efc8779c2e17bdc2874de6cdabc0f56744511171a7cb40c (649 frozen/290 inner) and pod eb24335683b7db88deb5d5b4a2676a2441eacee352a33832c4cfb59356359058 (370 frozen/43 inner) preserve actual handbacks. Prior attempt budgets remain spent.

New shared isolated source owner /root/rj45_top_only_source1 has816frozen inputs, envelopea3b0f0ec4fc4ac7b4701090a80ca852e5d1beb4e35e19c27496f05586b1e6b7b, workcut17:46:27Z/hard17:53:27Z, atmost2native candidates/0routing pilots/0replacements. Root owns both live boards. Author early geometry reports jack audio pin5 sits at least6.36mm inside nominal body; old4.0mm padcenter/4.2mm bottom-prefix limits cannot carry unchanged to an external top clamp. This is inherited preliminary diagnosis, not adopted replacement limits. Exact source geometry, protection path and primary guidance must support a reviewable replacement. Factory jack/cord/pinmap remain selected.

Root assembly-side checker proposal independently reads native numbered SMD lands and CPL side, includes manual population and reports missing legacy policy as ungraded. Public CLI regression pre-fix had4known-bad families falsely exit0; initial zero-test filter diagnostic is excluded. Current48/48assembly tests pass (24known-bad). Fresh independent source reviewer /root/assembly_sides_source_review1 has57frozen inputs, envelope7e8e144f0a1ace617ab9365995793d17c3d24d796310476b0621d18c956a7dc5, workcut17:32:19Z/hard17:39:19Z. No pending verdict adopted. Source/checkpoint/placement/routing/export/twin and changed orientation subjects must renew after exact source acceptance. FIRST-ARTICLE-ONLY/DO-NOT-ORDER; neither new release minted.


## 2026-09-13T17:34:23 UTC — independently accepted assembly-side enforcement; physical redesign remains open

Fresh actual FINAL closed PASS at2026-09-13T17:32:52.897689Z; engineering SOUND binds7exact sourcefiles, all reverified live before source acceptance at2026-09-13T17:33:37.621117+00:00. Checker SHA44b2e11314b9abdbe0693bf6d167e4f85d7906c96240df7c2a675a593a22a0e0. Independent8/8targeted tests (24actualCLIcalls) and10/10independent cases passed;67/67frozen inputs and399archive members reverified. Durable review411a21de68867a085848e2f9f046550e460afd284a9eac2ad013eefe758d66d9. Rootfull49/49assembly suite passed25knownbad. Repository final audit separately owed before commit; no waiver.

Original reviewDEFECTIVE308cf93c found duplicateDNP/manual rows coulderase fittedbottomSMD. Root reproduced REDfalseexit0, corrected duplicate-disposition refusal and retained ambiguousrefs in denominator; bothroworders andtestpointvariant nowreject. An incorrectly dispatched same-reviewer continuation inheritedcontext underaFRESHenvelope; it was stoppedbeforeany repairedcandidate tests and closedINCOMPLETE, archivee462c5cf retained. Actualfreshreviewer /root/assembly_sides_fresh_review2 provides the accepted verdict; no acceptance or fresh-context claim derives fromthemisdispatch. Rootcheckpoint19e70a7528d9148b4b99ee21427041db96a052b055b023887ae7bf7c16aced09 preserves99reopenedmembers of userintent, preimages, rawRED/GREEN, nativegap andsourceacceptance.

Both live nativeboards unchanged andnoncompliant: carrier16bottomSMD/pod1bottomSMD. Isolatedtop-only sourceowner reports pod60x40candidate has0fixedcourtyard/padcollisions; carrier153x100candidate reduced10collisions to1remainingF1/H1courtyard overlap0.300mm. These are inherited candidate observations, not adopted geometry. Original2/2nativecandidatecap remainsclosed; no third trial or routingpilot authorized. Await complete source handback, thenfresh independent D-BACK judgment of mounting/outline and protection geometry before owning-stage correction. OldB.Cu/prefix/fusegeometrylimits cannot be silently increased; userboardgrowth authority remains. Retain unrelated ADC/module and routing obligations. Rootsolelivewriter. FIRST-ARTICLE-ONLY/DO-NOT-ORDER; neither newrelease minted.

Root final staged repository contract suite17/17PASS (13knownbad), existing2873violations/26units held with0strays; no ratchet change. Documentation15/15, authorityPASS and disclosure14/14 were separately measured. Staged diff whitespace clean; all3beacons parse. These are source/governance checks, not acceptance of current bottom-populated boards.
