# Crow exact-job order readiness

## User sourcing decision on 3 November 2026

The user explicitly selected **keep external sourcing for home-install parts**.
The final-release JLC availability requirement applies to factory-installed
parts. For two assembled carriers and eight pods, preserve external sourcing
and home installation of two Raspberry Pi SC0915 Picos, two TI
LMK6CE012288CDLFR clocks, eight Same Sky CMA-4544PF-W microphones and eight
Same Sky CPE-203 buzzers. Their exact identities, handling requirements and
external availability checks remain required; JLC catalog absence alone does
not trigger replacement of these parts.

This resolves the all-JLC versus home-install scope question in the reviews
below. No purchase, reservation, substitution, assembly reassignment or
manufacturing commitment is authorized by this decision. Factory diode stock,
connector/model verification and manufacturing acceptance remain open. The
goal was marked blocked on unavailable signed-in browser evidence; this
decision does not establish browser reconnection. Release remains HOLD.

## Diode candidate engineering screen completed on 3 November 2026

[Nexperia BAT54S,215 / C47546 review](diode-review-20261103/README.md) now
reconciles the actual r10 clamp topology with the archived protection model.
Source hashes match the published historical manifest; all sixteen carrier
isolation legs, both pod output resistors and the required sink remain correct.
The existing bounded model does not rely on the original 600 mA long-pulse rating;
candidate temperature range covers the unchanged −20…60 °C electronics envelope.
SOL 6.1 high independently conditionally recommends the candidate; five tests pass.
No candidate was adopted. Exact-job stock and vendor placement precede a new
package; all-temperature waveform and actual thermal limits remain prototype
qualification conditions, not newly guaranteed facts.

Exact-code recovery also found JLC microphone/Pico listings not orderable;
those catalog flags do not independently establish manufacturer lifecycle.
The subsequent user decision above resolves the sourcing-scope question.
No production files or drafts changed; release remains HOLD.

## Release sourcing refresh on 3 November 2026

The [38-part refresh and diode shortlist](release-refresh-20261103/README.md)
cover two assembled carriers/eight pods including the home-install lines.
Public counts do not establish immediate PCBA allocation. BAT54S-7-F remains
short in the signed-in draft (4 available, 21 gross needed); exact-code public
recovery is consistent with that shortage. Nexperia BAT54S,215 / C47546 and
BAT54S-QR / C7507573 are credible same-footprint candidates, not adopted parts.
Exact-job supply and remaining fault/temperature/placement checks precede any
production update. Native boards, r10 and JLC drafts remain unchanged.

TinyFish is not currently installed; reconnection was offered. New pod C draft
retains its verified saved pose, with model/hash and outward mouth still open.
Carrier connectors and process acceptance remain open. Final release is HOLD;
the goal stays active. No purchases, reservations or vendor messages.

## 3 November: pod trial-C saved coordinates verified; mechanical review open

[Session report and sanitized evidence](quote-tests/r10-connector-mapping/macbook-c-session-20261103/README.md)
record the separate diagnostic C draft, exact uploaded filenames and local
hashes, and the reopened J1 record: C599441, X 10.556 mm, Y −9.390 mm,
180°, with zero default-panel offsets and angle. C remains loaded in this new
draft; A was not restored there. The earlier baseline-A draft remains separate.
Keep the new draft on HOLD; the next checks are its loaded model identity/hash,
pin and peg replay, and outward socket opening—not a repeat of coordinate
investigation. D2/D3 were omitted only in this diagnostic preview after a
shortage; both remain required for production. Carrier connectors require
separate checks. No purchases, reservations or manufacturing commitments.

Earlier dated findings below are historical; their draft-unchanged and
restore-A statements do not describe the subsequent separate C-draft session.

## Historical backend review: captured J1 geometry supports test C

The [backend numerical review](quote-tests/r10-connector-mapping/LOADED-J1-REVIEW.md)
of MacBook commit `9cec4096` establishes the captured pod footprint's raw origin
and active model UUID. Test C (10.556, −9.390 mm; 180°) aligns all eight captured
pin centres within 0.014 mm and both peg centres within 0.004 mm. A fails;
rotation-only B retains a 1.017 mm error. A fresh public model with the same
UUID/length also registers nominal tail-tip/peg-bottom profiles within 0.022 mm.
The cached browser asset's hash is still missing: do not claim byte equality
or saved-C verification. Four new regression checks and the ten existing
mapping tests pass. Native boards/r10 and JLC drafts remain unchanged.

Follow the new bounded MacBook C handoff: match the cached model, confirm the
saved/effective C pose and outward mouth, then restore A and retain HOLD.
This supersedes the older screenshot-first/origin-unknown recommendations
below. Carrier RJ instances and power J1 remain separate pending checks.
No purchases, reservations, substitutions, vendor messages or approvals.

## Current next step after original skill comparison

The [legacy-tool connector mapping experiment](quote-tests/r10-connector-mapping/README.md)
now measures and replays all ten connectors against retained catalog geometry.
It preserves exact native/r10 bytes and prepares isolated carrier J101 and power
J1 trials. The pod output reproduces test C exactly. Nominal catalog registration
passes; live JLC placement and independent acceptance remain open. The old
generic pad-datum rule includes RJ locator holes and differs from the exact
catalog origin, so it is not adopted blindly. No global rotation rows or vNext
acceptance gates were changed. Follow the linked bounded pod test only when
pin/peg registration is observable; otherwise use the existing read-only capture
or seek authorization for a JLC inquiry. No equivalent TinyFish retries.
All connector manufacturing holds remain; no purchases or vendor actions.

## Current next step: read-only JLC scene capture, before test C

