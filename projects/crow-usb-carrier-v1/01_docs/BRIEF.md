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
| G1 | USB interface IC and its required support circuitry are on the new carrier; Pi connects by USB cable without an external USB/TDM bridge. | P | source implemented; native board unmet |
| G2 | Preserve eight synchronous Crow audio channels at the existing 48 kHz, 24-bit operating point, unless the user changes it. | A1 | unmet |
| G3 | Preserve supported Crow analog/power spoke interfaces and protect independently powered USB/Pi and carrier domains. | A1, A2 | unmet |
| G4 | Exact USB implementation has an evidenced host/software/configuration path and a complete hardware programming/interface contract; firmware authoring remains a separate, explicitly authorized workstream. | P, Q2 | unmet |
| G5 | Source-generated schematic passes independent topology/readability review; routed board passes native DRC, connectivity, parity and relevant electrical/SI gates. | P, A3 | unmet |
| G6 | Work is delegated to Sol agents with bounded scopes, measured outputs and retained unsuccessful attempts. | P | satisfied for work to date; continues through remaining stages |

## Spec tensions

| # | Requirement | Standard / parts question | Resolution | User flagged |
|---|---|---|---|---|
| T1 | Onboard IC instead of existing external MCHStreamer | Existing Crow explicitly kept USB off-board; new user directive supersedes that boundary. | New carrier; see decision 0001. | yes, original request |
| T2 | Eight-channel direct USB audio | Exact IC, packet bandwidth, clock-master modes and host support must be verified together. | XU316-1024-TQ128-C24 selected under decision 0003; complete native schematic and host configuration verification remain owed. | pending research |
| T3 | Complete onboard USB function | Some candidate ICs need custom firmware, while firmware is forbidden by default. | D2 retains hardware-only scope. Board-specific firmware remains required for operation; its authoring is not authorized. | yes, Q2 |

## Commission fact-lock

This is an intake record, not admission. OWED entries keep commissioning open;
seeded rule examples are not product facts and will be replaced before use.

| Fact | Value | Locked by |
|---|---|---|
| Audio | Eight simultaneous channels, 48 kHz, 24-bit samples; existing TDM uses eight 32-bit slots. | A1; original Crow BRIEF G2 and digital-interface fact |
| External outputs | Eight Crow audio/power spokes concurrently, each 0.10 A; 10.8–13.2 V at the carrier connector plane. Three parallel supply and return conductors; the selected 15 m cable has a 3.0 ohm total hot-loop acceptance allocation. | A1; power_tree.yaml and 100009141 cable selection; realized delivery owed |
| Input source | Independent isolated external 11.4–13.2 V input; 2.185 A one-fault voltage-drop screen, 2.85 A hot continuous trunk/protection allocation, and 4 A input fuse. These distinct quantities are defined in power_tree.yaml. Actual source fault behavior and realized thermal/delivery qualification remain owed. | A2; source power/protection contracts; Q1 unanswered |
| USB power role | Pi is USB host; carrier is USB device. VBUS feeds sensing only under decision 0002; it does not supply the carrier. Exact power-state verification remains owed. | P, A2 |
| Protection posture | Re-evaluate USB-only, carrier-only, both-powered, brownout and cable connection/removal states; no inherited sequencing approval. | A2 |
| Measurement plane | Digital audio at Pi USB capture endpoint; analog/power capability at the existing Crow spoke boundary. Exact cable/load envelope OWED. | A1, A2 |
| Off-control / stored energy | Preserve supported quiet shutdown intent; changed USB core power and flash dependencies require new state analysis. | A2; OWED |
| Critical sourcing | XU316, W25Q128JWSIQ 1.8 V flash, CS5308P-DNR ADC, LT3045 quiet regulator and separate core/PHY rails; current source has 489 references and 85 exact MPNs. Full selected-BOM sourcing remains open. | P; current TSX/manifest/dossiers and sourcing CSV |
| Integration posture | Onboard bare USB IC is explicitly requested; module comparison informs the exception but cannot substitute an external bridge. | P; decision 0001 |
| Mechanical boundary | Adopt the current 220 × 120 mm rectangle for initial placement, with no inherited mounting holes or Pi HAT/header alignment. This reversible design assumption is not a size maximum or fit claim. | A3; decision 0007 |
| Fabrication / assembly | JLCPCB populated-PCBA intent, four-layer JLC04161H-7628G stackup with the advanced routing/process candidate in decision 0006; nominal 90-ohm USB cross-section documented. Selective LT3045 via fill/cap remains a proposed uploader/order requirement pending exact vendor acceptance. No hard numeric design budget was supplied; authorized expenditure is zero, with actual-board quotations and process acceptance required before spending. | A3; decisions 0006 and 0007 |
| Firmware | Research permitted. No firmware source, build or release until Q2 is answered affirmatively or an existing authorized image path is selected. | Q2; skill default |

