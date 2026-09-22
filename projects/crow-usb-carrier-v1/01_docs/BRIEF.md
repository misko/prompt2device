# brief: crow-usb-carrier-v1

status: draft
prompt_sha256: 5b4bf606a77fbfb700f834caf36af9b33d23c14a249a5f26ecff0b5293290d60
current_release: no

## Original prompt

<!-- prompt-verbatim-begin -->
please design a new crow carrier board with onboard IC to connect directly VIA USB to raspberry pi. please delegate work to SOL agents

<!-- prompt-verbatim-end -->

- date: 2026-09-22
- channel: Codex task goal

## End goal — definition of done

A new, source-reproducible Crow carrier PCB with its own onboard USB interface
IC and a direct USB cable connection to a Raspberry Pi. Preserve the Crow audio
acquisition function while replacing the external USB/TDM bridge. Deliver the
reviewed schematic, placed and routed native board, design calculations, BOM,
and layout verification evidence. Physical hardware performance remains a
separate first-article measurement; no fabrication or order is authorized here.

| # | Criterion | Source | Status |
|---|---|---|---|
| G1 | USB interface IC and its required support circuitry are on the new carrier; Pi connects by USB cable without an external USB/TDM bridge. | P | unmet |
| G2 | Preserve eight synchronous Crow audio channels at the existing 48 kHz, 24-bit operating point, unless the user changes it. | A1 | unmet |
| G3 | Preserve supported Crow analog/power spoke interfaces and protect independently powered USB/Pi and carrier domains. | A1, A2 | unmet |
| G4 | Exact USB implementation has an evidenced host/software/configuration path; firmware dependency is resolved before freezing the IC. | P, Q2 | unmet |
| G5 | Source-generated schematic passes independent topology/readability review; routed board passes native DRC, connectivity, parity and relevant electrical/SI gates. | P, A3 | unmet |
| G6 | Work is delegated to Sol agents with bounded scopes, measured outputs and retained unsuccessful attempts. | P | unmet |

## Spec tensions

| # | Requirement | Standard / parts question | Resolution | User flagged |
|---|---|---|---|---|
| T1 | Onboard IC instead of existing external MCHStreamer | Existing Crow explicitly kept USB off-board; new user directive supersedes that boundary. | New carrier; see decision 0001. | yes, original request |
| T2 | Eight-channel direct USB audio | Exact IC, packet bandwidth, clock-master modes and host support must be verified together. | USB IC research in progress; no part frozen. | pending research |
| T3 | Complete onboard USB function | Some candidate ICs need custom firmware, while firmware is forbidden by default. | Q2 pending; research may compare options, but firmware authoring is not authorized yet. | yes, Q2 |

## Commission fact-lock

This is an intake record, not admission. OWED entries keep commissioning open;
seeded rule examples are not product facts and will be replaced before use.

| Fact | Value | Locked by |
|---|---|---|
| Audio | Eight simultaneous channels, 48 kHz, 24-bit samples; existing TDM uses eight 32-bit slots. | A1; original Crow BRIEF G2 and digital-interface fact |
| External outputs | Eight Crow audio/power spokes, all operating concurrently. Exact connector and load envelopes under source review. | A1; OWED requirements research |
| Input source | Retain independent external nominal 12 V carrier supply; exact min/max, load budget and protection are not yet adopted. | A2; Q1 pending |
| USB power role | Pi is USB host; carrier is USB device. VBUS is not a replacement for spoke power under A2. Exact sensing, detach and backfeed behavior OWED. | P, A2 |
| Protection posture | Re-evaluate USB-only, carrier-only, both-powered, brownout and cable connection/removal states; no inherited sequencing approval. | A2 |
| Measurement plane | Digital audio at Pi USB capture endpoint; analog/power capability at the existing Crow spoke boundary. Exact cable/load envelope OWED. | A1, A2 |
| Off-control / stored energy | Preserve supported quiet shutdown intent; changed USB core power and flash dependencies require new state analysis. | A2; OWED |
| Critical sourcing | USB bridge, support memory/clock/power ICs and exact footprints: sourcing research underway, not frozen. | P; OWED research |
| Integration posture | Onboard bare USB IC is explicitly requested; module comparison informs the exception but cannot substitute an external bridge. | P; decision 0001 |
| Mechanical boundary | No Pi HAT/header alignment is assumed. Existing Crow outline/hole coordinates are precedent, not automatically hard limits. | A3 |
| Fabrication / assembly | JLCPCB populated-PCBA intent; start with ordinary through-via multilayer manufacture. No numeric cost ceiling supplied; exact tier/cost OWED before freeze. | A3 |
| Firmware | Research permitted. No firmware source, build or release until Q2 is answered affirmatively or an existing authorized image path is selected. | Q2; skill default |

