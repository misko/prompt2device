# brief: crow-roof-array-v1

status: draft
prompt_sha256: a6fcb7d5b8465bc23415c7d5f9381b368f12d69455da135d8b6b0b1cb89965b3
current_release: no

## Original prompt

<!-- prompt-verbatim-begin -->
/pcb-design please help me design a star shaped distributed microphone array to record and isolate which crow is talking from my roof

<!-- prompt-verbatim-end -->

- date: 2026-09-01
- channel: `/pcb-design`

## Current source interpretation — 2026-09-12

The later user-approved factory RJ45 direction supersedes the spoke
Micro-Fit/Belden/Cat5e assumptions retained in the dated log below. The current
source selects Würth 615008160221 and Weidmüller 8909650150 Cat6A cords,
with the exact pin map in `03_src/rules/spoke_interface.yaml`. This is
source adoption, not hardware qualification or release acceptance.

## End goal — definition of done

Create a weather-conscious, sample-synchronous roof microphone system whose
home-run cables form a physical star, records raw multichannel audio to a
Linux host, estimates a noncoplanar three-dimensional source track or an
explicitly calibrated multi-position signature with reported uncertainty, and
can produce a spatially focused audio stream. The required caller label is an
anonymous within-file source track: it persists only inside one 120-second
recording and only while the crow's calibrated position signature remains
sufficiently stationary. It expires at file end and becomes new or `unknown`
after material movement, overlap or ambiguity; no cross-recording biological
identity claim is required. One Cat6 PoE run is available to the device and a
short internal USB link is user-permitted. The accepted compute/network
boundary is one Raspberry Pi 5 roof appliance on that Ethernet/PoE uplink,
with the USB-audio link wholly inside the appliance. The exact Pi SKU, PoE
power implementation, storage, cooling and enclosure remain open. The first
deliverable is a controlled prototype, not an unattended lightning-qualified
roof installation.

| # | Criterion | Source | Status |
|---|---|---|---|
| G1 | Record at least eight simultaneous, sample-synchronous microphone channels at 48 ksample/s or better to one Linux host and retain raw channels. | P, A2, A5, P2 | unmet |
| G2 | Estimate a calibrated noncoplanar 3D source track, or a declared multi-position spatial signature, from surveyed microphone coordinates; report confidence and unresolved/ambiguous events honestly. | P2, P5, A6, A11, D2 | unmet |
| G3 | Associate an isolated call with the same biological crow across separate recording files. | P3, P5, A6, A10, Q4, Q7 | dropped — P7 |
| G4 | Define one compiled contract per operated interface—PoE/Ethernet, analog pod, internal USB and module/board boundaries as applicable—and check it at every represented end. The external building link is genuine PoE/Ethernet; the pod spokes use the adopted non-Ethernet factory RJ45 analog/power boundary in ADR 0013. | P4, P8, A3, A4, A7, A14, A16 | unmet |
| G5 | Pass bench synchronization, acoustic calibration, outdoor first-article, weather, and building-entry safety validation before unattended deployment. | P, A2 | unmet |
| G6 | Require no project-authored embedded firmware; a named, hash-bound vendor-module image may be loaded unchanged and host software remains outside this PCB commission. | A2 | unmet |
| G7 | Within each 120-second file, maintain an anonymous caller/source label only while the calibrated position signature remains within an evidence-derived stationary gate; expire the label at file end and reinitialize or return `unknown` on material movement, overlap or ambiguity. Report track switches and unresolved time. | P7, A13 | unmet |
| G8 | Use a Raspberry Pi 5 roof-appliance host and prove direct-hardware all-channel UAC2 continuity and CS5308P interchannel phase across resets, analog noise/crosstalk under concurrent load, crash-recovery-tested local spooling, idempotent at-least-once Ethernet transfer, bounded outage buffering, externally measured power margin and thermal operation in the admitted configuration. | P8, A14, A17 | unmet |

## Log

### A1 — 2026-09-01 — assumption (not asked)
Assumed: “which crow” means spatially attribute a call to a tracked source
position, not recognize an individual animal from its voice.
Authority: P delegates the engineering interpretation needed to begin a study.
Escalate if: biometric individual recognition is required, or the user will not
use a synchronized camera to associate a source track with a physical bird.

