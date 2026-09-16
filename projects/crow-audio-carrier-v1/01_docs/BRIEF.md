# brief: crow-audio-carrier-v1

status: in-progress
prompt_sha256: a6fcb7d5b8465bc23415c7d5f9381b368f12d69455da135d8b6b0b1cb89965b3
current_release: 07_releases/v0.1.7-2026-09-16
order_status: FIRST-ARTICLE ORDER AUTHORIZED — UPLOADER CHECK REQUIRED

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

A reviewable, regenerable first-article carrier PCB source exists for eight
phase-coherent microphone channels. One ADC and one external clock domain map
the eight active-balanced spokes to deterministic TDM8 slots for the off-board
MCHStreamer and Raspberry Pi 5 roof appliance. The carrier implements the
vendor input, reset and independent-power requirements in hardware and
preserves the shared spoke contract. A release may be staged only after the
exact schematic, layout and fabrication gates pass. Prototype ordering requires
separate authorization and final sourcing/upload checks; physical validation
follows fabrication under D6 / ADR-0007, before a tested or production claim.

| # | Criterion | Source | Status |
|---|---|---|---|
| G1 | Logical pods 1–8 map to physical ADC4,3,2,1,5,6,7,8; slots 0–7 carry pods4,3,2,1,5,6,7,8 under ADR0027 on exact reviewed artifacts. | A2, A3 | unmet |
| G2 | All channels share one CS5308P clocked by the MCHStreamer at 48 kHz, 24.576 MHz MCLK, 12.288 MHz BCLK and eight 32-bit TDM slots; independent power states fail quiet. | A2, A4 | unmet |
| G3 | Every receive channel realizes the Cirrus-derived unity/filter topology with ADR0025 shared-rail OPA2320, grounded filter shunts and two passive external VMID domains; exact review and bench qualification pass. | A2 | unmet |
| G4 | ADC reset performs high, waits at least 2 ms, pulses low at least 1 ms and returns high without project-authored firmware. | A2 | unmet |
| G5 | Eight exact Würth 615008160221 RJ45 spoke jacks implement the shared pin identity and deliver at least 10.8 V at 0.10 A per port with all eight loaded and one-fault/seven-healthy behavior qualified. | A3, A5 | unmet |
| G6 | Pi, PoE/Ethernet, USB data and the MCHStreamer remain off this PCB. | D1, D4, A1 | met — [architecture boundary](ARCHITECTURE.md) |
| G7 | Keep prototype design, order authorization, first-article testing and outdoor production acceptance separate; retain every unresolved hold at its proper boundary. | D5, D6, A5 | met — [prototype acceptance boundaries](decisions/0007-prototype-before-physical-qualification.md) |

G1–G5 include both design obligations and hardware validation. They remain
unmet at whole-system scope until measured; a prototype design release must
close their source/layout obligations and explicitly retain their bench clauses
in the first-article plan. An unmet hardware clause is not permission to ship a
known electrical defect, nor a reason to require a prototype before making it.

## Log

### D1 — 2026-09-01 — user directive
> i think we can do 8m radius! can we have the array be planar? identity needs to persist across recordings of 120s long , simultaneous crows do not need to be separated, short internal usb is acceptable

Impact: permits a planar array and short internal USB, removes simultaneous-
source separation from acceptance and supplies a provisional size later
corrected by D2.

### D2 — 2026-09-01 — user directive
> 8m diameter

Impact: corrects only D1's array dimension to 8 m diameter / 4 m radius.

### D3 — 2026-09-01 — user directive
> must recognition persist only across consecutive 120-second files, or across separate visits/hours/days and different perches? - no , it must only persist in the 120 second file if the crow does not move much

Impact: limits identity to an anonymous stationary-source signature within one
120-second recording; no cross-file or changed-perch identity is required.

### D4 — 2026-09-01 — user directive
> Great sounds good lets use the rpi5 with this, please continue design!

Impact: selects Raspberry Pi 5 as the roof-appliance host and authorizes
continued design under the accepted network plus short-internal-USB boundary.

### D5 — 2026-09-01 — user directive
> Great! Lets make a new branch for this board dev, and lets finish the board and get a release ready

Impact: authorizes the board-development branch and a governed release target;
it does not authorize ordering, production or fabricated-hardware claims.

### D6 — 2026-09-07 — user directive
> This is great news! lets keep going

