# PCB-COMMISSION journal — crow-roof-array-v1

## 2026-09-01 14:37 — start
- did: Commissioned a clean `design`-target scaffold from the user's verbatim `/pcb-design` request.
- result: `PCB-SCAFFOLD OK`; 47 files created; `COMMISSIONING-HOLD.md` present; stage `PCB-COMMISSION` INCOMPLETE.
- next: Audit archived crow-array evidence before proposing a successor architecture.

## 2026-09-01 15:10 — iterate 1
- did: Audited the latest archived pod and central board source, local gates, firmware boundary, and first-article status.
- result: Found a cross-board connector P0: pod pins 4/5 are +5 V and 7/8 ground, while central pins 4/7 are +5 V and 5/8 ground; a straight-through cable shorts the protected supply. The XU316 UAC2/TDM application is also absent.
- next: Treat archived designs as references only and develop a firmware-free successor comparison.

## 2026-09-01 15:35 — iterate 2
- did: Compared eight- and sixteen-channel acoustic geometry and central ADC/module architectures using primary vendor and research sources.
- result: Produced one DRAFT/INCOMPLETE architecture study; three proposed ADRs; zero accepted part, coordinate, connector, power, or CAD locks.
- next: Ask Q1-Q3 and retain the commissioning hold.

## 2026-09-01 15:45 — handoff
- did: Updated the brief, status, architecture checkpoint, report and interactive geometry explainer.
- result: Project remains blocked at `PCB-COMMISSION`; no rebuild, schematic, layout, release or order artifact exists.
- next: User answers Q1-Q3; then close D-SPEC/D-MATE, select eight-channel geometry, commission board roles and part dossiers.

## 2026-09-01 16:05 — iterate 3
- did: Ran an independent read-only red-team review of traceability, evidence labels, timing claims and the sixteen-channel option.
- result: No new P0; relabelled shared-clock adequacy and alias spacing as inferred, reduced sixteen channels from an “upgrade path” to an unproved study, and made all acceptance limits explicitly OWED by Q1/Q2/Q3.
- next: Retain the commission hold until the user supplies those requirements.

## 2026-09-01 16:20 — iterate 4
- did: Recorded the user's 3D/identity/PoE directive; quantified aperture and vertical-baseline tradeoffs; separated source-track identity from persistent biological identity; and compared external PoE/Ethernet architectures.
- result: Added one DRAFT/INCOMPLETE addendum and two proposed ADRs. Compared externally PoE/Ethernet roof-appliance options with optional internal USB and neutral 8/12/16-channel noncoplanar candidates. No coordinate, channel count, part, power class, interface or identity threshold was accepted.
- next: Answer Q1/Q4-Q6, then select 8/12/16 channels, close the PoE/pod interfaces and retain the commission hold until D-SPEC/D-MATE are complete.

## 2026-09-01 16:45 — iterate 5
- did: Preserved the user's 8 m-radius statement and immediate 8 m-diameter correction; evaluated a planar, single-active-caller array; recorded 120-second cross-recording identity and permission for short internal USB.
- result: Proposed, but did not accept, an eight-channel seven-outer-plus-center planar study at nominal 4 m radius, superseding the earlier proposed noncoplanar count study. Its largest acoustic lag is 23.26 ms/1,116 samples at 48 ksample/s. The branch makes no elevation/robust-3D claim; identity is graded across whole recording files and overlap may remain unresolved.
- next: Answer Q7, survey the usable roof polygon and cable routes, then simulate the planar seven-outer-plus-center and four-outer/four-inner candidates before accepting geometry or starting PCB work.

## 2026-09-01 17:05 — iterate 6
- did: Recorded the user's answer to Q7 and replaced the inferred cross-recording biological-identity goal with a within-file stationary-source track.
- result: Proposed anonymous `caller-A` continuity only inside one 120-second file. Labels expire at file end and reset or become unknown after material motion, overlap or low confidence. ADR 0007 supersedes ADR 0004; no voice biometric, enrolment database or cross-file association is required.
- next: Survey the roof, simulate seven-outer-plus-center versus four-outer/four-inner, and derive the stationarity/confidence gate from stationary and moving-source tests before accepting architecture or beginning PCB work.