### A2 — 2026-09-01 — assumption (not asked)
Assumed: this is a `design`-target PCB commission with custom firmware
forbidden. The design may use an unchanged vendor USB-audio module and later
host-side Linux DSP, but this project will not author MCU/FPGA/XMOS firmware.
Authority: conservative commission boundary.
Escalate if: a custom digital microphone node, wireless pod, or custom USB
audio firmware is desired.

### A3 — 2026-09-01 — assumption (not asked)
Assumed: the lowest-risk first architecture is balanced analog audio over one
home-run cable per pod into eight channels of one central ADC on one shared clock;
distributed unsynchronized ADC nodes are not the baseline.
Authority: P requests a distributed star and permits architecture selection.
Escalate if: cable length, conduit, or galvanic-isolation constraints make
analog home runs unacceptable.

### A4 — 2026-09-01 — assumption (not asked)
Assumed: the successor will use a keyed weather-resistant circular connector
family, with M12 only a candidate, and will not expose custom power on an RJ45.
Authority: the archived pod/central pair has a destructive cross-board pin-map
mismatch and a documented PoE misuse hazard.
Escalate if: existing structured cabling must be reused.

### A5 — 2026-09-01 — assumption (not asked)
Assumed: start with an eight-channel prototype and avoid foreclosing a later
sixteen-channel study. Exact microphone count and geometry remain open
until the roof and localization questions below are answered.
Authority: module-first risk reduction.
Escalate if: simultaneous-source separation or robust 3D localization is a
first-article requirement.

### Q1 — 2026-09-01 — clarification asked
Asked: What usable roof dimensions, cable-entry point, keep-outs, and allowed
height above the roof do we have, and may any microphones be mounted off-plane?
Answer: UNANSWERED — no CAD coordinate or cable length may be locked.
Impact: blocks the surveyed microphone coordinate set, enclosure anchors, and
cable/rail loss budget.

### Q2 — 2026-09-01 — clarification asked
Asked: Is the required output 2D bearing, 3D position, or only a focused audio
track; must it handle overlapping crows; and what localization error is useful?
Answer: UNANSWERED — proceeding only with a comparison study.
Impact: blocks the choice between eight perimeter microphones, a center/raised
reference allocation, and a sixteen-channel multiscale array.

### Q3 — 2026-09-01 — clarification asked
Asked: Where may the indoor hub and SELV supply live, what is the longest
home-run, is a keyed circular cable assembly acceptable, and what prototype
budget should the design target?
Answer: UNANSWERED — proceeding only with a module-first candidate.
Impact: blocks connector selection, power envelope, protection energy, board
outline, and sourcing lock.

### P1 — 2026-09-01 — user follow-up (verbatim)
> 1\) can you please make a table showing how dimension changes attributes of the array and makes things easier or harder?
> 2\) we want 3d position, or at least 3 position signature, we dont need to know where the crow is , but we do want to know which crow it is
> 3\) we can run a cat6 PoE cable up to the device. Do we need to have the device on USB or can we have it on PoE / ethernet only?

Impact: supersedes A1's blanket exclusion of individual identity, requests an
explicit dimensional study, partially constrains Q2, supplies one installation
fact relevant to Q3, and asks rather than decides the PoE/USB architecture.

### P2 — 2026-09-01 — parsed user requirement
Required: obtain a three-dimensional position or an explicitly defined
“3 position signature.”
Source: P1 item 2.
Impact: an exactly planar array is insufficient for the 3D branch; it may be
admissible for three known planar zones only if Q5 defines that fallback. The
required signature, overlap and error semantics remain Q5/Q2.

### P3 — 2026-09-01 — parsed user requirement
Required: determine which biological crow is calling; exact location is not the
desired user-facing result.
Source: P1 item 2.
Impact: source localization/tracking becomes an intermediate for isolation and
labelling, not the identity acceptance boundary. Q4 still owes the time span,
enrolment method and error limits.

### P4 — 2026-09-01 — user-provided installation fact and question
Available: one Cat6 PoE cable can run to the device. Asked: whether the external
device must use USB or can operate over PoE/Ethernet only.
Source: P1 item 3.
Impact: permits a networked roof-appliance option but does not select it.