Context: the user accepted proceeding from public manufacturer information to
documented design checks, completed layout and a prototype release, with
physical qualification on the first assembled board and the coupon optional.
Impact: supersedes mandatory pre-route physical qualification and the circular
first-article-tests-before-prototype-order assumption; retains all electrical,
geometry, review, sourcing and separate purchase-authorization requirements.

### A1 — 2026-09-01 — assumption (not asked)
Assumed: PoE/Ethernet, Raspberry Pi 5, storage, USB data and the USB-powered
MCHStreamer are COTS elements outside this PCB; only the short TDM/presence
cables cross the carrier boundary.
Authority: D1 and D4 delegate implementation of the accepted roof-appliance
architecture.
Escalate if: the carrier must itself implement PoE, Ethernet, USB or Pi mating.

### A2 — 2026-09-01 — assumption (not asked)
Assumed: one hardware-controlled CS5308P provides all eight synchronous ADC
channels, using the Cirrus-recommended eight-channel receive network, buffered
VMID, hardware reset sequence and one MCHStreamer-mastered TDM8 lane.
Authority: P delegates the electrical architecture and D5 requests completion.
Escalate if: a different ADC, multiple clock domains or project-authored
configuration firmware is acceptable.

### A3 — 2026-09-01 — assumption (not asked)
Assumed: the carrier implements the shared straight-through four-wire spoke
contract on eight exact Molex `43650-0400` headers: pin 1 +12V_POD, pin 2 GND,
pin 3 AUDIO+, pin 4 AUDIO−, with 0.10 A continuous available per pod.
Authority: the parent system partition delegates the child-board interface.
Escalate if: spoke connector, pin identity, output count or current changes.

### A4 — 2026-09-01 — assumption (not asked)
Assumed: MCHStreamer J3 presence sense and Ioff-capable clock/data buffers keep
carrier and USB/MCH power domains independent; two exact Samtec cables are used
and split/disconnected cases fail quiet.
Authority: A1/A2 require an off-board, independently powered TDM clock master.
Escalate if: the MCHStreamer is instead powered by the carrier or its exact
hardware/image cannot be acquired.

### A5 — 2026-09-01 — assumption (not asked)
Assumed: J9 accepts a protected, isolated regulated 11.4–13.2 V COTS source and
uses an input PPTC plus reverse-hookup PFET; eight branch PPTCs protect spoke
cables. The candidate stays DO-NOT-ORDER until hot drop, fault selectivity,
connector fit, reset/TDM/analog and roof-environment tests pass.
Authority: D5 delegates first-article engineering but not order authorization.
Escalate if: the source/protection boundary or release-risk posture changes.

Update under D6: the preceding test-before-order timing is superseded by
ADR-0007. The protected isolated source and all test obligations are unchanged.

### D7 — 2026-09-10 — user directive
> please verify public stock and contunue

Context: response to the explicit request to admit verified distributor stock
for the exact regulator for design work only, retaining JLC assembly and
purchase approvals before ordering. Impact: authorizes ADR0026's narrow
public-distributor pre-layout path. It does not authorize a part substitution,
purchase, quote submission, allocation claim or order.

### D8 — 2026-09-12 — user directive

> Great lets do it!

Context: the user approved the immediately preceding proposal to replace the
spoke Micro-Fit terminations with RJ45 ports and commercially preterminated
shielded Cat6 patch cords. This supersedes the earlier Cat5e/Micro-Fit
implementation assumption. Implement the same eight-contact assignment on the
carrier and pod, with the parent interface kept synchronized. The approved
function remains balanced analog audio and 12 V power; Ethernet and PoE remain
false. Preserve the 15 m design length, 0.10 A per pod, voltage-drop envelope,
and existing outdoor service requirements while selecting exact parts.
Source, schematic, placement and downstream acceptance must be renewed for
this material interface revision. No order or push authority is implied.

### D9 — 2026-09-16 — user directive

> Can you please make a list and review, we would like to get the board ordered today,
>
> Oh great thats not too bad. lets go through the list and address all changes required for ordering in this release/pass

Impact: authorizes preparation and purchase of the governed first-article lot
after the exact release upload, fabrication selections, BOM mapping, placement
preview and selective via-process checks pass. This does not authorize part
substitutions or a production/deployment claim. ADR0032 freezes the order
profile and preserves physical qualification as post-delivery work.

## Decision register