## 2026-09-01 17:20 — iterate 7
- did: Recorded the user's Raspberry Pi 5 selection; accepted the one-external-PoE/Ethernet plus short-internal-UAC2 boundary; and reviewed current official Pi 5 power, USB, storage, cooling, mechanical and PoE compatibility evidence.
- result: ADR 0005 and new ADR 0008 are accepted at the system boundary. Pi 5 is the recorder/network bridge, not the sample clock. The leading bench candidate is 4 GB Pi 5 plus Active Cooler, standard M.2 HAT+, NVMe and MCHStreamer, but exact variants remain unselected. The currently listed official PoE+ HAT is not a Pi 5 authority, so the exact isolated PD/splitter stays OWED.
- next: Prove exact eight-channel ALSA order and 120-second file integrity on the official 27 W supply; measure the complete load; then select and repeat under a standards-compliant PoE path before central-carrier schematic or floorplan work.

## 2026-09-01 17:35 — iterate 8
- did: Red-teamed the Pi 5 capture, spool, analog-quality and PoE admission claims; replaced frame-count and exactly-once assumptions with falsifiable direct-hardware, reset, crash and whole-appliance tests.
- result: The proposed recorder now requires persistent direct ALSA hardware capture, deterministic continuity and relative-phase stimuli, analog noise/crosstalk tests under concurrent loads, a same-filesystem crash-recovery spool contract, conflict-detecting idempotent at-least-once server transfer and externally measured PoE power corners. No bench result is inferred from the design.
- next: Assemble the official-PSU Pi 5/MCHStreamer bench and derive numeric phase, analog-quality, long-run, outage and power acceptance limits before selecting the carrier or PoE implementation.

## 2026-09-01 17:50 — iterate 9
- did: Created `codex/crow-roof-array-board-dev-20260901` from the reviewed Pi 5 checkpoint and recorded the user's release directive verbatim.
- result: The capability target is now `release`/`PCB-RELEASE-SEAL`. The commission hold remains active while the exact board partition, power/interface facts, connector assemblies, parts, sourcing and mechanical authorities are reviewed.
- next: Close the simplest conservative central-recorder PCB scope and exact sourcing boundary, then commit the commission/architecture/sourcing admission before conductor execution.

## 2026-09-01 18:25 — iterate 10
- did: Audited the requested release boundary against the one-board project contract and the whole-appliance acceptance criteria.
- result: Accepted ADR 0009. This project remains the held integration authority; `crow-audio-carrier-v1` and `crow-mic-pod-v3` were commissioned as separate release-target PCB projects. No physical roof, acoustic or weather criterion was marked met.
- next: Close the shared spoke interface and exact parts in both child projects, then develop the central carrier first.

## 2026-09-01 18:50 — iterate 11
- did: Rechecked the proposed multichannel ADCs against current primary sources and the selected MCHStreamer timing.
- result: Accepted ADR 0010. The four-device TAA5242 hardware chain is invalid; one CS5308P-DN matches TDM8 at 48 ksample/s with one conversion die and no initialization firmware. Its unusual post-power reset pulse, vendor-image interop and consigned/manual assembly remain explicit holds.
- next: Implement the CS5308P carrier and its eight buffered analog channels, then prove reset timing and TDM behavior on the first article before ordering.

## 2026-09-01 19:20 — iterate 12
- did: Closed the cross-board spoke contract after an independent hostile review of the archived pin-map failure class.
- result: Accepted ADR 0011. Parent, carrier and pod now carry byte-identical contract SHA-256 `9cd9ca21dd71a3bab04fe15c24b2719525fbd9e3955e8bdce7d4ea9508b403ea`: internal Micro-Fit behind sealed glands, explicit cavity/conductor identity, 12 V power planes and hot-corner protection requirements, balanced-audio impedance/headroom/coupling limits, and honest `OWED` harness/polarity/length qualifications. Five contract tests pass, including four hostile cases.
- result: Refroze the three byte-identical spoke contracts at SHA-256 `927bf709d15a187e97577621554c4991d72d0451004f7af00e6d1680fae3d1da` after the carrier selected exact `1812L035/60MR`. The carrier trip ceiling is 0.70 A at 20 C for cable/pre-pod faults; pod `0ZCJ0010FF2E` remains the 0.25 A-trip downstream-board tier. The 22 AWG cable, 7 A contacts and 1.0 A carrier trace class screen above the carrier ceiling, while source prospective current, thermal selectivity, fault energy and one-fault/seven-healthy behavior remain measured holds.
- next: Require both generated KiCad boards to emit independently regraded pad-to-net receipts before either release candidate can pass the parent interface gate.