### A6 — 2026-09-01 — interpretation of P3 (not yet accepted)
Assumed: persistent recognition of the same biological crow across positions or
days is the desired system goal. A stable anonymous acoustic track within an
encounter is required to isolate and label calls, but does not satisfy identity.
Authority: P3 prioritizes “which crow” over the displayed location.
Escalate if: only encounter-local `crow-A/crow-B` tracking is needed, or if no
camera/marked-bird evidence can be supplied for persistent identity.

### A7 — 2026-09-01 — proposed answer to P4 (not yet accepted)
Assumed: “PoE/Ethernet only” describes the single external building interface.
The candidate roof appliance may use a short internal USB 2.0 link from an
unchanged multichannel audio module to its Linux SBC; all audio channels are
sampled from one local clock before Ethernet packetization.
Authority: P4 makes Cat6 PoE available and asks whether USB is needed.
Escalate if: USB is forbidden anywhere inside the enclosure, not merely at the
building interface.

### A8 — 2026-09-01 — dimensional study boundary (not asked)
Assumed: no physical radius, height or coordinate is locked until Q1 is
answered. The addendum compares 0.5 m to 4 m outer radius and 0 m to 1 m
vertical baseline using 344 m/s and 48 ksample/s only as study assumptions.
Authority: P1 requests a table but supplies no roof envelope.
Escalate if: the usable roof envelope excludes those ranges.

### D1 — 2026-09-01 — agent synthesis (proposed, not accepted)
Proposed: compare 8/12/16-channel noncoplanar geometries after Q1/Q5; treat
spatial tracking as the isolation/labelling intermediate to P3's persistent
identity goal; and answer P4 with one external PoE/Ethernet roof appliance that
may contain a short internal USB audio link.
Authority: P1 requests an engineering comparison and permits a proposed answer.
Escalate if: the user accepts a specific geometry, requires zero USB anywhere,
or narrows “which crow” to encounter-local tracking.
Impact: creates ADR 0004/0005 and the addendum, but accepts no architecture,
coordinate, part, interface, power class or identity threshold.

### Q4 — 2026-09-01 — clarification asked
Asked: Does “which crow” mean a stable anonymous track during one encounter, or
the same biological individual across positions and days? If persistent, can a
camera or marked birds provide enrolment labels, and what false-match,
false-reject and unknown-class limits are acceptable?
Answer: UNANSWERED — P3 establishes the persistent-identity goal; A6 is only a
working interpretation of its time span, labelling and evidence boundary.
Impact: blocks the identity dataset, model, validation split and acceptance
thresholds; it does not block synchronized raw capture.

### Q5 — 2026-09-01 — clarification asked
Asked: Does “3 position signature” mean three known roof/perch zones, three
separate microphone clusters/viewpoints, or a three-dimensional TDOA vector?
Must two or more simultaneous crows receive separate identities?
Answer: UNANSWERED.
Impact: blocks the 8/12/16-channel allocation and multi-source validation.

### Q6 — 2026-09-01 — clarification asked
Asked: Is one external PoE/Ethernet cable sufficient while a short internal USB
link remains allowed, or is USB forbidden anywhere? What PSE/PoE type, maximum
Cat6 run, roof temperature/exposure and auxiliary loads are available?
Answer: UNANSWERED — A7 selects the lowest-risk candidate only.
Impact: blocks the PD, SBC, thermal, enclosure and exact power budget.

### P5 — 2026-09-01 — user follow-up (verbatim)
> i think we can do 8m radius! can we have the array be planar? identity needs to persist across recordings of 120s long , simultaneous crows do not need to be separated, short internal usb is acceptable

Impact: supplies a provisional radius, requests a planar feasibility answer,
bounds identity by 120-second recording files, removes simultaneous-source
separation from acceptance, and permits internal USB. It does not lock exact
coordinates, select the external architecture, or define the inter-recording
identity horizon.

### P6 — 2026-09-01 — user correction (verbatim)
> 8m diameter

Impact: supersedes only P5's dimensional phrase. The study envelope is 8 m in
diameter and 4 m in radius, still provisional until surveyed.

### A9 — 2026-09-01 — partial answer to Q1
User first proposed an 8 m radius in P5 and immediately corrected it to an 8 m
diameter/4 m radius in P6.
Disposition: treat 8 m diameter as an illustrative maximum-aperture study point,
not a locked coordinate or routed cable length, because “I think” and the usable
roof polygon, entry route and keep-outs remain unverified.