| id | decision | decided by | depth |
|---|---|---|---|
| 0001 | Use one hardware-mode CS5308P for synchronous eight-channel TDM8 conversion. | agent (A2 / P-delegation) | [architecture ADR](decisions/0001-single-cs5308p-tdm8.md) |
| 0002 | Generate the required high-delay-low-high ADC reset entirely in hardware. | agent (A2 / P-delegation) | [electrical ADR](decisions/0002-hardware-reset-pulse.md) |
| 0003 | Accept isolated 12 V through protected J9 and distribute eight independently protected spoke rails. | agent (A3, A5 / P-delegation) | [power/protection ADR](decisions/0003-power-and-spoke-boundary.md) |
| 0004 | Implement the Cirrus AN0556 Figure 2 receive cell and buffered VMID network. | agent (A2 / P-delegation) | [analog ADR](decisions/0004-cirrus-input-buffer.md) |
| 0005 | Use J3 presence sense plus Ioff buffers for the independently powered MCHStreamer boundary. | agent (A1, A4 / P-delegation) | [digital/power-domain ADR](decisions/0005-mch-power-domain-boundary.md) |
| 0006 | Permit design-only continuation from an exact-code public catalog screen while keeping authenticated JLC allocation mandatory for order readiness. | agent (A5 / D5-delegation) | [sourcing-boundary ADR](decisions/0006-public-catalog-prelayout-only.md) |
| 0007 | Admit documented prototype design before physical qualification; retain source/geometry/release checks and later hardware acceptance. | user (D6) | [prototype-boundary ADR](decisions/0007-prototype-before-physical-qualification.md) |
| 0017 | Correct analog/reference routing-mask overreach while retaining switching exclusion. | agent (A2 / P-delegation) | [routing-keepout ADR](decisions/0017-analog-routing-keepout.md) |
| 0018 | Reserve sixteen full-width ADC analog launches after correcting adjacent filter/reset fanout. | agent (A2 / P-delegation) | [ADC fanout ADR](decisions/0018-adc-analog-launches.md) |
| 0022 | Isolate buck VIN/EN and all local VIN ceramics from the shared spoke bus; unchanged supply/spoke/signal envelope. | agent (A2/A3/A5 / P-delegation) | [buck reverse-port ADR](decisions/0022-buck-input-reverse-isolation.md) |
| 0023 | Adopt OPA2320 on existing5V_OPA with retained-reference current limiters; source engineering acceptance remains open and the signal/spoke envelope is unchanged. | agent (A2/A5 / P-delegation), fresh source-part review | [amplifier/protection ADR](decisions/0023-opa2320-reference-protection.md) |
| 0024 | Reuse existing precision10k resistors for the four external-reference divider positions; preserve nominal bias, signal/spoke envelope and first-article limits. | agent (A2/A5 / P-delegation) | [reference-divider ADR](decisions/0024-precision-reference-dividers.md) |
| 0019 | Declare exact post-buffer P/N endpoint matching and a conditional saved-copper resistance screen; retain physical qualification. | agent (A2 / P-delegation) | [analog-path ADR](decisions/0019-analog-path-matching.md) |
| 0026 | Admit exact regulator distributor stock for design-only progression, with all JLC and purchase gates retained. | user (D7) | [design-only sourcing ADR](decisions/0026-exact-distributor-design-only.md) |
| 0008 | External hardware-mode VMID and direct reference returns | agent (P-delegation; existing ADR) | [existing decision](decisions/0008-external-vmid-and-reference-returns.md) |
| 0009 | quiet LDO, held energy and break-before-discharge analog boundary | agent (P-delegation; existing ADR) | [existing decision](decisions/0009-held-power-and-analog-isolation.md) |
| 0010 | exact route ownership, public stack and bounded ADC launches | agent (P-delegation; existing ADR) | [existing decision](decisions/0010-route-stack-and-current-paths.md) |
| 0011 | bounded digital pin launches and exact FSYNC ownership | agent (P-delegation; existing ADR) | [existing decision](decisions/0011-digital-pin-launches.md) |
| 0012 | 0012 — native regulator exits and a reserved quiet-return source cell | agent (P-delegation; existing ADR) | [existing decision](decisions/0012-regulator-source-exits.md) |
| 0013 | 0013 — bounded ADC supply, reference and configuration exits | agent (P-delegation; existing ADR) | [existing decision](decisions/0013-adc-source-exits.md) |
| 0014 | 0014 — bounded peripheral power entries | agent (P-delegation; existing ADR) | [existing decision](decisions/0014-peripheral-power-entries.md) |
| 0015 | 0015 — bounded west ADC feeds with retained return topology | agent (P-delegation; existing ADR) | [existing decision](decisions/0015-adc-supply-feeds.md) |
| 0016 | 0016 — explicit ADC thermal vias and a disjoint fabrication process | agent (P-delegation; existing ADR) | [existing decision](decisions/0016-adc-thermal-via-process.md) |
| 0020 | 0020 — Pad-only clearance scopes for retained package lands | agent (P-delegation; existing ADR) | [existing decision](decisions/0020-package-pad-clearances.md) |
| 0021 | Connected-start input current limits and damped OPA supply | agent (P-delegation; existing ADR) | [existing decision](decisions/0021-connected-start-input-current-limits.md) |
| 0025 | shared ADC/amplifier rail with passive external bias | agent (P-delegation; existing ADR) | [existing decision](decisions/0025-shared-rail-protection-architecture.md) |
| 0032 | Freeze the five-board carrier first-article fabrication and assembly order profile. | user (D9) | [order-profile ADR](decisions/0032-first-article-order-profile.md) |