## Mating fact-lock

No board-to-Pi mechanical alignment is required under A3: connection is by a
USB cable. Connector source admission now passes for all 11 operated connector references.
Nineteen explicitly planned installed-fit, cable-route and service checks remain
for their physical qualification boundary; source admission is not placement approval.
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
Impact: Controls firmware source/build/release authorization. See D2: it does not by itself prohibit reversible hardware design.

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
| 0002 | USB sensing and independent external carrier power topology. | agent (A2 / P-delegation) | [decision](decisions/0002-usb-power-path-intent.md) |
| 0003 | Onboard XU316, retained CS5308P and integrated TPSM power boundary. | agent (P-delegation) | [decision](decisions/0003-integrated-subsystem-boundaries.md) |
| 0004 | USB shell to local GND; Crow spoke shells remain on CHASSIS. | agent (A2 / P-delegation) | [decision](decisions/0004-usb-shield-separation.md) |
| 0007 | Initial outline and design-only cost assumptions; no purchase authorization. | agent (A3 / P-delegation) | [decision](decisions/0007-outline-and-design-cost-assumptions.md) |
| 0008 | USB tree endpoint paths, 1 mm skew ceiling and no-signal-via policy. | agent (P-delegation) | [decision](decisions/0008-usb-realized-copper-policy.md) |
| A1 | Existing Crow audio/spoke function retained provisionally. | agent (A1 / P-delegation) | log A1 |
| A2 | External carrier power retained provisionally. | agent (A2 / P-delegation) | log A2 |
| A3 | Cable connection, fresh design, populated-PCBA intent. | agent (A3 / P-delegation) | log A3 |

### D2 — 2026-09-22 — firmware posture clarification

Authority: user requested PCB design; `skills/pcb-design/references/commission-and-scope.md` says firmware is forbidden unless explicitly requested, and PCB gates may define the hardware programming interface without expanding scope. The commission exit criteria require an explicit firmware posture and recorded decisions, not an affirmative firmware authorization for every programmable part.

Decision: retain **firmware forbidden** and keep Q2 unanswered. Continue the hardware-only design under the user's existing PCB authorization. The prior coordinator requirement for firmware authorization before any hardware pin freeze was overly broad and is superseded. Before hardware freeze, verify the exact SoC, flash protocol/readiness, documented USB/audio stack capabilities, port resources, clock/data contract, reset/supply behavior and accessible programming interface. Document the board-specific firmware work still required; do not claim that an image exists or that USB capture has run. Firmware creation/build/release and physical functional qualification remain separate deliverables. This does not waive schematic, electrical, placement, routing, sourcing or PCB review gates.

### D3 — 2026-09-22 — current-state reconciliation

Updated intake rows to reflect adopted hardware source and decisions 0002–0004. This is not commission acceptance: [findings.yaml](findings.yaml) retains pending commission, native schematic and routed-layout gates. Source expansion and footprint loading do not prove a built board. G6 evidence is the bounded SOL deliveries and preserved unsuccessful attempts recorded in [commission journal](journal/commission.md) and the source-adoption research dispositions. Q1/Q2 remain unanswered; A1/A2 and firmware-forbidden D2 remain unchanged.

### D4 — 2026-09-22 — source checkpoint reconciliation

The current source has 489 references and 85 selected MPNs. Connector SOURCE
passes for 11 instances with 19 explicit physical deferrals and no source
findings. ADC/film-capacitor packaging and the PLL capacitor have been updated
without changing the named signal connectivity. The power rows above now
separate nominal requirements, one-fault screens, current allocations and fuse
rating; none is a bench-current-limit instruction. See the source journal and
[superseding advanced fabrication posture](decisions/0006-four-layer-advanced-escape-process.md); decision 0005 remains the superseded historical baseline.

The brief remains draft while full-BOM sourcing and refreshed schematic-source review are completed.
The source power/protection disposition is reviewed; its native-layout and
physical qualifications remain in the open final-design findings. A1/A2 remain the retained
Crow design assumptions; Q1/Q2 remain unanswered. No firmware or purchase work
is authorized by this reconciliation.