### A10 — 2026-09-01 — partial answer to Q4
User requires identity to persist across distinct recordings that are each 120
seconds long.
Disposition: whole recordings, not calls cut from the same recording, are the
minimum indivisible identity-validation unit. Consecutive files from one
encounter/visit must stay in the same split; Q7 still owes the grouping horizon.
The inter-recording gap, total identity horizon and required invariance to
changed position remain unanswered.

### A11 — 2026-09-01 — partial answer to Q2/Q5
User does not require simultaneous crows to be separated.
Disposition: overlapping-call events may return `unresolved` or be excluded
from the identity claim, but raw synchronized channels and the unresolved/
excluded rate must still be retained and reported.

### A12 — 2026-09-01 — partial answer to Q6
User explicitly permits a short internal USB link.
Disposition: this closes only the internal-USB subquestion. The external
PoE/Ethernet roof-appliance architecture and its power/environment facts remain
proposed and unaccepted.

### D2 — 2026-09-01 — agent feasibility answer (proposed, not accepted)
Proposed: a planar array is feasible for a calibrated planar/multi-position
signature and single-active-caller spatial filtering; it cannot claim robust 3D
elevation. Study an eight-channel seven-outer-plus-center layout at a nominal
4 m outer radius/8 m diameter alongside smaller/multiscale layouts. Lock no
radius, channel count or coordinate before the roof survey and acoustic
simulation.
Authority: P5 requests a feasibility answer and removes simultaneous-source
separation from acceptance.
Escalate if: elevation becomes required, overlap must be separated, or the
survey cannot close the proposed aperture and cable routes.

### Q7 — 2026-09-01 — clarification asked
Asked: Are the 120-second recordings consecutive file chunks from one
continuous encounter, or independently started sessions/visits? What maximum
gap must preserve identity, and must identity survive the crow moving to
another perch?
Answer: UNANSWERED.
Impact: distinguishes carrying a spatial track across file boundaries from a
persistent biological voice classifier and defines the leakage-safe holdout.

### P7 — 2026-09-01 — user clarification (verbatim)
> must recognition persist only across consecutive 120-second files, or across separate visits/hours/days and different perches? - no , it must only persist in the 120 second file if the crow does not move much

Impact: answers Q4/Q7 and supersedes P5/A10's cross-recording interpretation.
Recognition is required only within one 120-second file while the source is
approximately stationary. Cross-file, cross-visit, cross-day and changed-perch
biological identity are not required.

### A13 — 2026-09-01 — conservative interpretation of P7 (not asked)
Assumed: expose an anonymous source label such as `caller-A`, not a biological
identity. The label expires at file end and is reinitialized or becomes
`unknown` when measured motion, overlap or low confidence breaks the calibrated
stationarity gate. The numeric gate is derived from held-out acoustic tests,
not silently equated to one fixed distance.
Authority: P7 restricts recognition to one file and conditions it on little
movement.
Escalate if: the same label must survive substantial movement within the file,
or two sequential crows at the same perch must be biologically distinguished.

### P8 — 2026-09-01 — user directive (verbatim)
> Great sounds good lets use the rpi5 with this, please continue design!

Impact: selects the Raspberry Pi 5 platform for the roof-appliance Linux host,
accepts the immediately preceding one-external-PoE/Ethernet plus short-internal-
USB system boundary, and authorizes continued design work. It does not lock an
exact Pi SKU, roof coordinate, PoE implementation, connector, mechanical stack,
power budget, storage device, cooler, enclosure or validation threshold.

### A14 — 2026-09-01 — Raspberry Pi 5 selection boundary (not asked)
Assumed: “rpi5” selects the Raspberry Pi 5 Model B platform, not an exact RAM
capacity, board revision, storage device, cooler, PoE accessory, carrier or
enclosure. The Pi is the Linux recorder/network bridge; the shared local audio
clock remains the acoustic timing authority and Ethernet arrival time is never
used for TDOA.
Authority: P8 explicitly selects the host platform and accepts the preceding
network-boundary explanation.
Escalate if: the intended device is Compute Module 5, a specific Pi 5 SKU, or a
direct-TDM/GPIO implementation rather than the current USB-audio candidate.