## Spec tensions

| id | requirement | standard/part cap | how honoured | ADR | user-flagged |
|---|---|---|---|---|---|
| T1 | Eight phase-coherent channels without custom embedded firmware. | Multiple stereo ADCs add clock/configuration state; no reviewed module exposes eight analog spokes plus the required TDM8 boundary. | Use one hardware-mode CS5308P and keep its bare-IC responsibilities explicit. | [0001](decisions/0001-single-cs5308p-tdm8.md) | yes — first-article hold |
| T2 | CS5308P high→delay→low→high reset sequence. | An ordinary low-to-high POR cannot meet the vendor sequence, and the monostable has no guaranteed minimum pulse for the selected timing network. | Supervisor, monostable and NMOS generate the sequence; oscilloscope qualification is required for first-article acceptance under D6. | [0002](decisions/0002-hardware-reset-pulse.md) | yes — first-article hold |
| T3 | 0.10 A pod load with resettable per-port protection. | A thermal PPTC is not a precision limiter; its hot hold, trip time and post-trip resistance constrain drop and fault energy. | Exact 1812L035/60MR branches retain cited hot hold margin; hot drop, source fault and selectivity are measured. | [0003](decisions/0003-power-and-spoke-boundary.md) | yes — first-article hold |
| T4 | 1.2 Vrms differential pod signal into a 2.0 Vrms ADC. | The 4.85 V OPA rail floor constrains guaranteed OPA1656 common-mode range before ADC full scale. | Cap the shared interface at 1.2 Vrms and qualify VMID, headroom and distortion with known stimuli. | [0004](decisions/0004-cirrus-input-buffer.md) | yes — first-article hold |
| T5 | Full eight-spoke load at roof temperature. | The rejected 1812L110/33 input PPTC held only 0.63 A at 70 °C, below the load allocation. | Use 2920L260/33 with 1.60 A cited hold at 70 °C; retain all-eight hot load/drop testing. | [0003](decisions/0003-power-and-spoke-boundary.md) | yes — first-article hold |
| T6 | Survive accidental J9 polarity reversal. | Fuse plus shunt TVS does not block a sustained reverse connection. | Use a DMP6023LFG PFET reverse-hookup stage with gate clamp. | [0003](decisions/0003-power-and-spoke-boundary.md) | yes — source review |
| T7 | MCHStreamer may be powered while the carrier is off, and vice versa. | Unprotected logic lines can back-power either domain or create false clocks. | J3 presence sense and Ioff-capable input/output buffers implement four explicit power states. | [0005](decisions/0005-mch-power-domain-boundary.md) | yes — first-article hold |

2026-09-09 T4 implementation annotation: ADR0023 replaces the OPA1656 with
OPA2320 and corrects reference-current paths. The historical origin of T4
above is preserved; its1.2Vrms envelope is unchanged. Filter performance,
reference acceptance and all-state protection are not closed by substitution.

## Mating fact-lock

The eight pod connectors are governed by the shared parent contract. The MCHStreamer pinout is CITED from its user manual and the short interconnect is selected as two exact Samtec `TCSD-06-D-04.50-01` assemblies. Because miniDSP does not publish its board-header MPN, module-side post fit, pin-1 orientation, cable continuity, and hot-plug/power ordering remain first-article holds. The exact miniDSP-authorized TDM8 image is available only through the purchaser/dealer download workflow; its original bytes, SHA-256, updater version, load evidence and module readback are an additional COTS acquisition hold, not project-authored firmware. No physical Pi or Ethernet mating occurs on this PCB.