## Mating fact-lock

No board-to-Pi mechanical alignment is required under A3: connection is by a
USB cable. Exact USB receptacle/mate/cable and all serviced Crow connectors
still require their connector assembly facts before placement approval.
Foreign-mating applicability must be re-evaluated if a fixed enclosure or
Pi mounting geometry is introduced; no foreign dimensions are consumed now.

## Log

### D1 — 2026-09-22 — user directive
> please design a new crow carrier board with onboard IC to connect directly VIA USB to raspberry pi. please delegate work to SOL agents
Impact: commission a new carrier; supersede the prior off-board USB/MCHStreamer boundary for this project only. Use Sol for bounded research and engineering tasks.

### Q1 — 2026-09-22 — clarification asked
Asked: For the new USB carrier, should I retain Crow’s existing eight-channel audio inputs and external power supply, with USB carrying audio to the Raspberry Pi?
Answer: UNANSWERED — preliminary research proceeds on A1/A2.
Impact: USB power delivery and spoke-power topology could change.

### Q2 — 2026-09-22 — clarification asked
Asked: If the best onboard USB-audio IC needs firmware, may I develop and include that firmware as part of this design?
Answer: UNANSWERED — do not perform firmware authoring.
Impact: Determines admissible USB IC/software path and firmware workstream.

### A1 — 2026-09-22 — assumption (pending Q1)
Assumed: retain existing eight-channel phase-coherent audio, 48 kHz/24-bit operation and existing Crow spoke interoperability. Authority: P requests a new Crow carrier, not a reduced-channel product; existing Crow BRIEF is the requirements precedent.
Escalate if: user wants different sample rates, channel count, analog envelope or connector compatibility.

### A2 — 2026-09-22 — assumption (pending Q1)
Assumed: retain external carrier/spoke power; USB carries data to an independently powered Pi. Authority: existing Crow power boundary and P's requested interface change.
Escalate if: user requests USB-powered spokes or host power from this carrier.

### A3 — 2026-09-22 — assumption (not asked)
Assumed: separate new PCB, USB-cabled Pi5 compatibility as existing host precedent, no direct Pi header mating, design target through verified layout, JLCPCB assembly intent. Authority: P delegates a new board design; current PCB skill default assembly.
Escalate if: a specific enclosure, board outline, assembly budget or different Pi model imposes a requirement.

## Decision register

| id | decision | decided by | depth |
|---|---|---|---|
| 0000 | Retain the template ADR format reference; not a product choice. | agent (A3 / P-delegation) | [format reference](decisions/0000-example-adr.md) |
| 0001 | New board with onboard USB interface; prior off-board bridge boundary superseded. | user (P/D1) | [decision](decisions/0001-onboard-usb-boundary.md) |
| A1 | Existing Crow audio/spoke function retained provisionally. | agent (A1 / P-delegation) | log A1 |
| A2 | External carrier power retained provisionally. | agent (A2 / P-delegation) | log A2 |
| A3 | Cable connection, fresh design, populated-PCBA intent. | agent (A3 / P-delegation) | log A3 |