### P9 — 2026-09-01 — user directive (verbatim)
> Great! Lets make a new branch for this board dev, and lets finish the board and get a release ready

Impact: authorizes a dedicated board-development branch and changes the PCB
delivery target from design/layout seal to an immutable reviewed release. It
does not itself authorize an order, claim a fabricated first article, relax
physical evidence, or request project-authored firmware.

### A15 — 2026-09-01 — release-target boundary (not asked)
Assumed: “release ready” means a sealed, self-contained PCB release candidate
that may remain `DO-NOT-ORDER` when live allocation, uploader, physical fit or
first-article evidence is still owed. It does not mean production authorized.
Authority: P9 explicitly requests a release while the PCB lifecycle separates
release, order, first article and production claims.
Escalate if: this turn must include placing an actual fabrication/assembly
order or production authorization rather than preparing the release.

### A16 — 2026-09-01 — single-board release partition (not asked)
Assumed: the user's release request applies to the custom boards required by
the array, not to falsely promoting the whole roof appliance before physical
tests. This parent remains the system-integration record; the central carrier
and replicated microphone pod receive separate single-board release projects.
Authority: P9 authorizes board development, while the repository contract and
the discovered archived pin-map short require independently governed boards
with one shared cable contract.
Escalate if: both PCBs must instead share one coupled fabrication/release
identity, despite their different stackups, quantities and verification gates.

### A17 — 2026-09-01 — single eight-channel ADC selection (not asked)
Assumed: minimizing unsynchronized conversion domains and avoiding custom
initialization firmware are more important than using a JLC-stocked ADC in the
first design candidate. Select one hardware-controlled CS5308P for all eight
channels and keep the release `DO-NOT-ORDER` until its consignment/assembly and
MCHStreamer interoperability are proved.
Authority: P9 delegates board completion; A2/A3 require one shared sampling
clock and forbid project-authored embedded firmware. Primary-source review
found the earlier four-TAA5242 hardware chain invalid and the CS5308P TDM8
framing an exact match for the selected MCHStreamer clock ratios.
Escalate if: JLC turnkey assembly is mandatory for the first carrier revision,
or a small configuration processor and its firmware are acceptable.

### D3 — 2026-09-12 — user directive

> Great lets do it!

Context: approval of the proposal to replace the Micro-Fit spoke terminations
with RJ45 ports and commercially preterminated shielded Cat6 patch cords.
Synchronize the parent, carrier and pod interface contracts. Preserve balanced
analog audio and 12 V power, 15 m design length, 0.10 A continuous per pod,
voltage-drop limits and outdoor service requirements. Ethernet and PoE remain
false. Source and downstream release gates must be renewed for the changed
interface. Existing sealed releases remain immutable; no purchase or push is
authorized by this directive.

## Decision register

| id | decision | decided by | depth |
|---|---|---|---|
| 0000 | Keep the scaffold's validated ADR format example. | agent (scaffold) | [format reference](decisions/0000-example-adr.md) |
| 0001 | Use central shared-clock conversion of balanced analog home runs. | agent (A3 / P9 delegation) | [accepted ADR](decisions/0001-shared-clock-analog-star.md) |
| 0002 | Historical noncoplanar channel-count study, superseded by the planar branch in 0006. | agent (A5/P2; superseded by P5/P6) | [superseded ADR](decisions/0002-eight-channel-first-article.md) |
| 0003 | Historical keyed-circular proposal; its anti-RJ45 and entry-safety boundary survives in 0011. | agent (A4; superseded by A16) | [superseded ADR](decisions/0003-keyed-outdoor-interface.md) |
| 0004 | Historical persistent-biological-identity proposal, superseded by the within-file track boundary in 0007. | agent (P3/A6; superseded by P7) | [superseded ADR](decisions/0004-individual-identity-evidence-boundary.md) |
| 0005 | Use one external PoE/Ethernet roof-appliance uplink with an allowed internal USB audio link. | user (P8; initial proposal P4/A7) | [accepted ADR](decisions/0005-poe-ethernet-roof-appliance.md) |
| 0006 | Use a planar eight-channel 8 m-diameter v1 target for the single-active-caller signature branch. | user (P5/P6; implemented under P9) | [accepted ADR](decisions/0006-planar-signature-versus-3d.md) |
| 0007 | Limit recognition to one stationary-source track within each 120-second file. | user (P7; implemented under P9) | [accepted ADR](decisions/0007-within-file-stationary-caller-track.md) |
| 0008 | Use Raspberry Pi 5 Model B as the roof-appliance Linux host; leave SKU, storage, cooling and PoE implementation open. | user (P8 / A14 boundary) | [accepted ADR](decisions/0008-raspberry-pi-5-roof-appliance-host.md) |
| 0009 | Keep this project as the system authority and release the central carrier and microphone pod as separate single-board projects. | agent (A16 / P9 delegation) | [accepted ADR](decisions/0009-split-system-into-two-single-board-releases.md) |
| 0010 | Use one hardware-controlled CS5308P for all eight synchronized conversion channels and one MCHStreamer TDM8 lane. | agent (A17 / P9 delegation) | [accepted ADR](decisions/0010-single-cs5308p-audio-carrier.md) |
| 0011 | Terminate uninterrupted spoke cables on internal Micro-Fit headers behind sealed cable glands; no spoke is RJ45/PoE. | agent (A16 / P9 delegation) | [accepted ADR](decisions/0011-internal-microfit-cable-gland-spokes.md) |