| Fact (`external_hardware/minidsp_mchstreamer`) | Grade | Error bar | Where it is spent | Mating budget it is spent against |
|---|---|---|---|---|
| `tdm8_header_pinout` | CITED | — | J10 signal pins and ADC/TDM rules | User-manual J1 pin identity |
| `tdm8_clock_master_48k` | CITED | — | U_CLK and CS5308P mode/clock rules | 48 kHz TDM8 framing |
| `j3_presence_supply` | CITED | — | J11 pins 1–2 and presence-only sense | MCH/carrier independent-power boundary |
| `header_key_and_pin1_orientation` | OWED | — | J10/J11, both exact cables and service operation | Module post fit, seating, rotation, continuity and retention |
| `tdm8_firmware_image_identity` | OWED | — | COTS module configuration and first-article readback | Authorized image/package digest and repeatable TDM8 state |

## Commission fact-lock

| Fact | Value | Locked by |
|---|---|---|
| External outputs | Eight spokes; all eight operate simultaneously. | A3 |
| Spoke supply | 12.0 V nominal, 10.8–13.2 V at each carrier output header and at least 10.5 V at the pod header after qualified maximum cable drop; 0.10 A continuous per pod. | A3, A5 |
| Measurement plane | Carrier RJ45 output jack; includes input protection, branch PTC, copper/joints and header contacts; excludes mated contacts, cable and pod. | A3 |
| Input envelope | Protected, isolated regulated 12 V COTS source; 11.4–13.2 V at J9. | A5 |
| Protection posture | Input PPTC/TVS/reverse-hookup defense and independently protected spokes; direct lightning and building-code protection remain upstream/system obligations. | A5 |
| Off control / storage | Unplug or de-energize the external isolated 12 V source; no stored-energy source on carrier. | A1, A5 |
| Audio interface | Active-balanced analog, 2.5 V nominal pod common mode, 1.2 Vrms differential maximum at the carrier connector. | A3 |
| Digital interface | MCHStreamer TDM8 clock master; 3.3 V, 48 kHz, eight 32-bit slots; J3 pin 2 is about 0.320 mA presence sense only. | A2, A4 |
| Integration posture | Off-board Pi/PoE/USB/MCH modules are preferred; bare CS5308P is the deliberate exception because no reviewed module meets the eight-spoke plus TDM8 contract. | A1, A2 |


### 2026-09-12 — user-directed Cat cable change

User: “can we use cat cable instead of custom cable to run to pods?”
After the two termination options were explained, user: “Great! lets do it!”
Implementation assumption announced: outdoor shielded Cat5e bulk cable with
the existing Micro-Fit PCB connectors. The approval does not specifically
select RJ45; no RJ45, Ethernet or PoE conversion is inferred. See parent
ADR0012. All8 audio/power pairs and board pin identities remain unchanged;
only the prospective harness and its qualification contract change.

## 2026-09-12 — G1 implementation identity under A2

ADR0027 freezes pod1..8 to physical ADC4,3,2,1,5,6,7,8 and slots3,2,1,0,4,5,6,7.
G1 remains deterministic; connectors, signal polarity, COTS image and hardware
mode are unchanged. The exact map ID/digest and surveyed pod-coordinate binding
must accompany capture records; bench slot qualification remains owed.


## 2026-09-13 — single-side SMD assembly directive

> Can we please make sure all SMD components are from one side? it will be tricky and costly to assign from both sides. We can expand the board a bit in size if tha thelps

Current requirement: all fitted SMD components on the top (F.Cu) side of both
carrier and pod, including consigned or manually fitted SMD parts. Board growth
is authorized where needed for placement, soldering and rework access.
Implementation and regenerated layout acceptance remain pending.


## 2026-09-15T16:43:13.024171+00:00 — publication and board-view directives

User follow-up: please commit and push the newest Crow board files and the latest board rendering to the prompt2device remote main branch. Verify the intended Crow project files, preserve unrelated work, and report the commit hash and push result here.

Additional user request: include and push angled perspective renderings of the Crow board that clearly show the Ethernet/RJ45 connectors. Prefer useful front-left/front-right oblique views (and rear oblique if needed for connector visibility), use the latest exact board state, keep renders reproducible and board-bound, and include them in the same reviewed origin/main publication if all gates pass.