The server's bounded read-only attempt has now terminated: TinyFish reports no
runtime/console or network-body inspection capability and returned no geometry.
See the [attempt assessment and raw result](quote-tests/r10-pod-j1-origin/SCENE-CAPTURE.md#server-browser-attempt-capability-unavailable).
It also reported a disabled placement tab, inconsistent with the earlier
MacBook preview; this remains an observation to reconcile, not permission to
re-upload. Use the MacBook's existing diagnostic session for the read-only
capture. No further equivalent TinyFish retries; all placement holds remain.

Public viewer-code review found model recentering/offset paths and separate
effective-placement/panel transforms. The catalog-origin assumption behind C
is therefore still unverified. Follow the [bounded MacBook capture handoff](quote-tests/r10-pod-j1-origin/SCENE-CAPTURE.md)
to obtain actual J1 pose and loaded footprint/model metadata while A remains
restored. This supersedes the immediate B/C upload recommendation below.
The read-only console procedure is source-reviewed but not live-browser tested.
No signed-in draft was accessed or changed during this code review. No native,
r10 or test-CPL changes; all ten factory connector instances remain on HOLD.
No purchases, reservations, substitutions, vendor messages or approvals.

## Current next step is the pod reference point test

The A/B review identified a possible origin mismatch: native pod J1's electrical
pin centroid is 1.017 mm from the body centre used by the CPL. A new
[diagnostic test C and MacBook procedure](quote-tests/r10-pod-j1-origin/README.md)
changes only J1 Y relative to B, from −8.373 to −9.390 mm, retaining 180° rotation.
The source-bound generator and ten tests verify its derivation and isolation;
this does not verify the active JLC draft's coordinate convention.

Next: use the existing diagnostic draft for one B/C comparison with a 2D
pin-pattern or actual underside view, then restore A. If those features remain
hidden, capture sanitized loaded scene geometry instead of repeating roof views.
No C upload has occurred. All ten factory connector instances remain on HOLD;
carrier RJ and power-jack transformations need separate downstream verification.
Native boards, original r10 and existing A/B files remain unchanged. No purchases,
reservations, vendor messages or manufacturing approvals. Entries below retain
the history; this section identifies the current next action.

## 2 November 2026 MacBook pod A/B experiment

The separate [pod diagnostic draft](r10-pod-ab-session-20261102/REPORT.md) was tested with baseline A and J1-180 test B. JLC's selected model visibly turned, and B's appearance persisted after reopening. The eight solder tails, two pegs and opening could not all be verified, so the result is **inconclusive** and A was re-uploaded and visually restored. The diagnostic draft remains NOT FOR ORDER; the original drafts were not edited. Pod J1, carrier J101–J108 and carrier power J1 remain on placement HOLD. No purchase, reservation or manufacturing approval occurred.

## 2 November 2026 MacBook pod comparison handoff

Next action: run the [updated pod A/B handoff](quote-tests/r10-pod-j1-180/README.md)
on the MacBook. Create a fresh diagnostic pod draft from the unchanged files,
upload A (0°) then B (180°), and return actual views identifying all eight solder
tails, both locator pegs and the outward opening. Reopen to check persistence;
restore A if B fails or remains inconclusive. Leave the original drafts unchanged.

The two latest TinyFish runs both terminated without a new test draft, any CPL
upload or alignment images. The second reported a file-picker limitation; this
does not establish a JLC platform limitation. The [assessment and raw reports](quote-tests/r10-pod-j1-180/browser-assessment.json)
preserve those outcomes. No further identical browser retries are planned.

Pod J1, carrier J101–J108 and carrier power J1 remain on placement HOLD. This
handoff tests only pod J1 and does not approve a carrier-wide correction. Native
boards, the original r10 package and both test CPLs remain unchanged. No purchases,
reservations, vendor messages or manufacturing approvals. Earlier checkpoints
below are historical; this handoff is the current next action.

## Current next step is the pod J1 controlled CPL comparison

The user authorized a separate pod J1 180° test CPL and publication of the
[MacBook comparison instructions](quote-tests/r10-pod-j1-180/README.md). A is
byte-identical to the r10 pod CPL; B changes only J1 Rotation from0 to180deg.
All29 references, XY, sides and other rotations remain unchanged. Neither file
grants alignment or production acceptance. The original213-file r10 package and
native boards remain unchanged. No browser upload has been performed by this task.

The shared MacBook report at `c8b70522` confirms the toolbar90deg is an increment,
not saved-angle evidence, and contains actual screenshots. Use a separate
quote-only comparison draft, explicitly upload A then B, capture same-camera
pin/peg/mouth views and reopen to verify the observed state persists. This
replaces the previously blocking saved-angle-readout prerequisite for this
known-input trial only. Retain physical registration and manufacturing HOLD;
do not change original pod/carrier drafts, purchase or send vendor messages.

## MacBook handoff for connector rotation tests

The user authorized publishing the latest findings and a direct-browser handoff
to the existing shared branch `codex/crow-jlc-source-review-20261030`. Follow
[MacBook connector rotation handoff](MACBOOK-R10-CONNECTOR-ROTATION-HANDOFF.md):
capture actual saved placement data and inspectable pin/peg views, test pod J1
first, then carrier J101 and power J1, and retain only verified quote-only edits.
The 180° conversions are test candidates, not accepted JLC corrections. Native
boards, Gerbers, BOMs and the r10 CPL remain unchanged. No purchases, vendor
messages or production approval. The handoff supersedes older no-trial wording
only for these authorized reversible preview tests.

The published diagnostic evidence includes local catalog-fit renders, manufacturer
references and both unsuccessful browser reports with coordinator assessments.
These do not establish JLC alignment. `verify_evidence.py` checks retained bytes
and their native subjects without KiCad; `r10_upload_check.py` checks the unchanged
213-file quote package. Earlier local/unpushed notes describe those checkpoints.

## Current checkpoint — connector preview verification incomplete

The user requested a focused follow-up to obtain actual placement rows and
close-up pin/peg views before testing corrections. The [second TinyFish pass](https://agent.tinyfish.ai/runs/95ac5ef5-6f17-49e7-b681-5d3d39a50374)
ended after379seconds/30steps. It selected podJ1/C599441 but returned neither
actual saved XY/absolute-angle data nor inspectable close-up captures. No
rotation trial was initiated, and the conditional carrier test was not run.
See [raw report](r10-orientation-images/jlc-focused-browser-run.json) and
[assessment](r10-orientation-images/jlc-focused-assessment.json). This does not
prove JLC cannot expose/export data; it establishes failure of this automation
method to retrieve it. Do not repeat the same TinyFish approach. Next requires
a directly inspectable browser/data capture (the MacBook handoff route), or
authorized JLC production-pose verification. No corrections or approval; all213
local package files still verify unchanged. This update is local/unpushed.

The user authorized reversible, quote-only connector rotation tests in the
existing r10 JLC drafts, keeping the native boards unchanged. This supersedes
the earlier no-preview-rotations restriction only for those tests; it does not
authorize production approval, purchases, substitutions or vendor contact.

The bounded [TinyFish pass](https://agent.tinyfish.ai/runs/d75727db-b8b6-4f6b-9c0f-c049876ac4a3)
completed after573seconds/53steps. It reports no placement changes and performed
no before/after rotation test. Its narrative did not return inspectable pin/peg
captures or a placement export; conflicting angle/mouth claims cannot establish
alignment. In particular, the reported power-jack90deg is not established as an
absolute placement angle rather than a rotation-step control. PodJ1 angle was
not observed. Do not adopt these as corrected poses or infer approval from BOM
row counters. See the [raw result](r10-orientation-images/jlc-browser-run.json)
and [coordinator assessment](r10-orientation-images/jlc-browser-assessment.json).

Local catalog-model registration and opposing45deg renders are diagnostic;
they do not replay the actual JLC draft's CPL interpretation. All213 r10 payload
files remain unchanged and pass upload-integrity verification. Both drafts remain
on placement HOLD. Next: obtain an inspectable selected-reference absolute
placement row plus physical pin/peg/model evidence, or seek authorized JLC
production-pose verification if the viewer cannot expose it. No additional
unverified rotation loop. This checkpoint is local/unpushed.

## Retained authorization — quote-only 7628A selection and preview evidence

Following the assessment of MacBook commit278309e0, the user explicitly authorized
**quote-only selection of JLC04161H-7628A**, including the reported1.5542mm ±10%
warning, and pushing the assessment/checklist to the shared branch. It remains
unperformed by this backend. The allowed range to record is1.39878..1.70962mm;
no manufacturing tolerance waiver or production/placement approval follows.

[Current MacBook checklist](r10-registration-review/MACBOOK-CHECKLIST.md) directs
selection/persistence verification, unchanged5 fabricated/2 assembled carriers
and10 fabricated/8 assembled pods, and a bounded numbered-pin/peg evidence pass
on podJ1, carrierJ101 and carrier powerJ1 before any correction. Preserve all
136/29 factory references and20 HOME installations. [Assessment](r10-registration-review/REVIEW-AND-NEXT-STEPS.md)
and hash-bound native audit distinguish matching native/CPL geometry from the
still-unknown JLC model/production transform. Earlier requests for authorization
to select this exact stack for quotation are superseded only to that extent.

No new board/package revision, source CPL edit, vendor message, purchase, payment,
reservation, substitution, noncancelable sourcing or manufacturing commitment
is authorized by the stack selection. Quote-only preview rotation trials are
separately authorized above. The prior$390.97 excludes shipping/tax/HOME and must be refreshed
after confirmed stack selection. Other manufacturing/first-article holds remain.

## Publication handoff — r10 quote-only successor

User authorized publishing the verified r10 package and MacBook instructions
to existing shared branch `codex/crow-jlc-source-review-20261030`; no purchases.
[MacBook handoff](MACBOOK-R10-HANDOFF.md) specifies the new carrier fabrication
and CPL, unchanged pod, exact reviewed v2 grouped BOM equivalents, quantity
settings, numbered-pin/peg preview checks and retained process/stack holds.
The Python-only `r10_upload_check.py` verifies213 payload files,105 preserved
r9 files, review/native bindings and136/29 per-board factory reference identities
without needing KiCad; it explicitly does not rerun engineering acceptance.
Full native/Gerber replay and eight r10 tests pass on the server. Publication
includes reviewed source dependencies and final render sets, excluding unrelated
failed clock experiments and superseded render/authoring scratch directories.
No JLC draft, vendor message, sourcing commitment, reservation or purchase is
authorized by publishing or by an integrity PASS. Earlier "local/unpushed"
entries below describe the engineering-task checkpoint, not the publication.

## Completed — r10 outward power-jack quote derivative, 2026-11-02 UTC

Completed the bounded repair under vNext affected placement/routing/mating
review, with SOL6.1high author and independent reviewer. Final candidate4
SHA256`1fc774524ef57efdd3a644de338328837e42ba648d3a4dd6bb78bad44e8852a1`
places carrier J1 at(188,14.7),180deg: mouthY1.0 faces outward. Independent
review rejected candidate3's0.0369mm rear-body gap; coordinator explicitly
authorized a distinct-cause0.5mm outward robustness shift, now giving a
0.5369mm lower-bound gap under the retained manufacturer/installed-pose caps.
The named straight PP3 plug has>=0.90mm finished-board clearance; revised
finite corridor is carried into current instructions, not inherited from the
historically reversed mouth assumption.

Fresh strict DRC, opens, schematic parity, ERC and routing geometry pass.
Shared return paths and unchanged D3 output copper were checked; immediate
D3 input-side copper is geometrically identical and its continuous cooling
island increased206.408→216.184mm². This preserves the bounded prototype
thermal basis, not measured thermal performance. Author replay is byte-identical.
Only J1 placement, local VIN/FUSED routing and the explicit cooling extension
changed; schematic, other placements, vias, outline and pod are unchanged.

[Independent review](power-jack-r10-review/REVIEW.md) passes **prototype quote
derivative only**. [r10 package](quote-draft/r10-2c8p-outward-power/README.md)
build/verify passes213 files with105 r9 files preserved. Fresh carrier Gerber
and drill regeneration reproduces the packaged fabrication data (only timestamp
comments ignored). J1 CPL is bodycenter(188,-8.2),180deg; native geometry changed,
so new carrier Gerbers and CPL must be used together. BOMs and exact installed
split remain476 SMT/28 factoryTHT/20 HOME for5 fabricated/2 assembled carriers
and10 fabricated/8 assembled pods. All113 original r9 payload files still verify.
Eight package regression tests and nine render tests pass, including wrong-CPL
and changed-drill rejection even when a tampered file's manifest hash is restamped.

[Final renders](render-review-r10/REVIEW.md) include123 PNGs for both boards,
with outward registration/direction checks passing. Diagnostic solids are not
physical-fit acceptance. No formal vNext stage/release receipt was issued by
the quote helper. Historical full-release/production status remains HOLD.
Next is new-carrier JLC quote/registered placement review and reconciliation of
existing stackup, hole/assembly/process/retention and first-article thermal
controls. No browser draft, vendor message, purchase, reservation or manufacturing
commitment changed. Work is local and has not been committed or pushed.

### Repair checkpoint — shared-copper backtrack

Native J1 moved from (188,2.2),0deg to (188,15.2),180deg about its retained
body center. Maker mouth now faces -Y, nominal frontY1.5. The first concrete
repair passed strict native DRC/parity but the author then found its VIN path
reduced connected D3 FUSED cooling fill206.408→150.608mm². This invalidated the
initial routing candidate despite DRC0. A bounded causal repair reconnected a
left copper lobe and extended the same local cooling polygon; the first
extension193.388mm² was rejected, the second212.588mm² awaits independent
spreading/thermal judgment. Total copper area is not a guaranteed thermal model.
No circuit changes, new vias or unrelated placements were introduced. Earlier
SWIG/pointer implementation attempts are retained but are not separate accepted
designs. Candidate3 frozen SHA42a51e3b180ccfa1d0aeda85e9131c292ee8e1c32b6db3cb0c3261f22f134a01.

Both final diagnostic render sets pass registration/direction checks; carrier
has92 views, unchanged pod29, plus overview sheets. Independent review is
rederiving the real plug service corridor and tight rear-body gap; render solids
are not the clearance proof. No quote promotion until this review completes.

## Active bounded repair — outward carrier J1, 2026-11-01 23:49 UTC

User authorized native power-jack repair, affected routing/clearance checks,
regenerated renders and a verified quote successor; no purchases. Parent
deliverable is an independently reviewed r10 quote derivative, not a new full
release or silent promotion of historical stage receipts. Reopen J1 placement,
input-power/return routing, affected mating/assembly/fabrication evidence only.
The r9 diagnostic establishes a real native orientation conflict, so this is
first author attempt on the authorized physical correction, not another preview
or stock-search retry. Preserve r9 and all earlier renders.

Plan: SOL6.1high is sole native author under a new `power-jack-r10/` candidate
folder; coordinator owns integration/quote/renders and a separate reviewer
checks exact candidate evidence. Close condition: outward maker-supported pose,
unchanged circuit/other placement and outline unless explicitly justified,
complete affected supply/return duties, strict fresh refill/DRC/parity and geometry
checks, defensible connector/body/cable access clearance, source-bound review.
Author deadline00:03UTC; parent deadline00:15UTC Nov2 includes review/package.
Reassess after one unsuccessful attempt; at most two same-cause attempts within
that deadline. No new stage receipt is claimed through quote-only tools; the
existing quote workflow has no full current-adapter admission binding. Use its
actual native checks and independent affected-engineering review, keeping
production/release and vendor holds explicit. Next advancement requires actual
corrected native copper and verified access, not another report alone.

## Current update — r10 JLC quote and placement holds, 2026-11-01

The r10 carrier Gerbers, grouped BOM and r10 CPL were uploaded and processed.
JLC shows 23 selected carrier groups and the retained pod preview lists 20.
The displayed carrier/pod estimates total **$390.97** before shipping, tax and
home parts; they are not complete or production-ready. The required carrier
7628A stack triggered an unaccepted thickness warning, and connector model/pin
registration remains on hold. [Session report](JLC-R10-MACBOOK-SESSION-20261101.md)
records the draft links, hashes, charges and limits; [backend handoff](BACKEND-R10-JLC-BLOCKERS-HANDOFF-20261101.md)
requests source-bound stackup and connector diagnosis. No purchase, reservation
or manufacturing commitment.

## Current update — local multi-angle rendering finds power-jack direction conflict

Added generic `vnext/skills/render-board`: six cardinal and sixteen45-degree
orbit views, labeled connector close-ups, source hashes and explicit model
coverage. Skill validation and nine tests pass. Ran on both unchanged r9 boards;
[final galleries and review](render-review-20261101/REVIEW.md) contain123 PNGs.
Models are drawing-derived diagnostics; other components are unqualified native
footprint envelopes, not complete manufacturer CAD or clearance acceptance.

All9 RJ45 native orientations and Pico USB direction check outward. **Carrier
J1 PJ-102AH faces +Y/inward** from maker terminal geometry, inconsistent with
older outward negativeY cable-clearance assumptions. Current r9 CPL center and
THT table agree with the actual inward pose. Do not rotate only the model/CPL;
placement/mating must resolve the intended access direction and affected routing.
Both JLC placement holds and other production holds remain. All113 r9 payload
files still verify unchanged. No board correction, vendor change, purchase or
push was made by this diagnostic task.

## Current update — RJ45 native geometry checked; JLC placement hold retained

Reviewed remote input4eb497aa and [recorded the orientation diagnosis](R9-RJ45-ORIENTATION-REVIEW-20261101.md).
All9 RJHSE-5080 native pin/peg constellations and CPL body centers match the
manufacturer component-side drawing within0.004mm nominal rounding. A physical
180-degree reversal would misplace the locator-peg row by4.826mm. A JLC
zero-angle/model registration mismatch remains plausible, not proven.

Merged v2 BOMs preserve136 carrier/29 pod per-reference identities and routes;
r9 manifest verification passes. The new read-only TinyFish observation conflicts
with MacBook's inward-mouth finding and contains material factual inconsistencies;
it cannot close placement acceptance. Next: registered close-up evidence with
pin1/pin8/both pegs, or authorized JLC review if the preview hides those witnesses.
No CPL rotation, native/BOM/Gerber edits, browser changes, production approval,
vendor message, purchase or push. Both placement holds and carrier stackup hold
remain; USD391.09 remains the earlier incomplete delivered-quote figure.

## Current update — RJ45 connector orientation hold, 2026-11-01

JLC's angled 3D previews show pod J1 and all eight carrier J101–J108
connector mouths facing inward, contrary to the documented edge-facing
intent. Both drafts are on orientation hold; determine model convention,
pin/peg alignment and any corrected placement before approval. See
[follow-up report](JLC-R9-SELECTION-QUOTE-FOLLOWUP-20261101.md). No
rotations or production approvals were applied.

## Current update — r9 selection and draft quote follow-up, 2026-11-01

Both drafts reached PCBA quote screens after population-preserving BOM row
merging and per-reference checks. JLC initially hid a required row in each
first candidate despite its confirmed counter; the v2 candidates display all
expected groups in BOM and placement lists. Carrier $229.11 plus pod $161.98
= $391.09 before shipping, tax and HOME parts. Carrier stackup is still No
Requirement, and placement and assembly acceptance are not signed off.
[Follow-up report](JLC-R9-SELECTION-QUOTE-FOLLOWUP-20261101.md) records
itemization, draft links, caveats and candidate hashes. No purchases,
reservations, vendor messages or manufacturing commitments.

## Current update — r9 JLC selection blockers, 2026-11-01

The r9 carrier Gerber/BOM/CPL were uploaded to a new JLC quote-only draft;
the retained pod draft uses byte-identical r9 files. Both portals report
“Project has unselected parts” despite checked rows, and the carrier displays
38 confirmed for 29 detected. No part was intentionally omitted to bypass
the warnings. The earlier $161.98 pod price is not a verified complete quote;
carrier and pod full placement audits and itemized quotes remain open.
[MacBook session report](JLC-R9-MACBOOK-SESSION-20261101.md) records draft
URLs, selections and observations. [Backend handoff](BACKEND-R9-JLC-SELECTION-HANDOFF-20261101.md)
requests diagnosis and a validated population-preserving remedy. Stack, rail,
process and first-article holds remain. No purchases, reservations, vendor
messages or manufacturing commitments were made.

## Current update — r9 publication and MacBook handoff, 2026-11-01

User authorized pushing the validated r9 package to the existing shared branch
`codex/crow-jlc-source-review-20261030` for MacBook quote uploads; no purchases.
[MacBook handoff](MACBOOK-R9-HANDOFF-20261101.md) specifies an isolated checkout,
portable r9 verification, exact matched files/hashes, 5/2 carrier and 10/8 pod
quantities, home/factory split, preview checks and all remaining stop conditions.
This publication includes the r8 baseline required for r9 validation and retained
TI qualification history. No new part adoption, CAD change or release acceptance.
All eleven regression tests passed again. The reviewed draft7 is included;
earlier failed drafts remain local. Full staged whitespace checks report existing
formatting in preserved CAD/CSV/research bytes; scoped new handoff/r9 code checks
pass. Do not reformat hash-bound artifacts to suppress these diagnostics.
Actual publication commit and remote verification will be reported after push;
JLC drafts remain unchanged by repository publication.

## Current update — TinyFish login works; r9 transfer blocked, 2026-11-01

User authorized resuming the existing TinyFish session for r9 quotation only.
[Session report](JLC-R9-TINYFISH-20261101.md): both existing drafts loaded with
authenticated access. Carrier remains r7 with the CTS shortage and old C4;
no r9 file was uploaded. Local r9 verification passed, but the remote browser
cannot access the local package and its exposed tool has no file-transfer input.
Do not remove CTS from the old carrier draft as a substitute for uploading r9.

Pod confirmed counters are not stock acceptance: the run also reported an R5
inventory warning. No new placement preview or complete quote was obtained.
Next recommended step is authorized publication to the existing shared branch
and a MacBook upload of the matched r9 files, then TinyFish draft inspection.
Alternative is a supported TinyFish file-transfer path. No new board redesign
or stock-search loop is warranted. No draft edits, purchases, reservations,
vendor messages, manufacturing commitments or remote push were made.

## Current update — r9 home-installed TI clock, 2026-11-01

User explicitly chose home SMT installation of TI LMK6CE012288CDLFR X1.
Created [r9 quote package / home-work and browser instructions](quote-draft/r9-2c8p-home-clock/README.md).
Scope remains 5 fabricated / 2 assembled carriers and 10 fabricated / 8 assembled
pods. X1 is removed from carrier factory BOM/CPL and assigned HOME, not circuit
DNP. C4 remains factory installed, with 14 CL21B105KBFNNNE across the build.
New totals: **476 factory SMT + 28 factory THT + 20 home = 524 installed parts**.
Home scope is 2 Picos, 2 TI oscillators, 8 microphones and 8 buzzers.

`r9_quote.py build` passed: 113 payload files, 105 r8 payloads preserved byte for
byte. Both boards' native sources and fabrication files are unchanged; r8 itself
is preserved. Population checks account for every factory/home reference exactly
once. The retained r8 engineering review is not a new r9 assembly or release
acceptance. No independent r9 assembly acceptance or production approval claimed.
All five r9 regression tests and six retained r8 regression tests passed;
`r9_quote.py verify` and `git diff --check` passed. KiCad emitted property/image
handler diagnostics during the retained r8 tests; no test failed.

DigiKey browser observation for exact TI MPN: 2,884 in stock, MOQ1, USD3.34 each;
two installed USD6.68 before spares/shipping/tax. Purchase quantity and delivery
remain unconfirmed and no purchase is authorized. JLC oscillator warehouse date
is no longer required for this factory assembly split. All other factory stock,
placement preview, process, mechanical, stack and first-article holds remain.

Next: upload matched r9 quote files, confirm intentional X1 exclusion with C4
still included, inspect previews and obtain the complete itemized quote. Keep
"Do not confirm automatically". Confirm empty X1 pads are suitable for home
reflow. No browser changes, uploads, orders, reservations, vendor messages or
remote push were made in this step. This bounded assembly-split task advances
quote preparation without another component search or circuit backtrack.

## Current update — r8 TI quotation package passed, 2026-11-01

**TI LMK6CE012288CDLFR qualified for prototype quotation**, not production.
[r8 package and browser instructions](quote-draft/r8-2c8p-ti-clock/README.md)
are ready locally for 5 fabricated / 2 assembled carriers and 10 fabricated /
8 assembled pods. Replace the carrier's Gerbers, BOM and CPL as a matched set;
do not mix r7 carrier files with r8. Pod and home/THT files remain unchanged.

Independent review passed the exact changed native clock/power implementation;
a separate follow-up audit passed all 111 payload files, 38 procurement
identities and 524 installed parts. Need **2 TI oscillators** and **14 total
CL21B105KBFNNNE capacitors** after C4's change. All six regression tests pass,
including native/CPL/net checks, fabrication-file replay and tamper rejection.
`r8_quote.py verify` passes; r7 preservation also passes all 97 files.
Manifest SHA256: `ee01e3f63a993af9a6088c352bc260bf9451293311b2e2aeee4dde3ee35b25a5`.

JLC's ten TI units are overseas/presale, $4.9424 each; two installed cost
$9.8848 before allowances/fees/tax. **Usable warehouse date and exact gross
demand remain unconfirmed**. No allocation, immediate assembly or zero-day
lead claim. Current browser drafts were NOT changed. Next: deliberately upload
the matched r8 carrier set, verify exact matches and previews, obtain gross
demand/date/itemized quote, and retain all process/stack/mechanical holds.
No purchases, reservations, vendor messages, manufacturing commitments or push.

Engineering uses revised 192 mA / 350 mA / 680 mA prototype power allocations,
not inherited old limits. Narrow thermal/supply sensitivities and first-article
falsifiers remain explicit. No new workflow stage receipt or release approval
is issued by this quotation work. [Assessment](substitutions-20261101/LMK6C-QUALIFICATION-20261101.md)
and [independent package audit](substitutions-20261101/lmk6c-engineering/r8-audit.json).

## Current update — TI local implementation under review, 2026-11-01

User authorized qualifying TI LMK6CE012288CDLFR and changing the 2-carrier /
8-pod quote only if it passes; no purchases. Independent feasibility review
found no architecture contradiction. Created isolated native candidate
`substitutions-20261101/lmk6c-engineering/draft7/`: new DLF oscillator lands,
nearby1uF C4, local ground spreading and vias. **Not an upload package.**
Strict carrier DRC/refill/native schematic parity has zero findings, opens,
parity differences and ignored DRC checks; routing geometry has zero via/SMD
overlaps and zero .15mm annulus-gap findings. Same schematic as draft5, whose
ERC reports zero findings with four unchanged inherited disabled checks.
Expanded actual-layout clock model:26.35255pF load,1.621mV overshoot,
28.808ns minimum modeled high/low dwell. Models are not measured guarantees.

Power proposal explicitly reopens allocations:192mA external3V3,350mA5V,
680mAwhole-array12V, with source-voltage/ramp and D2/D3/LMK thermal review.
The old3.6V model is not silently transferred to the TI3.5V operating ceiling.
Independent exact-draft review is pending, bounded to18:25UTC. Feasible-path
decision completed within the earlier18:12 engineering-screen timebox; actual
new native implementation now exists. No new component search or board restart.
Generator/API failures and one repaired local via/track short are retained in
the [implementation packet](substitutions-20261101/lmk6c-engineering/IMPLEMENTATION-REVIEW.md).

JLC read-only browser still shows10 at$4.9424/unit, but raw evidence identifies
overseas stock; **usable warehouse date remains unconfirmed**. Reject browser
inferences of0-day lead time and5installed clocks. Need2installed; generic
attrition defaults are not exact-job gross demand. C4's existing1uF MPN would
rise from12to14 installed acrossbothboardtypes; fresh public pools retained.

All97r7files reverified unchanged. No r8, BOM/CPL/Gerber or JLC draft changes,
purchases, reservations, vendor messages, manufacturing commitments or push.
See [qualification assessment](substitutions-20261101/LMK6C-QUALIFICATION-20261101.md).

## Current update — stocked high-drive alternative found, 2026-11-01

Deeper user-requested search found TI LMK6CE012288CDLFR / C36974742 with
manufacturer-confirmed 30 pF drive below 50 MHz and a JLC offer for ten units,
MOQ one, browser price $4.9424 each. Raw exact-part JLC fields show **overseas
stock/presale**, not confirmed factory inventory. Two installed units required;
warehouse date, fees and attrition remain unconfirmed. jlcsearch has no exact
result; direct JLC identity and overseas fields are retained separately.

This is a promising **redesign candidate**, not an accepted substitute. New
2.5 x 2 mm footprint, power budget and bypass, 3.5 V supply ceiling/ramp and
clock waveform/timing/jitter checks must pass before any r8 package. Recommend
that bounded local qualification as the next engineering task; retain r7 intact.
See the latest section of [high-drive review](substitutions-20261101/HIGH-DRIVE-CLOCK-SEARCH-20261101.md)
and [raw lookup](substitutions-20261101/LMK6C-STOCK-20261101.json).
TXC AU and CTS commercial variants have zero/pre-order JLC offers; external
stock does not establish JLC readiness. No purchases, messages, reservations,
JLC draft changes, release changes or publication in this search.

## Current update — high-drive clock search, 2026-11-01

User authorized a stocked, adequately rated replacement and quote-package update
only if it qualifies. Completed public JLC browser search and manufacturer drive
screens: three stocked YXC leads have published 15 pF family drive ratings, not
enough for the retained 27.32305 pF model. No qualifying immediate-JLC-stock
replacement established. CTS CB3LV-3C-12M288000 is a same-footprint 30 pF
distributor-stock lead with a narrower temperature rating; TI
CDC6CE012288ADLYR is a 30 pF distributor-stock lead needing a new footprint,
routing and dynamic checks. Neither has a confirmed usable JLC assembly route.
See [high-drive review](substitutions-20261101/HIGH-DRIVE-CLOCK-SEARCH-20261101.md)
for exact identities, dated evidence, sourcing caveats and the bounded decision.

Recommendation: resolve the original CTS exact-part JLC eligibility/consignment
route before spending on a redesign that may retain the same sourcing delay.
Fallback: qualify the TI local redesign only after establishing a practical JLC
offer. The user's prior permission for the non-binding JLC inquiry is recorded;
the historical request for that permission below is superseded. No inquiry was
sent in this search. r7 preservation PASS (97 files), production_ready=false;
no r8, CAD/BOM/CPL/Gerber or JLC draft changes, purchases, reservations or
manufacturing commitments. Review and status are local, not pushed.

## Current update — Taitien oscillator qualification, 2026-11-01

User authorized qualifying OVETDLJANF-12.288MHZ / C5382655 and updating the
2-carrier/8-pod quote package only if it passes. Result: NOT QUALIFIED for the
retained direct-drive clock network. Fresh read-only native extraction confirms
r7 clock segments/pads/vias match the reviewed clock geometry. Retained load
sensitivity reaches 27.32305 pF versus candidate 15 pF drive capability; the
retained high receiver allocation alone is 16.80774 pF. These are engineering
model allocations, not measured capacitance or TI guaranteed maximum values.
Do not reduce them silently or transfer CTS waveform acceptance to Taitien.

Footprint changes are understood: 5.0 x 3.2 mm body, 1.50 x 1.20 mm lands on
2.54 x 2.20 mm centers instead of current 1.80 x 2.00 mm lands on 5.08 x 4.20
mm centers. New routing and generated fabrication outputs would be required,
but are not produced for a candidate that failed its electrical screen.
See the appended qualification in
[three-part handoff](substitutions-20261101/THREE-PARTS-HANDOFF-20261101.md).

All 97 r7 package files reverified PASS and remain unchanged; no r8, upload,
purchase, reservation, vendor message or manufacturing commitment. Recovery:
prefer preserving the reviewed drive capability through CTS sourcing or a
properly rated alternative; alternatively authorize a bounded buffered-clock
redesign for Taitien. The latter is not a BOM-only substitution. Existing factory
and release holds remain. Findings are local, not pushed.

## Current update — bounded r7 TinyFish follow-up, 2026-11-01

Read-only checks completed against the new drafts and exact CTS Global Sourcing
offers. TinyFish reports the DigiKey cut-tape offer for unchanged CTS
CB3LV-3I-12M288000 has 1,449 distributor units, MOQ 1, $2.1389/unit and
8–14 business days procurement-to-JLC-warehouse excluding 1–2 business days
review. However, it also reports a visible disabled-Add tooltip stating the
part does not support PCB assembly. This is NOT an actionable sourcing offer,
confirmed JLC inventory, or a complete quote. Two installed clocks are required;
purchase quantity including attrition and eligibility remain unresolved.

Pod audit reports all 21 groups selected with expected MPNs/codes. Manufacturer
and placement verification remain incomplete; this session could not access
the preview/quote previously reached on the MacBook. Do not discard the earlier
provisional $161.98 observation or infer a new confirmed price. Reject the
browser's quantity-mismatch classification: per-board BOM and batch/sourcing
quantities are different bases. See the appended review and UNSENT inquiry in
[session report](JLC-R7-MACBOOK-SESSION-20261101.md).

Fresh r7 package verification PASS, 97 files, production_ready=false. No package
changes, substitutions, purchases, reservations, vendor messages or approvals.
Stop repeated sourcing checks at this external eligibility dependency. Preferred
next action: obtain permission for one non-binding exact-job JLC inquiry covering
CTS eligibility and retained process controls. Alternative: request permission
to qualify a stocked clock substitute; do not adopt it or omit X1. Findings are
local until a subsequent explicit publication step.

## Current update — r7 JLC draft continuation, 2026-11-01

After explicit assembly-terms authorization, both new drafts were saved by JLC
and the r7 BOM/CPL uploads processed. Pod has a rendered preview and a
provisional $161.98 PCB + PCBA figure before shipping/tax; placement, identity
and process review remain open. Carrier is blocked at the unchanged CTS X1
clock (2 shortfall); do not proceed by selecting Do not place. Seven carrier
capacitor and two pod resistor grouped rows were selected using their specified
identities. Portal confirmed counters became inconsistent; do not infer coverage
from those counters. See [session report](JLC-R7-MACBOOK-SESSION-20261101.md)
for draft URLs, prices, evidence and open holds. No reservation or order.

## Current update — r7 MacBook forms, 2026-11-01

Two new unsaved JLC forms have the r7 Gerbers and requested 5/2 carrier and
10/8 pod quantities. The session stopped before NEXT because the assembly
service terms are preselected and the handoff prohibits approving disclaimers.
No BOM/CPL uploads, component matches, previews, complete quotes or durable
draft URLs exist yet. See [session report](JLC-R7-MACBOOK-SESSION-20261101.md)
for observed settings, preliminary board-only prices and remaining holds.
Earlier drafts were untouched; no purchases, reservations or production
commitments were made.

## Publication handoff — r7 new drafts, 2026-11-01

User authorized publishing r7 and instructions to the existing shared review
branch `codex/crow-jlc-source-review-20261030`, not main. Start with
[MacBook agent instructions](MACBOOK-R7-NEW-DRAFTS.txt). The next action is
creation of TWO NEW JLC quote-only drafts with exact r7 files, leaving earlier
drafts untouched. This publication carries the package, upload kit, bounded
qualification, sourcing observations, validation, generator/tests and history.
Earlier local-only notes are historical once this commit is verified remotely;
publication itself does not upload anything to JLC or approve production.
Publication check retains the exact hash-bound native payload, including blank-
line whitespace in inherited/generated KiCad files; staged whitespace checking
reports those lines. The check passes outside that native payload. This cosmetic
finding does not alter package identities, copper or validation receipts.

## Current update — fresh-draft request and upload kit, 2026-11-01

User now requests NEW JLC drafts from scratch, not modification of the saved
r6 drafts. No new JLC draft was created: TinyFish's confirmed file-transfer
limitation prevents uploading exact Gerbers/BOM/CPL. Do not reuse old component
selections or claim an empty draft contains r7. Existing drafts are untouched.

Prepared [upload-only kit](quote-draft/crow-r7-new-drafts-upload-only.zip): six
exact r7 Gerber/BOM/CPL files plus README, qualification, procurement and home
installation lists. This is a ten-file upload subset, not the full native/replay
package. Extract the outer ZIP; upload each board's inner Gerber ZIP and matching
BOM/CPL separately. CRC/byte checks passed against r7; full 97-file r7 replay
also passed. Kit SHA256:
`3e8f761dbb7a1d3b2c3af4c0781062a20c5f479789a209a28f21312fba106ae6`.

Factory coverage verified: 137 placements/carrier and 29/pod; full batch 478
SMT + 28 THT + 18 home, 38 procurement identities. Zero-population mechanical
scope rows remain, not extra installed components. Final fuse/regulator and
unchanged CTS identities are retained. Scope is still 5/2 carriers and 10/8 pods
(fabricated/assembled). A browser/file-transfer handoff is needed to create
the two new jobs, after which TinyFish can inspect the exact draft URLs. No
purchases, reservations, vendor messages, approvals or remote push.

## Current update — TinyFish access checked, 2026-11-01

User prefers TinyFish over MacBook operation. Signed-in TinyFish reached both
saved PCBA drafts. Read-only access run `98140db6-9e69-4263-87c6-984813a725cf`
mixed carrier/pod quantities and row counts; do not use its carrier quantity.
Single-carrier verification `9ea05ff7-fe85-46f9-b90c-77f77e98a51f` reported
PCBA quantity 2, CTS X1 shortage 2 and the old C18212367 regulator match still
deselected. It did not verify fabrication counts, dimensions or stack settings.
The first pass reported pod assembly quantity 8, but its duplicated BOM summary
is untrusted. Neither run supplied screenshot evidence.

TinyFish can navigate/inspect these drafts but explicitly reported that this
automation session lacks CSV/file-upload transfer tools (including from supplied
content or HTTPS URLs). A visible Upload BOM/CPL button does not establish tool
upload support. r7 is NOT uploaded; drafts unchanged. A manual upload of the
matching r7 BOM/CPL pairs from a browser with file access remains the narrow
handoff; MacBook specifically is not required. TinyFish can then inspect matches,
stock, placement availability and quote information within existing authority.
No purchases, reservations, vendor messages, acknowledgements or approvals.

## Current update — r7 qualified quote derivative, 2026-11-01

User authorized completing qualification and adopting passing parts into a
2-carrier/8-pod quote, with CTS unchanged and no purchases. LUTE 1206L010/30NR
and TRACO TSR 1-2450 passed engineering desk review for controlled prototype
quotation, with explicit factory-process and first-article gates. They are now
in [r7](quote-draft/r7-2c8p-stocked-power/README.md): 24 fuses and two regulators.
Fabrication remains five carriers/ten pods; assembly two/eight. CTS, home scope
and all four r6 substitutions are retained. The existing JLC drafts remain r6.

Both Gerber ZIPs, all copper/drills/mask/paste/silkscreen and connectivity remain
unchanged. U10 gets corrected non-fabricated body/courtyard graphics, a new
footprint ID and CPL body center (184.530,-36.250) mm; the old RECOM 3D model
is removed rather than reused. The pod CPL and all other carrier rows are unchanged.
Quote-owned native metadata, scope/procurement/THT tables are reconciled.

Validation: 35 quote regression tests pass (including seven r7 tests), fresh
KiCad ERC/DRC reports show zero violations and zero unconnected items under
retained ERC settings; netlists unchanged and source/PCB/BOM identities agree.
Deterministic replay passes 97 r7 files; all 94 r6 files still verify. See
[qualification](substitutions-20261101/r7-review.json) and
[validation receipt](substitutions-20261101/r7-validation/result.json).

No independent adversarial review, hardware tests or factory-process acceptance
is claimed. Exact stock allocation, CTS sourcing, previews, stackup/rails,
mechanical/stencil controls and complete price remain open. No account changes,
purchases, reservations, vendor messages or manufacturing commitments. Local
only: r7 has not been committed or pushed.

## Current update — LUTE/TRACO candidate qualification, 2026-11-01 Pacific

Read-only signed-in regular-catalog checks reported 33,897 available-to-order
LUTE C7542926 fuses and 167 TRACO C6886877 regulators, both ordinary in-stock
assembly-library items with no pre-order indicator. Installed need is 24 / 2.
These are not allocated stock or confirmed job dates. Retain CTS unchanged.
Bounded electrical/layout review recommends both for a subsequent quote
revision, with explicit process, footprint and prototype-validation conditions;
neither is fully accepted/adopted. See the
[candidate review](substitutions-20261101/THREE-PARTS-HANDOFF-20261101.md#lutetraco-stock-and-qualification--2026-11-01-pacific)
and normalized evidence. No BOM/CPL/CAD/draft changes, purchases, reservations,
vendor messages or manufacturing approval. Current continuation is local only.

## Current update — signed-in sourcing follow-up, 2026-11-01 Pacific

Secure sign-in worked. The direct Global Sourcing search still lists the exact
DigiKey fuse, CTS and RECOM offers with reported supplier quantities
45,522 / 1,449 / 32,691 and 8–14-business-day ranges; none establishes usable
JLC inventory. Clock/regulator unit-price arithmetic supports the old $4.28
and $9.69 illustrations; fuse quantity-specific pricing remains unverified.
Rejected the browser agent's inconsistent assembly-warning interpretation:
hidden tooltip text and zero attrition do not prove rejection or acceptance.
The existing Crow drafts were not reached; fees, eligibility, dates, previews,
full quote and mechanical/process holds remain open. See the
[signed-in follow-up](substitutions-20261101/THREE-PARTS-HANDOFF-20261101.md#signed-in-follow-up--2026-11-01-pacific).
No account/draft changes, purchases, reservations, substitutions or vendor
messages. Reports are local; not committed or pushed in this continuation.

## Current update — r6 quantity/policy reconciliation, 2026-11-01

Continued from `75447f43`; retained the r6 package unchanged. Public checks
do not establish enough usable stock for the exact fuse, CTS clock or RECOM.
Reconciled 24 installed fuses versus 28 last-displayed gross and 30 in the
historical price illustration; the extra two are not an approved requirement.
Recorded source-pool restrictions, conditional sourcing fees and the explicit
no-unpaid-order workaround: JLC says assembly order placement occupies stock.
See [reconciliation and read-only checklist](substitutions-20261101/THREE-PARTS-HANDOFF-20261101.md#backend-reconciliation--2026-11-01).
Current account quantities, charges, usable dates, exact assembly eligibility,
previews and full quote remain open. Secure browser sign-in setup was authorized
and offered; session save is pending. No purchases, reservations, vendor
messages, substitutions, draft changes or manufacturing commitments.

## Current update — three-part visual handoff, 2026-11-01 Pacific

Added [images, dated sourcing observations and a ready-to-paste backend
handoff](substitutions-20261101/THREE-PARTS-HANDOFF-20261101.md) for the fuse,
oscillator and RECOM regulator. The $35.69 illustrative subtotal is neither a
purchase quantity nor a complete quote. The quote, previews and factory
acceptance remain open; no vendor action or purchase was made for this report.

## Current update — r6 quote-only browser session, 2026-10-31 Pacific

At the user's request, processed both r6 BOM/CPL pairs with the four reviewed
replacement identities. JLC selected the replacement rows, but reprocessing
reset grouped selections and reselected the wrong-manufacturer regulator;
restored ten required grouped rows and deselected YLPTEC U10. Exact fuse,
oscillator and RECOM remain sourcing blockers. Illustrative Global Sourcing
lines total $35.69 before fees and with unconfirmed required quantities.
No complete placement preview or itemized PCBA quote; no purchases,
reservations, vendor messages or manufacturing commitments. See the
[session report](substitutions-20261101/JLC-MACBOOK-SESSION-20261031.md).

## Publication handoff — r6, 2026-11-01

User authorized publishing the r6 package/checklist to the existing
`codex/crow-jlc-source-review-20261030` branch, with no purchases. Start with
[MacBook instructions](substitutions-20261101/MACBOOK-START.md) and its portable
payload check. The reviewed 94-file r6 is unchanged; raw manufacturer downloads
and incidental KiCad preferences remain local. The public integrity check is not
full engineering replay; external replay dependencies are explicitly documented.
Earlier statements below describing uncommitted/local work are historical.

## Current update — r6 reviewed substitutions, 2026-11-01 UTC / 2026-10-31 PDT

User authorized replacements using find-substitute-part. Four identities are now
changed in the separate working native sources and complete quote derivative:
PCM1864DBTR/C544855 and Samsung CL21B105KBFNNNE/C28323,
CL21B225KBYVPNE/C5362585, CL31B106KBHNNNE/C89632. Independent SOL 6.1 high
reviews support the specific unchanged circuit roles and package integration.
Exact fuse, CTS clock and RECOM module are retained with adequate dated DigiKey
offers; use exact Global Sourcing candidates/approved consignment, not risky
electrical substitutions. Their factory allocation remains unresolved.

Scope stays 2 assembled carriers + 8 assembled pods on 5/10 fabricated boards;
factory 478 SMT + 28 THT, home 18. [r6 package](quote-draft/r6-2c8p-substitutions/README.md)
and [MacBook checklist](substitutions-20261101/HANDOFF.md) supersede r5 part
identities/routes only. Existing stack/rail/stencil/process and quote holds remain.
No saved vendor drafts were changed. Original release and r5 are preserved.

[Validation](substitutions-20261101/VALIDATION.md): local engineering/integration
reviews PASS; deterministic native/quote replay PASS; nine regression tests PASS;
zero reported ERC, zero DRC and unconnected items on both boards; connectivity,
Gerber and CPL preservation PASS. ERC uses unchanged inherited settings.
This is not a new sealed release or complete stock/allocation/production approval.
No purchases, reservations, vendor contacts, commit or push in this run.

## Current update — stackup follow-up, 2026-10-31

Selected and verified the specified pod JLC04161H-7628 in its saved quote.
The release's carrier design basis already states the 7628A layer sum is
1.5542 mm; JLC's displayed nominal is not a new discrepancy. Its explicit
±10% warning remains unaccepted and carrier stackup remains unspecified.
Actual-lot, factory and mechanical controls still need agreement. See
[the exact-match report](JLC-R5-EXACT-MATCH-20261031.md).

## Current update — carrier precision and stackup warning, 2026-10-31

Carrier ±0.1 mm precision outline became selectable and was chosen; the
incomplete carrier screen price is now $67.93. JLC warned that the specified
7628A stackup has nominal 1.5542 mm thickness ±10%, versus 1.6 mm. The warning
was not accepted; the carrier stackup remains unspecified pending mechanical
and factory review. Routing eligibility and all design-owned controls also
remain open. See [the exact-match report](JLC-R5-EXACT-MATCH-20261031.md).

## Current update — corrected quote finish and review settings, 2026-10-31

Changed both JLC drafts from leaded HASL to the planned ENIG; chose pod
precision outline. Carrier precision outline was disabled, leaving regular
±0.2 mm selected and an unresolved exact-job fabrication question. Requested
production-file and placement confirmation on both drafts and selected “Do
not confirm automatically” in each warning. Indicative incomplete board-screen
prices are $57.35 carrier and $42.24 pod, replacing earlier $37.40/$14.00.
Exact stackup, production data, sourcing and placement remain unconfirmed.
See [the exact-match report](JLC-R5-EXACT-MATCH-20261031.md); no order action.

## Current update — pod edge rails, 2026-10-31

The saved pod quote explains its 85 × 88 mm size: JLC proposes two 5 mm edge
rails on the 85 × 78 mm board, and the displayed depanel-before-delivery
option is No. Rail attachment, finished edges, geometry, handling and delivery
configuration remain subject to review against the released controls. See
[the exact-match report](JLC-R5-EXACT-MATCH-20261031.md); no setting changed.

## Current update — ADC land-pattern comparison, 2026-10-31

Released carrier U1/U2 each have 30 pads with the same corner numbering and
0.5 mm pitch as TI's example. Their pads are 1.475 × 0.300 mm at 5.725 mm
column spacing, versus TI's example 1.500 × 0.300 mm and 5.800 mm. This is a
documented comparison, not acceptance of the difference or of the JLC preview.
See [the exact-match report](JLC-R5-EXACT-MATCH-20261031.md). No release files
were modified.

## Current update — JLC sourcing and oscillator process, 2026-10-31

JLC's FAQ says library items labeled wave soldering are assembled manually;
the CTS oscillator's label therefore needs factory clarification against the
manufacturer's reflow specification. JLC's same-part stock guidance also
prohibits mixing public/pre-order with global/consigned inventory; the fuse's
seven public pieces cannot simply be added to a global quantity. Its matching
guidance says sourced private stock must arrive and be selected before use.
See [the exact-match report](JLC-R5-EXACT-MATCH-20261031.md). No inventory was
ordered or reserved, and no factory process was accepted.

## Current update — CTS and ADC manufacturer checks, 2026-10-31

The CTS CB3LV series datasheet documents reflow up to 260°C for 20 seconds,
which supports reflow for this oscillator despite JLC's wave-soldering label;
JLC's actual process remains unconfirmed. TI's PCM1864DBT package drawing is
nominally consistent with the r5 footprint dimensions and JLC's 175-mil label;
land pattern and orientation still require review. See the
[exact-match report](JLC-R5-EXACT-MATCH-20261031.md). No sourcing, preview or
factory-acceptance hold is closed by these checks.

## Current update — saved PCB quantities and incomplete pricing, 2026-10-31

The saved JLC drafts show 5 fabricated/2 assembled carriers and 10
fabricated/8 assembled pods. Preliminary screens display $37.40 and $14.00
respectively, with component and assembly charges still blank. Shipping is a
separate estimate, and combined freight and arrival dates remain unknown.
These figures are not complete PCBA quotes. See the
[exact-match report](JLC-R5-EXACT-MATCH-20261031.md) for details and blockers.

## Current update — smaller RECOM sourcing candidate, 2026-10-31

JLC Global Sourcing also displayed exact RECOM R-78E5.0-0.5 from DigiKey with
MOQ one: two at $9.69, 8–14 business days, tube. This is an unreserved
search-screen candidate, not a final quantity or full quote. Confirm JLC's
actual allowances, acceptance, fees and warehouse-ready date before use; see
[the exact-match report](JLC-R5-EXACT-MATCH-20261031.md). The ten-for-$48.05
Sager listing remains an alternative, not a minimum proven across all sources.
No purchase, reservation, substitution or manufacturing commitment.

## Current update — r5 home-part estimate, 2026-10-31

Public DigiKey listings show an indicative **$49.14** for the r5 home kit:
two SC0915 Picos, ten CMA-4544PF-W microphones and ten CPE-203 buzzers (two
spare of each acoustic part), before delivery, tax and potential tariffs.
See [the r5 home cost](R5-HOME-PARTS-COST-20261031.md). This replaces the
home-THT-scope $68.07 benchmark for the current kit; it is not a quote or
part of JLC's unfinished PCBA price. No purchases or reservations made.

## Current update — shortage identity review, 2026-10-31

The carrier draft's Part Info identifies its unstocked ADC candidate C2863172
as TI PCM1864DBT and oscillator candidate C17275161 as CTS Electronic
Components CB3LV-3I-12M288000. The TI-linked PCM1865-named datasheet covers
PCM1864 too. These are manufacturer/MPN checks only; package reconciliation,
CTS handling, supply and factory approval remain open. See the updated
[exact-match report](JLC-R5-EXACT-MATCH-20261031.md). The support inquiry remains
unsent; no purchase, reservation, substitution or manufacturing commitment.

## Current update — exact match review, 2026-10-31

The JLC r5 carrier auto-match for RECOM U10 is a YLPTEC part, C18212367,
and was deselected. Exact RECOM C5199916 showed zero available stock; an exact
RECOM Sager Global Sourcing offer remains an unreserved estimate. Eight exact
carrier capacitor rows and two exact pod resistor rows previously unchecked
were selected; portal summary counters are internally inconsistent. Manufacturer
identity evidence supports Amphenol RJHSE-5080 and the CUI/Same Sky PJ-102AH
rebrand; final geometry/process and supplier acceptance remain open. See
[exact-match observations and unsent inquiry](JLC-R5-EXACT-MATCH-20261031.md).
Seven exact sourcing identities, full previews and a complete non-binding quote
remain open. No purchase, reservation, substitution or manufacturing commitment.

## Current update — r5 JLC browser session, 2026-10-31

The carrier and pod r5 BOM/CPL pairs were processed in existing JLC drafts for
two Economic carrier assemblies and eight Standard pod assemblies. JLC showed
30 carrier rows (25 confirmed, five short) and 21 pod rows (18 confirmed, three
short). These are BOM-row counts, not acceptance of all 506 placements. The
pod's NEXT warning offered to leave unselected parts unplaced; **Select parts**
was chosen. Carrier placement did not advance from BOM matching. No complete
preview, PCBA quotation, sourcing fees, combined freight or delivery date was
obtained. Exact RECOM variant, sourcing and all process holds remain open.
See [the MacBook session report](JLC-R5-MACBOOK-20261031.md) and
[backend handoff](BACKEND-HANDOFF-R5-QUOTE-20261031.md). No purchases,
reservations, substitutions, vendor contact or manufacturing commitments.

## Quote-package publication checkpoint — OR22, 2026-10-31

User requests pushing complete r5 and MacBook instructions to the existing
`codex/crow-jlc-source-review-20261030` branch; no purchases. Publication scope:
r5 plus its required r4 inputs, both generators/tests, drawing-derived review,
current handoff/ownership banners and OR20–OR22 records. Unrelated local stock
CLI/research changes are not part of this publication. Earlier records marked
local/unpushed remain preparation history; the current remote commit and
post-push verification are reported in the handoff response.

Use [current MacBook instructions](MACBOOK-2C8P-QUOTE-HANDOFF-20261031.md).
The package is for two assembled carriers and eight assembled pods, with full
JLC SMT/THT scope and only Picos/microphones/buzzers at home. Source manifests,
coverage and release-preservation checks must pass on the exact publication
snapshot, not just the dirty working tree. No board/release bytes changed.
Exact staged-tree replay PASS: quote validation, 256-file release preservation
and **59 published order-readiness tests**. Five additional local public-stock
tests are intentionally outside this commit (OR21's 64 includes those).
Initial temporary export omitted the already-tracked `vnext/tools` test
dependency; exporting it from the same staged tree resolved both import errors.
No repository code repair was needed. Staged whitespace check PASS.
No JLC uploads, purchases, reservations or manufacturing approvals authorized
by Git publication. Exact matching/stock, final placement preview, process
agreement and a complete quote remain pending.

## Complete quote-upload files — OR21, 2026-10-31

User authorizes finishing THT placement verification and complete BOM/CPL files
for **2 carriers / 8 pods**, no purchases. Prepared
[r5 package and MacBook steps](quote-draft/r5-2c8p-complete/README.md).
137 carrier and 29 pod references have complete per-board BOM/CPL coverage:
478 SMT + 28 THT = 506 JLC installations; 18 home parts. r4 remains unchanged
as the incomplete historical candidate. Gerbers, BOMs and every SMT CPL byte
remain identical to r1/released sources. No board/release edits.

Three manufacturer drawings visually reviewed; all 11 unique THT pin/peg
constellations, top-side zero-angle physical poses and power-pin functions
checked against read-only native KiCad sources. CPL uses nominal body centers,
not pad-1 anchors. RECOM center incorporates the drawing's 3.21-mm edge-to-pin
dimension, 0.10 mm different from the F.Fab-box center; copper stays unchanged.
Source revisions/hashes, formulas and physical orientation instructions retained.
This is local coordinator verification, not independent adversarial review or
new vNext assembly acceptance. The sealed historical acceptance is inherited.

Milestone progress: missing THT coordinates are resolved; complete quote files
now exist. Separate **quote_upload_ready=true** from **production_ready=false**:
JLC library zero/center and final preview must be reviewed after matching, not
invented before upload. Previous r4 pre-upload gap is closed locally without
waiving that vendor hold. vNext assembly-verify/resume contracts guided the
source preservation, coverage checks and explicit ordering boundary; no new
domain receipt, autonomous execution or supplier agreement is claimed.

Verification: **64 order-readiness tests PASS** (11 new completeness, physical
pose, missing/duplicate/home-reference and tamper regressions). Fresh KiCad
10.0.4 native audit and portable hash-bound replay PASS; 25 inherited SMT angle
offsets preserved. KiCad property/image-handler warnings retained; exit 0.
Publication preservation PASS for all 256 release files; engineering acceptance
not reassessed and order gate still DO-NOT-ORDER. `git diff --check` PASS.

Next: publish this local revision when requested, then authorized MacBook
quote upload/matching and full placement-preview check using r5. Confirm all
THT operations, exact source eligibility/gross demand, fees and dates; no
repeated public stock sweep needed. If pricing requires buying shortage parts,
report the boundary rather than omit them. No uploads, supplier contact,
purchases, reservations or commitments; this work remains local/unpushed.

## Current assembly ownership — OR20, 2026-10-31

User selects JLC Ethernet/power-jack/RECOM installation for **2 carriers/8 pods**;
only Pico/microphone/buzzer remain home work. Prepared [r4 mixed-assembly draft](quote-draft/r4-2c8p-jlc-tht/README.md):
478 SMT + 28 THT = 506 JLC placements; home 18; total 524. THT is 24 RJHSE-5080,
two PJ-102AH and two R-78E5.0-0.5. Home is two SC0915, eight CMA-4544PF-W and eight
CPE-203. RECOM returns to JLC sourcing. Supersedes r3 and older 2c8p home-THT/
SMT-only-spare instructions, not historical evidence or sealed release bytes.

vNext assembly-verify/resume/part-recheck guidance applied. Full BOMs cover
137 refs/carrier and 29/pod; SMT CPL and Gerber bytes unchanged. Native THT
pad-1 origins are not verified vendor centroids; preserve the inherited gap.
SMT-only CPLs marked INCOMPLETE; THT worksheets NOT-UPLOAD; manifest readiness
false. Strict upload gate must fail until complete CPL mapping/review.

Next bounded task: resolve three part-type mappings across 11 per-board THT
positions, preserve SMT rows, then verify 137/29 CPL coverage and vendor preview.
Fallback is a separately accepted quote/review for all 28 manual installations,
not silent omission/home transfer. Stock/gross demand, fees/dates, exact process
acceptance and purchase authority remain open. No repetitive stock sweep needed.
Local/unpushed; no browser changes, uploads, contact, purchases or commitments.

OR20 verification: 53 order-readiness tests PASS, including eight new split/
coverage/tamper/readiness checks; all 256 release files preserved. Read-only
KiCad 10.0.4 native audit PASS, retaining 25 SMT angle offsets; 11 THT geometry
records match native board hashes. KiCad emitted property/image-handler warnings
but exited successfully. Strict upload-readiness check correctly returned exit 2.

## Current publication — OR16, 2026-10-31

User authorizes publishing OR15's reconciliation, CSV, MacBook checklist and
regression checks on the existing `codex/crow-jlc-source-review-20261030`
branch. This supersedes OR15's local-only publication status, not its technical
holds. Publish only these preparation artifacts and this journal; leave main,
release payloads and existing quote packets unchanged. Verify remote commit
and file identities after pushing. Next: the checklist's bounded signed-in
quote pass for 2 carriers/8 pods, not purchases or manufacturing commitments.
No JLC/browser/vendor actions are part of this publication.

## Current preparation — OR15, 2026-10-31, 2+8 reconciliation

User authorizes quantity/fee/assembly reconciliation and next MacBook steps,
not purchases. Reopened remote `0b44f57d` in the clean review worktree. One
bounded preparation pass under vNext resume/recover, part-recheck and assembly
verification guidance; no new engineering acceptance or autonomous adapter.
Prior browser attempts/history remain charged; this is not a fresh stock-search
loop. New evidence to resolve: exact package/process facts and source-pool/fee
effects on the already observed two-job quantities. Stop after this handoff,
not another public catalog sweep. Preparation/validation deadline 17:35 UTC;
coordinator is sole writer, order-readiness files only.

See [reconciliation](JLC-2C8P-RECONCILIATION-20261031.md), its six-row CSV and
[MacBook instructions](MACBOOK-2C8P-QUOTE-HANDOFF-20261031.md). Current quote
scope is 2 SMT carriers/8 SMT pods on 5/10 bare, 478 factory placements; home
kit completes one array (35 installed parts), second carrier SMT-only spare.
Installed shortage demand 54; observed gross 88; historical global offers 96
pieces/$87.58, not final buy quantities. Seven public fuses receive zero credit
against the global candidate; regular 21-piece shortfall remains conditional.
Potential $40 global fuse inspection/certification requires exact-job application.
TI confirms DBT tube packaging; public TI availability conflicts with the
account offer, so one exact account recheck/DigiKey-global fallback is specified.
CTS maker/FAQ clarify SMD vs manual label, not factory acceptance.

Milestone assessment: scope arithmetic and public package facts reconciled;
complete quote, allocation, fees, usable arrival and factory process acceptance
remain open. No production hold is promoted by these documents. Next owner is
the signed-in MacBook session for one 30-minute targeted pass; if account facts
need vendor contact or committing pre-order submission, stop with the unsent
inquiry and request authority. Preserve the noncancelability warning; do not
omit short components to obtain a false total. No browser/cart/vendor actions,
purchase, substitution, release mutation or main merge in this preparation.

OR15 validation checkpoint: 40 order-readiness tests (including five new
quantity/pool/price/unknown-field regressions) and 15 publication tests PASS.
R1 and r3 verification PASS; their historical scenario totals are not the new
2+8 scope. All 256 release payloads preserved; `git diff --check` PASS.
Deliverables are local and not pushed. No independent engineering/vendor
acceptance is claimed. End this bounded preparation pass; continuation needs
the targeted account results, not another identical server-side review.

## Current update — 2026-10-31, sourcing report and backend handoff

The signed-in JLC Global Sourcing screens showed exact-part indicative lines
for all six shortages, totaling $87.58 at illustrative quantities, before
fees. This is not a complete quote or confirmed purchase quantity. See the
[sourcing report](JLC-ITEMIZED-SOURCING-20261031.md) and
[backend handoff](BACKEND-HANDOFF-JLC-SOURCING-20261031.md). Assembly pricing,
fees, usable-stock dates and combined shipping remain unconfirmed; JLC warns
that completed pre-order quotations cannot be canceled. No purchase,
reservation, substitution, vendor message or manufacturing commitment made.

## Current update — 2026-10-31, cost proposal

The user accepts two assembled carriers and asks for a quote-only exact-parts
proposal. [The 2+8 cost proposal](JLC-2C8P-COST-PROPOSAL-20261031.md) records
the six SMT sourcing lines and a separately priced home-install kit. The full
JLC PCBA amount, allocation and production acceptance remain unknown. No
substitutions, purchases, reservations or manufacturing commitments authorized.

## Current update — 2026-10-31, two-carrier quote check

JLC's existing Economic form offered two assembled carriers on five bare
boards; the draft was left at two, with eight assembled pods on ten bare.
Six exact SMT identities remain short across the two jobs; no complete PCBA
price or approved process exists. See [the dated observation](JLC-HOME-QUOTE-OBSERVATIONS-20261031.md)
for per-job quantities, the shared-fuse caution, exact listing snapshots and
ranked paths. The five-carrier case remains a comparison, not an adopted build.
No purchases, reservations, substitutions or manufacturing are authorized.

## Current publication — OR14, 2026-10-31

User authorizes pushing the revised 1+8 plan and r3 submission draft to the
existing remote branch for MacBook quantity/sourcing checks, explicitly no
purchases. R3 README now has the current bounded Mac prompt: smallest supported
carrier assembly lot, eight assembled pods, separate five-carrier comparison,
six exact shortages and home installation. No new vendor action in this turn.
Keep main and original release unchanged; verify remote commit after push.

## Current preparation — OR13, 2026-10-31

User now requests revised procurement for target 1 carrier/8 pods, separate
5-carrier scenario, home-install list and a JLC submission preparation. No
purchases. Prepare r3 SMT-only vendor draft outside the immutable release;
do not submit it or represent unresolved stock/preview/process as production
approval. The 5-carrier case is observed portal configuration, not a proven
minimum (JLC public minimum is two assembled boards). Quote both scenarios
without adopting extra builds. Home installation applies to all six manual
identities; RECOM is no longer a JLC Global Sourcing requirement.

Prepared locally: `quote-draft/r3-1c8p-home/README.md` is the revised plan,
`JLC-SUBMISSION-NOTES.md` the unsent vendor brief. Six per-board vendor data
files preserve r1 SMT-only BOMs/CPLs/Gerbers exactly; machine-readable demand,
shortage/home lists, scenario quantities and source hashes accompany them.
`home_assembly_plan.py verify` passes, with 50 tests and 256 release payloads
preserved. Target 1+8 = 351 JLC SMT + 35 home; comparison 5+8 = 859 SMT + 79
home if all five are completed. Four extra carriers may remain SMT-only spares,
in which case home purchases still cover one array. No new total price or
production approval established. Next is one scenario/quantity and exact supply/
job review, not a stock-search repeat. OR13 prepared locally; publication is now
authorized under OR14. No vendor submission or purchase is authorized here.

## Current update — 2026-10-31

The active target is one assembled carrier and eight pods; investigating extra
boards for minimum quantities is acceptable. The user chose home installation
of the 18 through-hole parts for the JLC route. JLC SMT-only drafts have five
carrier and eight pod assemblies, but exact-part shortages block a complete
quote. PCBWay has two submitted quote-only inquiries under audit using the
earlier factory-installed through-hole scope. Neither is a complete price or
manufacturing approval. See [the current session report](PCBA-SESSION-20261031.md)
and [backend handoff draft](BACKEND-HANDOFF-PCBA-20261031.md). Earlier
authorization and current-action statements below are historical where they
conflict with that report. No substitutions, purchases, payments, reservations
or manufacturing commitments are authorized.

Goal authorized 2026-10-26: prepare **5 carriers / 10 pods** for ordering, not
five complete arrays. State: OR10 consolidated procurement proposal prepared; exact-job process,
allocation and quote approval remain open. Not order-approved. Authority: user's
“great lets set that as a goal! and lets go!” after the stated next milestone.
No purchase, vendor submission/contact or design change is authorized.

Baseline: main `5ddd8d796bdbaeb51476c8835986f681f24b67c1`, public package
`crow-prototype-v3-first-run-5c10p-public-v1`; original source/seal remain frozen.
The package's nine holds remain OPEN. Do not edit historical status or claim a
new receipt. Publication authorization already covers the separate public subset,
not vendor submissions or spending.

## Current action

OR12: `quote-draft/r1-20261031/` contains source-bound quote-only full/SMT BOMs,
byte-preserved CPL/Gerber files, manual/user schedules, complete scope and hash
manifest. Native KiCad audit covers 142 carrier and 35 pod footprints, including
all exclusions/identities/poses. Original mapped vendor angles are preserved;
not requalified against JLC previews. Global part public codes are intentionally
not advertised as usable private inventory in BOMs. `quote_files.py verify`
checks deterministic source/output binding; no new engineering receipt or order
acceptance. Current user authorizes publishing this packet, not uploading to JLC.
Next: use the packet README and quote handoff's manifest/permission boundary;
then collect an integrated quote, including all 60 manual operations. No stock
research repeat or design regeneration. No purchases, payments or substitutions.

OR11 publication/handoff, 2026-10-31 PDT: user authorizes pushing OR10's
proposal and preparing Mac steps for a complete 5-carrier/10-pod JLC quote,
explicitly no purchases. `MACBOOK-QUOTE-HANDOFF.md` supersedes both completed
browser passes. Next: locally validated quote-only BOM/CPL/manual schedule,
then one scoped non-binding quote session after presenting its upload/action
manifest for approval. No ready-to-upload packet or full quote is claimed.
Preserve original release and source observations; no vendor action in this turn.

OR10: verified and fast-forwarded remote b39eb5a4, containing exactly OR9's
pricing report, JSON and journal update. `PROCUREMENT-PROPOSAL-20261030.md`
and its 38-row CSV now consolidate the complete 5/10 installation/supply split.
Preferred: 28 catalog identities, five regular replenishment lines and exact
Global Sourcing for RECOM plus ADC; three identities remain user-installed.
Seven-line component benchmark $227.71 is not a whole-batch quote. Final job
quantities/fees/usable-stock dates and vendor process/placement acceptance are
unconfirmed. No holds are closed, orders authorized or independent acceptance
claimed. Proposal publication is now authorized on
`codex/crow-jlc-source-review-20261030` alongside earlier evidence, not main.

The bounded Mac pricing pass is complete; do not rerun it or the 35-part pass.
Next artifact is reviewed vendor drafts and one integrated exact-job quote/
process review for both boards. Factory BOMs are still empty; no uploads or cart,
submission, vendor-contact or payment authority is inferred. Preserve the
release and obtain scoped authority at any required external-action boundary.

Historical OR8 (route superseded by OR9/OR10): `SOURCING-COMPARISON-20261030.md` and its CSV compare seven exact external
offers against JLC catalog minima/prices and procurement policies. External
component benchmark is $138.96 + EUR4.88; six JLC catalog lines total $93.54,
excluding ADC, attrition and all logistics/process extras. These are not quotes.
Preferred next approach is JLC-managed replenishment plus Global Sourcing of
exact PCM1864DBT, conditional on account offer/date; external consignment is the
fallback. Perform one bounded account offer comparison, not another broad stock
search. Applicable consignment fees and actual receipt dates remain unquoted.
JLC FAQ clarifies the Wave Soldering label means manual assembly, not proof of
literal wave exposure; retain a compatible CTS SMD process check, not redesign.
No hold is closed and no purchase/submission is authorized by this comparison.

OR7 review: `SOURCING-DRAFT-20261030.md` records source-supported Panasonic
spelling and CUI/Same Sky history reconciliations for the draft only. Original
OR6 classifications remain immutable. CTS is a manufacturer-specified SMD
reflow part; JLC's label needs compatible matching/process verification, not a board
redesign. TI confirms DBT is TSSOP-30 and offers DBTR as a packaging variant;
no variant is adopted. Next recommendation is one seven-line exact external
sourcing/consignment comparison against JLC replenishment, not another full
browser pass. Browser commit be16560f is present on the local review branch
`codex/crow-jlc-source-review-20261030`; this review is not merged/pushed to main.
No ordering hold is claimed closed. Mac checkout damage and TMPDIR test handling
are documented separately from design correctness.

OR6 MacBook browser pass complete, 2026-10-30 PDT:
`JLC-BROWSER-20261030.md` and `.json` contain one complete 35-identity pass.
26 exact identities show sufficient available-to-order stock; seven show
insufficient/zero stock; two stocked candidates need identity reconciliation.
Four missing catalog leads are recovered (Panasonic spelling still pending).
No failed lookup is being treated as zero stock. No stock pools are added.
Next recommended route is a reviewed exact-part JLC matching/sourcing draft,
with exact external consignment as fallback; no upload/contact/order authority
is inferred. Exact process, allocation, lead times and quote remain open.
The handoff and v3 worksheet retain their source instructions and identities.

OR5 mapping checkpoint complete: `ASSEMBLY-MAPPING-20261026.md` and current
`procurement-map-20261026-v3.csv`. Thirty-eight exact identities and all 1,000
installed parts accounted for; 32 SMT identities split into 11 JLC-positive,
14 LCSC-positive/JLC-eligibility-pending and seven external-source candidates.
These are draft route classifications, not a vendor-ready BOM or allocation.
User selected JLC installation of 60 connectors/regulators and user installation
of 20 acoustic parts, in addition to the five Picos. V3 records ownership only;
inventory observations retain their original dates. JLC acceptance is pending.

Prior user decision, 2026-10-26, after reviewing Pico photos, relief geometry
and stated tolerances: “Yes it will be fine, lets move on.” Treat this as user
acceptance of the discussed prototype Pico-fit risk and direction to stop further
Pico-relief investigation. Do not reopen that research without new contrary
evidence. This is not a measured fit result, supplier guarantee, blanket waiver
for other connectors or purchase authority. Preserve the sealed engineering
record; any later order disposition must explicitly carry this user decision
instead of representing the old mechanical hold as verified closed.

Next work is assembly-package preparation, not more Pico-tolerance research.
Read-only population audit confirms the following installed batch allocation:

| Operation | Carrier batch | Pod batch | Current owner/route |
|---|---:|---:|---|
| SMT population | 635 | 280 | Proposed JLC; exact catalog/consignment mapping pending |
| Pico U3 installation | 5 | 0 | User |
| RJ connectors | 40 | 10 | JLC manual requested; acceptance pending |
| DC jack J1 | 5 | 0 | JLC manual requested; acceptance pending |
| RECOM U10 | 5 | 0 | JLC manual requested; acceptance pending |
| Microphone MIC1 / buzzer BZ1 | 0 | 20 | User; protected hand soldering after JLC processing |

Source: sealed `fab/assembly/population.csv`. Total 1,000 installed components;
915 proposed SMT and 85 manual: 60 requested from JLC and 25 user-installed.
Both factory BOMs still contain zero lines; existing consigned BOMs contain 27
carrier and 20 pod grouped lines (not unique system MPN counts). The next concrete
deliverable is confirmation of exact JLC sourcing/process and pricing, keeping
manual parts out of machine-placement files and preserving reviewed geometry.
The draft mapping is not a ready-to-upload factory BOM. User-installed parts
remain outside JLC placement/paste scope, with their holes open for completion.
Procure those parts separately; no loose JLC shipment is assumed. If JLC declines
any of the 60 operations, obtain a new decision rather than assigning them to user.

Earlier user decision, 2026-10-26 (expanded by current split above): user can perform Pico assembly. Assign the five Pico
installation operations to the user; do not infer ownership of the other manual
parts. Existing D1-only preparation and inspection instructions still apply;
performed work and physical qualification are not claimed. User requests an
online review of JLC support for exact fabrication/placement/assembly limits.
OR4 comparison is complete in `JLC-CAPABILITY-REVIEW-20261026.md`: ordinary
partial assembly is supported; selected design-owned geometry/process limits
are not established by the published capabilities. Recommended next action is
a targeted engineering review of those constraints, with explicit affected
evidence reacceptance if changed. This review has not been performed or adopted.

OR3 produced positive exact-part availability evidence for all eight prior
exceptions: seven direct supplier fetches today and one four-day-cached DigiKey
observation. See `SOURCING-RECOVERY-20261026.md`. No substitution is indicated by
these findings. The other 30 observations retain their OR2 freshness limitations.
The next discriminating evidence is exact-job fabrication/assembly compatibility,
usable stock/consignment allocation and itemized pricing, not another broad stock
search. Supplier contact/submission and spending remain unauthorized. The goal
service still reports BLOCKED; this successful user-directed recovery does not
constitute full goal completion or reopen it through an unsupported status call.

## Execution binding

Use vNext orchestrator dispatch/recover and PCB sourcing, fabrication, assembly
and release order-boundary contracts. No implemented local order-admission node
exists in graph.json. This continuation therefore uses explicit coordinator
checks and independent review, not a fabricated automated stage receipt.
Do not invoke legacy order conductors or recreate board design acceptance.
The journal below is the single attempt/progress record; STATUS is its live view.

Historical recommendation after OR4 (Pico research now superseded by the user
decision above): review designer-owned precision/pose/seating
and paste restrictions against normal JLC manufacturing variation. Alternative:
retain all controls and seek explicit exact-job agreement. Candidate assembly
route was JLC fabrication/SMT plus user Pico installation; current ownership is
now the 60/20 split above, still pending exact-job JLC acceptance. Neither a revised
process nor an engineering waiver is adopted; no blind all-consigned order.

Scope/cost: components and bare fabrication/setup subtotal, separately itemized
assembly/manual work, fees, shipping and tax. Enclosures/roof hardware excluded.
No spending limit or quote approval inferred from earlier per-array estimates.

## Journal

- OR14 pre-push validation, 2026-10-31 PDT: r3 deterministic verification
  PASS; all 35 order-readiness and 15 publication tests PASS; all 256 release
  payloads preserved. No native design, prior quote revision or supplier
  observation modified. Push contains the prepared plan/data/tools/tests and
  handoff/journal only. Production and purchasing holds remain open.

- OR14 publication dispatch, 2026-10-31 PDT: publish existing OR13 plan,
  scenario generator/tests and r3 packet plus refreshed Mac instructions.
  Source baseline 1caaa35d; preserve unchanged released payloads and r1/r2.
  Validate scenario/source binding, all tests and whitespace, stage only named
  order-readiness paths, normal push to existing branch, verify remote SHA.
  This is publication/handoff, not sourcing acceptance or a vendor submission.

- OR13 checkpoint, 2026-10-31 PDT: r3 data build/verification passes; 38 exact
  identities partitioned into 32 JLC SMT and six home identities, all 177 native
  refs accounted for. Six shortage demands: A CTS1/fuse16/Murata10/TDK0805-8/
  TDK1206-2/ADC2; B CTS5/fuse48/Murata18/TDK0805-8/TDK1206-10/ADC10. No portal
  attrition or shared stock silently credited; prices/purchase quantities unknown.
  Home counts A 16RJ+1PJ+1RECOM+1Pico+8MIC+8BZ; B 48+5+5+5+8+8. Exact source
  SMT/ZIP bytes and per-board counts unchanged. Seven prior quote checks plus
  six new scenario regressions pass within 35 order-readiness + 15 publication
  tests; original 256 payload preservation PASS. Read-only public JLC guidance
  confirms minimum two, not five; actual supported job/exception remains open.
  Milestone: reviewable revised packet prepared, not actual order admission.
  Next discriminating step is supported quantity, exact usable sourcing/fees,
  vendor previews/process and complete cost before purchase approval. No vendor
  submission/contact, portal mutation, purchase, reservation, push or design change.

- OR13 dispatch, 2026-10-31 09:27 PDT: user authorizes local revised plan and
  submission preparation, not purchase or vendor action. Clean checkout was
  fast-forwarded to 1caaa35d; session report treated as retained observation,
  not fresh browser access. Coordinator prepares exact per-board SMT files,
  scenario demand, home list, supplier notes and checks. Stop by 09:50 PDT
  including validation with draft and named production blockers. Preserve
  OR6–OR12 sources and old packet manifests; no regeneration/redesign or repeat
  35-part research. Source changes invalidate batch availability/cost assumptions,
  not retained board geometry. Explicitly no independent manufacturing admission.

- OR12 validation checkpoint, 2026-10-31 07:55 PDT: quote-only carrier BOM
  has 137 refs (127 SMT + ten manual), pod 29 (28 SMT + one manual), all per
  board. Batch 915 SMT + 60 JLC manual + 25 user = 1,000; eight mounting features
  explicitly excluded. Full/SMT-only alternative BOMs retain exact identities;
  global codes blank in upload BOM rather than misrepresent public stock as
  private inventory. Released CPLs and Gerber ZIPs are byte-identical. KiCad
  10.0.4 read-only audit passed native fields, exclusions and poses for all 177
  footprints; 25 inherited vendor-angle offsets retained, not silently reset.
  Initial probe used nonexistent GetProperties API; corrected to native field
  access before audit. Nonfatal KiCad property-enum/image warnings disclosed.
  Portable verify PASS; 29 order-readiness + 15 publication tests PASS, including
  seven new quote regressions; 256 released files preserved. Native audit is a
  coordinator source check, not new independent engineering/vendor acceptance.
  Milestone advance is the reproducible quote-only artifact; ordering holds
  remain. Next is actual JLC file ingestion/matching/process/quote after scoped
  user authority. Publish only these drafts/tools/handoff/journal, no vendor
  action or purchasing. No board/regeneration/backtrack needed.

- OR12 dispatch, 2026-10-31 07:51 PDT: user authorizes preparing, validating
  and publishing quote-only BOM/CPL files for 5 carriers/10 pods, no purchases.
  Coordinator owns one deterministic source-bound draft and regression checks;
  not new independent engineering admission. Scope: new quote-draft revision,
  builder/checks, native read-only audit, handoff and journal. Preserve release,
  exact identities, original CPL angles and 975/25 installation split. Stop by
  08:15 PDT with verified draft or concrete blocker, including review/push; no
  JLC upload, cart, contact, order or payment. No new stock-search cycle. Native
  audit found intentional retained CPL angle offsets; preserve and disclose,
  do not equate raw footprint angle to vendor angle. Inspect current JLC format
  documentation, but do not claim vendor ingestion or matching acceptance.

- OR11 pre-push validation, 2026-10-31 PDT: publication preservation PASS for
  256 files; 15 publication + 22 order-readiness tests PASS; diff whitespace
  check clean. Remote and local starting commit both b39eb5a4. Seven scoped
  order-readiness paths selected for publication; no release, design, original
  stock/pricing observations or vNext instructions modified. This is a handoff
  verification, not independent manufacturing acceptance or a completed quote.

- OR11 publication dispatch, 2026-10-31 PDT: publish OR10 proposal, full
  38-row worksheet, its four regression tests, and next Mac quote handoff.
  Existing worktree changes are exactly the prior coordinator's artifacts.
  No board engineering, vendor upload, cart/order action or purchase. Validate
  payload preservation/tests/diff, stage only named order-readiness files,
  normal push on existing branch, then verify exact remote commit. Updated
  handoff exposes empty factory BOMs as a local draft prerequisite and carries
  forward one integrated job quote task, not another inventory-research cycle.

- OR10 checkpoint, 2026-10-30 20:27 PDT: complete 38-identity proposal and
  draft CSV account for all 1,000 installed parts (975 JLC requested, 25 user).
  Five regular estimates $74.78 plus two global observations $152.93 yield
  $227.71 for seven shortage lines only. Nominal 558 query pieces cover 110
  installed positions; minima surplus is not silently called free/user-delivered
  spares. RECOM ordinary purchase is excluded. Review binds exact codes/needs
  and retains OR9 transcription/arrival/attrition limitations. Publication
  preservation PASS for 256 payloads; 15 publication + 22 order-readiness tests
  PASS, including four new proposal-accounting regressions. OR6/OR9 evidence
  files remain byte-identical to b39eb5a4. No order hold closed or manufactured
  quote claimed. Milestone reassessment: useful plan/pricing evidence advanced,
  but actual order admission did not. Stop routine inventory research; next
  discriminating work is reviewed vendor drafts and integrated job quote/process
  evidence, subject to scoped external-action authority. No automatic dispatch,
  purchase, substitution, upload, contact, commit or push in this task.

- OR10 dispatch, 2026-10-30 20:24 PDT: user requests verification/review of
  pushed OR9 and one consolidated procurement proposal, explicitly no purchases.
  Fetched remote b39eb5a45cad93410c6e01a9b09eaf7d69e39a83; its only delta is the
  pricing report, observations JSON and STATUS. Clean branch fast-forwarded.
  Coordinator owns proposal and deterministic checks; no independent engineering
  admission claimed. New input changes RECOM to Global Sourcing; do not repeat
  the seven/35-part lookup. Scope: all 38 identities and exact 5/10 ownership,
  with seven priced recovery lines separated from unquoted remainder. Stop by
  20:40 PDT with a decision-ready plan and explicit unknowns, not an order.
  Preserve OR6–OR9 observations and cumulative history; no cart, uploads,
  contacts, purchases, substitutions or manufacturing changes. Missing account
  quote/arrival/allocation cannot be closed by report writing. Proposal remains
  local unless publication is separately requested.

- OR9 checkpoint, 2026-10-30 20:15 PDT: after user completed login, signed-in
  catalog/global results recorded in JLC-PRICING-20261030.md/.json. Five regular
  indicative prices visible; exact RECOM now unavailable for purchase, and exact
  PCM1864DBT global offers visible. Global results are selective, not exhaustive;
  account fees and usable warehouse arrival dates remain unresolved. Some searches
  returned late, so these are not claimed as fully assessed global offers. No cart
  changes, quote requests, orders, supplier contact, substitutions or payments.
  No ordering hold closed. Preferred mixed JLC path requires exact RECOM global
  and ADC plus five regular lines; external exact consignment is fallback.
  Publication preservation PASS 256; 15 + 18 tests PASS in isolated source snapshot.

- OR9 dispatch, 2026-10-30 20:09 PDT (2026-10-31 03:09 UTC): user forwards
  published seven-shortage pricing handoff at 916323c6. Coordinator resumes one
  read-only account-offer pass; OR6 availability and OR7/OR8 history remain intact.
  Allowed writes: new dated pricing evidence and STATUS in isolated local source
  snapshot. No complete clean checkout claimed: snapshot contains vnext and Crow
  project from the pinned commit; original damaged checkout/index untouched.
  Browser controls confirmed, with initial stale-session/input recovery recorded.
  Exact CTS page shows Sign In; user requested to complete login/MFA. Account
  offers are pending login, not unavailable stock. No cart/order/submission action.
  Stop after one seven-line pass or 30 minutes active browser work, with elapsed
  fallback deadline 20:39 PDT excluding no work already performed. No repeated
  35-line pass, substitute research, supplier contact, payment or manufacturing
  upload. Coordinator is sole writer and evidence verifier, no stage acceptance.

- OR8 publication dispatch, 2026-10-30 PDT: user authorizes remote publication
  for the MacBook pricing/lead-time pass, explicitly no purchases. Retain branch
  ancestry from browser evidence commit be16560f. Publish only scoped
  order-readiness comparison/review/evidence tests, handoff and STATUS. Verify
  payload preservation, tests, staged paths and remote commit identity. Updated
  handoff carries forward missing account prices, fees and usable-stock dates,
  with a single bounded pass and no cart/order/submission authority.

- OR8 verification, 2026-10-30 18:30 PDT: 256 public payloads preserved;
  15 publication and 18 order-readiness tests pass. Additional read-only checks
  bind all seven comparison rows to OR6 exact identities, quantities, minima and
  source URLs, verify USD/EUR arithmetic independently, and confirm both browser
  evidence files exactly match be16560f. Engineering acceptance remains
  NOT_REASSESSED and order remains DO-NOT-ORDER. Comparison and journal are local
  on `codex/crow-jlc-source-review-20261030`; no commit/push or vendor action.

- OR8 research checkpoint, 2026-10-30 PDT: all seven exact external listings
  show sufficient installed-quantity stock; six are cached DigiKey snapshots,
  one is a direct Bürklin fetch. JLC catalog tiers fetched directly and bound
  to exact codes; no account replenishment quotation inferred. Three capacitor
  minimum-order illustrations total $27.32, changing the preferred logistics
  recommendation toward JLC-managed procurement. Published global purchasing
  timing is 9–20 business days after a separately described 1–3-day review;
  actual part receipt dates remain unknown. Conflicting consignment fee
  publications are disclosed rather than summed. No source/BOM geometry changed,
  vendor action taken, or sourcing/assembly acceptance claimed. OR8 artifact is
  a bounded comparison; missing account quotes are the next discriminating input.

- OR8 dispatch, 2026-10-30 18:23 PDT: user explicitly requests seven-shortage
  exact external/consignment versus JLC replenishment comparison, including cost
  and time. New deliverable is a combined sourcing decision, not another full
  catalog pass or attempt to infer vendor agreement. Reuse OR6 observed minima
  and OR7 reconciliation; refresh only external offers and relevant JLC policy/
  prices. Coordinator owns authoring and checks; no independent admission claim.
  Allowed writes: order-readiness comparison/evidence and journal only. Deadline
  18:38 PDT including validation; preserve OR1–OR7 history/spend. No substitutions,
  supplier messages, uploads, cart/library changes, reservations or purchases.
  Missing account-specific quotations remain explicit unknowns, never estimates
  invented to close a hold. Stop with ranked complete routes and exact missing
  inputs rather than repeat requests for each passive component.

- OR7 checkpoint, 2026-10-30 18:06 PDT: fetched and reviewed exact user commit be16560f
  (only browser report, observations JSON and STATUS delta). Preserved both
  browser evidence files byte-for-byte. Source-supported identity explanations
  and CTS/TI process/package facts now inform a draft, not an independent
  approval. Original 26/7/2 classifications and supplier timestamp semantics
  remain unchanged. Manufacturer PDF/press access failures are disclosed; maker
  originals hosted by distributors support the limited identity-history review.
  Seven exact-part routes compared without repeating stock lookup. New browser
  binding tests cover worksheet hash, subjects/references, 975-unit scope,
  separate-pool arithmetic, manual ownership and unknown lead times.
  Eighteen sourcing tests plus fifteen publication tests PASS; all 256 payloads
  preserved. This is useful preparation, not supplier agreement/allocation,
  order admission or restored goal completion. Stop at the draft; no further
  supplier-agreement retry, external write or purchasing action. Prior OR1–OR6
  budget/history retained; this bounded review used approximately three elapsed
  minutes after dispatch, within the 18:13 PDT deadline.

- OR7 dispatch, 2026-10-30 18:03 PDT (2026-10-31 01:03 UTC): consume user-published
  browser commit be16560f0fe14c102ea048fbad64d362366efc51. OR6 establishes a new
  complete browser matching result, not order acceptance; no repeated catalog
  polling. Next discriminating work: manufacturer reconciliation of the two
  identity exceptions and CTS/package process facts, then one exact-part sourcing
  draft. Coordinator is sole writer/checker; no independent admission claimed.
  Allowed writes: order-readiness only, outside sealed payloads. Deadline 18:13
  PDT including tests/checkpoint. Preserve prior OR1–OR6 history/budgets; this is
  the returned-evidence review, not a reset of the supplier-agreement plateau.
  Stop at a reviewed draft; no upload, supplier contact, substitution or purchase.
  Loaded both vNext entrypoints, sourcing, part-recheck, task-interface, dispatch,
  recover and resume. Ordering adapter remains procedural, not an automatic gate.

- OR6 checkpoint, 2026-10-30 17:39 PDT (2026-10-31 00:39 UTC): complete
  browser matching pass recorded in JLC-BROWSER-20261030.md/.json. All 35 exact
  requested subjects and 975 JLC-requested installed parts joined to v3 demand;
  26 sufficient, seven insufficient/zero, two stocked identity-review candidates.
  Exact CTS/TDK/TI codes recovered, Panasonic hyphenless candidate explicit;
  PCM1864DBTR excluded. JLC public eligibility is separate from job acceptance.
  No current global-sourcing offer/lead time or allocation established. This
  advances the requested browser evidence deliverable, not any order-hold closure.
  Coordinator checks PASS; preservation PASS (256); 15 publication and 14 sourcing
  tests PASS with /private/tmp and isolated local-HEAD stock_lookup.py import.
  Initial environment failures and corrected preliminary tally retained in report.
  No substitutions/uploads/cart additions/vendor contacts/orders/design changes.
  Approximately nine elapsed minutes for OR6 plus earlier interrupted setup;
  prior approximately 35 OR1–OR5 author minutes retained. No independent acceptance
  claimed. Stop after this complete pass. Preferred next path: reviewed exact JLC
  sourcing/matching draft; fallback: exact Western-source consignment preparation.
  Upload/contact, supply allocation, exact-job process and quote approval stay open.

- OR6 browser dispatch, 2026-10-30 17:30 PDT (2026-10-31 00:30 UTC):
  user requests the MacBook handoff exact-JLC availability pass, with no
  substitutions or orders. New discriminating evidence is the functioning Mac
  Chrome catalog UI, unavailable to the previous server attempts. Scope is one
  complete pass over 35 JLC-requested identities, preserving the 60/20/5 split.
  Coordinator is sole writer/verifier of observations, not independent sourcing
  acceptance. Allowed writes: new dated evidence and this STATUS/journal only.
  Stop after the pass or by 18:15 PDT, including checkpoint and portable checks;
  no repeat stock cycles, uploads, vendor contact, purchases or release changes.
  Prior OR1–OR5 history and approximately 35 author minutes remain retained.
  vNext entrypoints, sourcing, part-recheck, task-interface, dispatch and recover
  read from local HEAD because vnext is absent from the working tree; no checkout
  or index repair attempted. Browser setup succeeded: exact C599441 page shows
  available order quantity 569 vs 50 need. This is a public stock observation,
  not allocation or agreement to the released manual assembly process.

- Publication handoff, 2026-10-26: user requests all inputs needed for MacBook
  continuation on remote main. Scope: current order-readiness records, exact
  60/20/5 assembly ownership, portable tests and a browser-first handoff. Sealed
  payloads and unrelated worktrees remain unchanged. No order approval claimed.

- User route decision, 2026-10-26: “lets have JLC do the 60 and i will do the 20.”
  Recorded JLC-requested 50 RJ jacks, five power jacks and five RECOM modules;
  user-owned ten microphones and ten buzzers, plus the previously accepted five
  Picos. Updated plan, unsent inquiry and reproducible v3 procurement worksheet;
  v1/v2 retained. No inventory refresh, machine-placement change, supplier
  acceptance, contact, upload, purchase or ordering-hold closure is claimed.
  Regression checks enforce the 60/20/5 manual split and exclusion from SMT routes.

- OR5 dispatch, 2026-10-26 16:00 UTC: user authorizes progressing to exact JLC
  mapping and manual-route preparation. Pico-fit investigation remains stopped
  per user decision. Prior OR4 produced prerequisite capability evidence, not
  order acceptance; new deliverable is a source-bound 38-identity procurement
  map, not another tolerance/stock-exception loop. Reuse existing positive supply
  evidence and retained catalog leads; exact-code supplier checks establish
  proposed factory candidates, not allocated stock. Coordinator is sole writer
  and consistency verifier, no independent receipt claimed. Writes confined to
  order-readiness, immutable release unchanged. Deadline 16:15 UTC including
  validation/checkpoint, approximately 28 prior author minutes retained. No
  purchases/uploads/vendor contact. Manual ownership choice requested in parallel;
  absent reply retain proposed options, never assign unaccepted work to user.
- OR5 checkpoint, 2026-10-26 16:07 UTC: 31 catalog-code leads checked against
  exact supplier products (six OR3 observations reused with original timestamps).
  Draft mapping joins all 38 identities/1,000 installed parts to released refs;
  manual parts excluded from machine candidates. Current v2 corrects two Western
  fallback locators; v1 retained. Published shortage at one pool does not erase
  previously adequate independent offers. Fourteen unit/data tests PASS;
  publication preservation PASS for 256 files; whitespace check PASS. User's
  interim question changes the immediate handoff to a manual-part breakdown,
  not a new manual-route authorization. No vendor-ready exports/allocations or
  independent acceptance issued. Elapsed approximately seven minutes; cumulative
  approximately 35 author minutes. This advances the requested mapping artifact,
  not full order readiness. Stop this bounded pass with exact route questions;
  do not repeat lookup cycles or reopen accepted prototype Pico-fit risk.

- OR4 dispatch, 2026-10-26 15:40 UTC: focused user-requested capability review,
  not another stock retry. New route input: user-owned Pico assembly removes
  the need to find a vendor for that installation. Check published JLC process
  limits against frozen controls, distinguishing designer reject limits from
  maker requirements and supplier guarantees. Coordinator owns this literature
  comparison and decision record, not engineering reacceptance. Allowed writes:
  order-readiness only; no supplier contact, uploads or design changes. Deadline
  15:50 UTC including checkpoint. Prior approximately 25 author minutes retained.
  Deliverable: requirement-to-capability comparison and recommended next action.
  Instructions read: both vNext entrypoints, fabrication, assembly-verify,
  task-interface, dispatch and recover. Manual coordinator binding unchanged.
- OR4 checkpoint, 2026-10-26 15:43 UTC: official JLC capability/help pages
  support general partial SMT/THT assembly and omission of Pico paste/placement.
  Published drilling/outline options do not establish all exact sealed limits;
  no universal final radial/3D pose guarantee found. Source controls explicitly
  identify several limits as design-owned, motivating a focused requirement/fit
  review rather than another general search. Standard PCBA is a candidate to
  evaluate, not adopted or guaranteed necessary. Conflicting generic wave/manual
  wording prevents inference of acoustic hand-only/no-wash handling. Literature
  report and unsent inquiry updated; user Pico ownership reduces unassigned
  manual component count from 85 to 80, without changing geometry requirements.
  Publication preservation PASS for 256 payload files; diff whitespace PASS.
  No independent review, exact-job agreement or ordering hold closure claimed.
  Approximately three elapsed author minutes for OR4; cumulative approximately
  28 minutes. Stop at requested literature-review result; proposed engineering
  changes require a separate scoped attempt and affected acceptance.

- OR1 dispatch, 2026-10-26: coordinator author, one writer. Inputs: immutable public
  package and its 38-row demand; vNext dispatch/recover, sourcing/part-recheck and
  fabrication/assembly contracts; public JLC capabilities. Writes confined to
  this order-readiness directory and its parent contract. First-attempt budget
  10 minutes elapsed, at most one follow-on after explicit reassessment; total
  20 author minutes plus 10 independent-review minutes for this route decision.
  Highest impact: determine whether the accepted manufacturing controls and
  manual operations have an executable supplier path before procurement.
  No repeat stock polling, no substitutions, no acceptance/receipt edits.
- OR1 checkpoint, 2026-10-26 15:06 UTC: first bounded attempt complete; no
  ordering hold closed. `jlc-inquiry-draft.md` is prepared but NOT SENT. Current
  public fabrication tolerances, stencil policy and consignment rules do not
  establish compliance for this exact job. The 38-MPN aggregate discovery
  screen returned empty/unrelated results and no exact matches. This is a
  discovery limitation, NOT proof of zero stock; direct supplier verification
  and allocation remain open. No substitutes were selected.
  Evidence: `stock-20261026-1/observations.json`, bound to demand SHA-256
  `bb707f71c9c0cbdd4cc1e681b250c42b90c7122eb6ac3018c7cbe550aa482194`.
  Scope checks passed: 38 exact identities, 1,000 installed components, per-part
  requested quantities preserved. Publication verification passed for all 256
  payload files; engineering acceptance was not reassessed and order status
  remains DO-NOT-ORDER. `git diff --check` passed.
- OR1 reassessment: do not repeat this discovery endpoint or infer supplier
  feasibility from generic webpages. Highest-impact next evidence is an exact-job
  JLC response. Ranked next options: (1) user forwards the consolidated inquiry
  through their JLC account, seeking full completion plus SMT-only fallback;
  (2) identify a separate qualified manual assembler, then seek split quotations.
  Vendor submission/contact and disclosure of the complete manufacturing package
  require explicit authorization; no contact/upload/purchase has occurred.
  Await that direction before external coordination. Direct 38-part supplier
  checks, independent route review and quote approval are still required; this
  checkpoint is not their acceptance and is not a fabricated vNext gate receipt.
- OR2 dispatch, 2026-10-26 15:07 UTC: previous turn classified progress in
  prerequisite evidence, not order-hold closure. Supplier contact still awaits
  authority. Independent safe work: direct supplier pages can distinguish an
  aggregate search limitation from a real availability problem. One bounded
  fallback, deadline 15:16 UTC, within the existing 20-minute author allowance;
  no repeat aggregate queries. Coordinator is sole writer and checks exact
  maker/MPN, present stock and quantities against sealed 5/10 demand. Allowed
  writes remain order-readiness only. Older 5/40 sourcing observations supply
  URLs, not current quantities or verdicts. A complete supplier observation
  table is the output; allocation and independent acceptance remain separate.
  Instructions loaded: both skill entrypoints, task-interface, dispatch, recover,
  sourcing and part-recheck. No new stage or order-acceptance adapter is claimed.
- OR2 checkpoint, 2026-10-26 15:12 UTC: direct supplier-page attempts cover all
  38 current identities. Observation counts: 30 displayed sufficient; five
  unresolved after insufficient offers; one unverified inventory; one stale
  positive; one alias-review lead. See `SOURCING-20261026.md` and its CSV for
  exact URLs, quantities, cache-age limitations and failed fallback checks.
  Rejected older positive snippets contradicted by opened pages. No inventory
  pools summed, substitutions adopted or vendor communications performed.
  Demand-join validation PASS: exact manufacturer/MPN/quantity equality, 38 rows,
  1,000 installed components, sufficient-count arithmetic. Publication preservation
  PASS for 256 payload files; `git diff --check` PASS. Instruction load was 5,044
  words across seven files, an estimate rather than a token measurement.
- Milestone reassessment: two author checkpoints yielded prerequisites and
  actionable sourcing exceptions, but zero ordering holds are closed. Routine
  local research stops under vNext's plateau rule. Causal missing facts are an
  agreed fabrication/manual-assembly route, supplier-confirmed exact stock and
  allocation, and exact-job pricing; these cannot be manufactured by a review
  agent. The prepared inquiry now includes all eight sourcing exceptions.
  Preferred next action remains the user's JLC account inquiry; fallback is a
  named manual assembler and split quotations. The full 5/10 ordering objective
  remains active and incomplete. This is the second goal turn with the external
  coordination/authority dependency; no live process is being monitored.
  Actual author elapsed across OR1/OR2 is approximately 13 minutes, below the
  cumulative 20-minute allowance; unused time does not authorize a third repeat.
- Goal blocking audit, third consecutive goal turn, 2026-10-26: previous turn
  classified progress (38-part direct observations and actionable exceptions).
  Reopened current journal and directory: no supplier response, exact-job quote,
  allocation confirmation or new user authorization is recorded. The same
  external coordination/authority dependency has persisted across all three
  goal turns. No live process exists to poll. Bounded public checks and inquiry
  preparation are complete; another unchanged research/review cycle cannot
  provide supplier agreement or user approval. Goal status set to BLOCKED,
  not complete and not user-paused. Resume on supplier response or explicit
  direction enabling the named inquiry/split-assembler path. Preserve the full
  objective, all nine holds, sealed inputs and cumulative attempt history.
- OR3 dispatch, 2026-10-26 15:26 UTC: user explicitly requests best-effort
  self-service resolution using visible stock and JLCSearch. Preserve the prior
  plateau and spent attempts. New hypothesis: search/access limitations, not
  absent inventory, explain some holds; compare documented listing/full-field
  queries and exact code pages, then current direct supplier data. Coordinator
  owns writes within order-readiness; no sealed changes, vendor messages,
  uploads or purchases. Bounded recovery ends 15:45 UTC, including verification
  and checkpointing; prior approximately 13 author minutes remain charged.
  Success: evidence-backed resolution or narrowing of exact sourcing exceptions,
  and separation of publicly resolvable requirements from genuine job-specific
  decisions. The manual coordinator remains the execution binding; no invented
  adapter admission. Public capability review must not waive source controls.
- OR3 checkpoint, 2026-10-26 15:38 UTC: catalog-code JLCSearch queries recovered
  three exact discovery hits. Direct supplier Product JSON-LD and exact bound
  product data recovered seven exceptions; a newer opened DigiKey product page
  supports the eighth (ERJ-3EKF68R0V, 64,642 versus five required; four-day cache).
  Correction: earlier empty aggregate results and missing extracted stock fields
  did not justify treating these as shortages. All eight now have positive
  availability observations, with pool/freshness limitations retained. This is
  not real-time verification of all 38 or a JLC allocation receipt. No part
  substitutions, source-control waivers or factory BOM/CPL mutations occurred.
  Public policy confirms manual-pad paste exclusions align with JLC's selected
  population workflow and both boards meet the precision-profile minimum size;
  it does not establish custom finished holes, registration/pose, seating,
  aperture constraints or special manual operations. Inquiry narrowed accordingly,
  NOT SENT. Eight regression/data-binding tests PASS; publication preservation
  PASS for all 256 payload files; `git diff --check` PASS. Initial `python` test
  invocation found no interpreter; rerun with `python3` completed successfully.
  These are coordinator checks, not independent adversarial acceptance.
  Elapsed OR3 approximately 12 author minutes; cumulative approximately 25 across
  OR1–OR3, within this renewed bounded recovery. No ordering hold closed. End this
  attempt with materially improved evidence, not repeat stock polling. Preferred
  next route remains one exact-job process/quotation inquiry; fallback remains
  JLC SMT plus qualified manual completion. Their authority dependency persists.