## Spec tensions (D-SPEC — commission remains open)

| # | Requirement | Standard / parts cap it exceeds | Resolution (ADR) | User flagged |
|---|---|---|---|---|
| T1 | “Which crow” initially appeared to require biological identity. | Position identifies a source track, not necessarily the same biological bird after it moves or returns. | [0007](decisions/0007-within-file-stationary-caller-track.md): expose only a within-file stationary-source label; no cross-file biometric claim. | yes — P3/P7/Q7 |
| T2 | A visually perfect star suggests uniformly spaced microphones. | Wide microphone spacing aliases at upper crow-call frequencies and periodic geometry creates ambiguous sidelobes. | [0006](decisions/0006-planar-signature-versus-3d.md): star wiring, surveyed mildly nonperiodic acoustic positions and broadband delay evidence. | yes — Q1/Q2/P5/P6 |
| T3 | A single Cat6 powers and networks the Raspberry Pi 5 roof appliance. | Rooftop copper still crosses weather, surge, ESD, lightning, bonding and building-entry boundaries no PCB-only claim can close; the listed Pi 3B+/4 PoE+ HAT is not a Pi 5 mechanical authority. | [0005](decisions/0005-poe-ethernet-roof-appliance.md) and [0008](decisions/0008-raspberry-pi-5-roof-appliance-host.md): accepted external topology and host platform; [0011](decisions/0011-internal-microfit-cable-gland-spokes.md): distinct analog spokes behind sealed glands. | yes — P4/P8/Q1/Q3/Q6 |
| T4 | The user prefers a planar study but earlier requested 3D or a position signature. | A planar array can supply a calibrated planar signature/2D track but cannot close elevation or robust 3D. | [0006](decisions/0006-planar-signature-versus-3d.md): planar signature branch only; no 3D claim. | yes — P2/P5/Q5 |

## Mating fact-lock (D-MATE — OPEN)

No foreign dimension has been consumed by CAD. The following facts are OWED;
the scaffolded `mates.yaml` remains an unadopted example and floorplanning is
forbidden until each selected device has one graded `external_hardware/`
record and matching machine reference.

| Fact (`external_hardware/<device>` id) | Grade | Error bar | Where it is spent | Mating budget it is spent against |
|---|---|---|---|---|
| usable-roof-coordinate-envelope | OWED | — | microphone positions and cable lengths | P6 supplies an 8 m-diameter/4 m-radius study point; Q1 still owes polygon, route and keep-outs |
| roof-appliance-mounting-envelope | OWED | — | central carrier, SBC, PD and enclosure | Q1/Q3/Q6 service, thermal and weather clearance |
| usb-audio-module-header-and-mounts | OWED | — | central carrier header/floorplan | vendor connector and standoff tolerance stack |
| raspberry-pi-5-usb-ethernet-and-mounts | OWED | — | internal USB/network compute floorplan | P8/A14 platform selected; current official STEP, physical sample, cable, cooler, storage and service stack still owed |
| poe-uplink-assembly-envelope | OWED | — | building-facing connector, shield, PD and enclosure | P4/Q6 mate, seal, grip, bend, surge and thermal stack |
| poe-pd-module-envelope | OWED | — | central power tree and carrier outline | Q6 input class, isolation, derating and peak-load budget |
| outdoor-cable-assembly-envelope | OWED | — | pod/central connector cell and enclosure | sealing, grip, bend, service, and mate clearance |

## Commission fact-lock (D-SPEC — accepted boundaries and explicitly owed facts)

| Fact | Value | Locked by |
|---|---|---|
| Output rail(s): Vout min-max @ Imax | Carrier spoke plane is 10.8–13.2 V with 100 mA maximum continuous pod current; each pod derives a quiet local 5 V rail. Cable drop, hot-corner protection and the exact converters remain child release obligations. | A3, A16, 0011 |
| External outputs: connector count + simultaneous count | Exactly eight pod ports and eight simultaneous recorded channels for v1. Seven perimeter microphones plus one center reference are the leading planar study; no 12/16-channel compatibility claim. | P5, P6, P9, A16 |
| Duty: continuous and peak current/time | Recording file length is 120 s; cross-file identity is not required. Cadence, retention/ring buffer, pod and calibration-load current envelopes are OWED. | P5, P7, A13, Q3 |
| Measurement plane + included/excluded path elements | Acoustic plane: eight surveyed microphone membranes. Digital plane: eight raw PCM channels at the roof appliance. Includes pod, cable, ADC and local clock; excludes unvalidated host track assignment and any biological-identity inference. | A2, A3, P5, P7, A13 |
| Input envelope: Vin min-max, source type | Accepted external source: one standards-compliant IEEE PoE/Ethernet uplink. Exact PSE/PD type, cable corner, USB-C power advertisement, conversion loss and auxiliary-load margin are OWED; Type 2 versus Type 3 remains a measured power-budget decision. | P4, P8, A14, Q3, Q6 |
| Protection posture (defended failures + escalation boundary) | Per-port current limiting, polarity/overvoltage defense, cable ESD/surge and shield strategy are required; lightning/building-entry protection requires qualified review and is not delegated to the PCB. | A4, Q1, Q3 |
| Off-control / storage (how it de-energizes; quiescent budget) | Disable/unplug the indoor PSE port; no battery assumed; PD off-state and stored-energy budgets are OWED. | A2, A7, Q3, Q6 |
| Hard-cell parts (spec-critical functions): sourcing class a/b/c | Raspberry Pi 5 Model B is user-selected as a self-supplied module; exact RAM/SKU remains OWED. MCHStreamer TDM8 and one CS5308P-DN are selected for the carrier, but the vendor image, module sample and ADC consignment/manual-assembly path remain OWED. PoE PD, storage, microphone capsule, cable glands and chassis-bond hardware remain system/child-project selections. | P8, A14, A17, 0010, 0011 |
| Integration posture (modules preferred; bare-IC exceptions) | Raspberry Pi 5 Model B is the accepted Linux-host module and a short internal USB link is user-permitted. Vendor USB-audio and PoE modules are preferred; ADC and analog front end may be bare ICs after dossiers and interface proof. The Linux capture/streaming application is outside PCB firmware. No custom embedded firmware exception is authorized. | P8, A14, A2, A3, A7, P5, A12 |


### 2026-09-12 — user-directed Cat cable change

User: “can we use cat cable instead of custom cable to run to pods?”
After the two termination options were explained, user: “Great! lets do it!”
Implementation assumption announced: outdoor shielded Cat5e bulk cable with
the existing Micro-Fit PCB connectors. The approval does not specifically
select RJ45; no RJ45, Ethernet or PoE conversion is inferred. See parent
ADR0012. All8 audio/power pairs and board pin identities remain unchanged;
only the prospective harness and its qualification contract change.


## 2026-09-13 — single-side SMD assembly directive

> Can we please make sure all SMD components are from one side? it will be tricky and costly to assign from both sides. We can expand the board a bit in size if tha thelps

Current requirement: all fitted SMD components on the top (F.Cu) side of both
carrier and pod, including consigned or manually fitted SMD parts. Board growth
is authorized where needed for placement, soldering and rework access.
Implementation and regenerated layout acceptance remain pending.
