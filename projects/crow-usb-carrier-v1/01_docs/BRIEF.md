# brief: crow-usb-carrier-v1

status: agreed
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
and layout verification evidence, then a reviewed, self-contained sealed hardware release
with fabrication/assembly payloads and the applicable release receipts. Physical hardware performance remains a
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
| T2 | Eight-channel direct USB audio | Exact IC, packet bandwidth, clock-master modes and host support must be verified together. | XU316-1024-TQ128-C24 and the documented lib_xua/lib_i2s plus Linux snd-usb-audio path are selected under decision 0003 and the hardware/software interface record; native schematic and board-specific firmware implementation remain owed. | yes; decision 0003 / D2 |
| T3 | Complete onboard USB function | Some candidate ICs need custom firmware, while firmware is forbidden by default. | D2 retains hardware-only scope. Board-specific firmware remains required for operation; its authoring is not authorized. | yes, Q2 |

## Commission fact-lock

This is an intake record, not admission. OWED entries keep commissioning open;
seeded rule examples are not product facts and will be replaced before use.

| Fact | Value | Locked by |
|---|---|---|
| Audio | Eight simultaneous channels, 48 kHz, 24-bit samples; existing TDM uses eight 32-bit slots. | A1; original Crow BRIEF G2 and digital-interface fact |
| External outputs | Eight Crow audio/power spokes concurrently, each 0.10 A; 10.8–13.2 V at the carrier connector plane. Three parallel supply and return conductors; the selected 15 m cable has a 3.0 ohm total hot-loop acceptance allocation. | A1; power_tree.yaml and 100009141 cable selection; realized delivery owed |
| Input source | Independent isolated external 11.4–13.2 V input; 2.185 A one-fault voltage-drop screen, 2.85 A hot continuous trunk/protection allocation, and 4 A input fuse. These distinct quantities are defined in power_tree.yaml. Conditional source fault requirement: at most 3.4 A peak, 10 ms cumulative above 2.85 A per fault episode, then at most 2.85 A or off until explicit rearm; recovery at most 13.2 V. Actual source/cable fault behavior and realized thermal/delivery qualification remain owed. | A2; source power/protection contracts; Q1 unanswered |
| USB power role | Pi is USB host; carrier is USB device. VBUS feeds sensing only under decision 0002; it does not supply the carrier. Exact power-state verification remains owed. | P, A2 |
| Protection posture | Re-evaluate USB-only, carrier-only, both-powered, brownout and cable connection/removal states; no inherited sequencing approval. | A2 |
| Measurement plane | Digital audio at Pi USB capture endpoint; analog/power capability at the existing Crow spoke boundary. Exact cable/load envelope OWED. | A1, A2 |
| Off-control / stored energy | Preserve supported quiet shutdown intent; changed USB core power and flash dependencies require new state analysis. | A2; OWED |
| Critical sourcing | XU316, W25Q128JWSIQ 1.8 V flash, two TLV320ADC6140IRTWT ADCs, LT3045 quiet regulator and separate core/PHY rails; current generated schematic has 568 references, 90 exact MPNs and 39 pages. Refreshed public observations meet D7/D10 for all88 JLC-coded MPNs. Exactly 24 D9 through-hole refs are manual assembly. D11 uses public records and jlcsearch for design continuation; actual assembly fulfillment remains an order-time check. Schematic review and placement remain ahead. | P; current TSX/manifest/dossiers and sourcing CSV |
| Integration posture | Onboard bare USB IC is explicitly requested; module comparison informs the exception but cannot substitute an external bridge. | P; decision 0001 |
| Mechanical boundary | Adopt the current 220 × 120 mm rectangle for initial placement, with no inherited mounting holes or Pi HAT/header alignment. This reversible design assumption is not a size maximum or fit claim. | A3; decision 0007 |
| Fabrication / assembly | JLCPCB populated-PCBA intent, four-layer JLC04161H-7628G stackup with the advanced routing/process candidate in decision 0006; nominal 90-ohm USB cross-section documented. Selective LT3045 via fill/cap remains a proposed uploader/order requirement pending exact vendor acceptance. D5 requires JLCPCB to populate every non-through-hole component from in-stock inventory, including U_ADC. The former ADC exclusion and secondary-assembler plan are superseded; ADC sourcing and other SMD shortages must close before placement. No hard numeric design budget was supplied; authorized expenditure is zero, with actual-board quotations and process acceptance required before spending. | A3; decisions 0006 and 0007; assembly.yaml |
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
| 0005 | Historical four-layer fabrication/cost baseline; superseded by 0006. | agent (A3 / P-delegation) | [superseded decision](decisions/0005-four-layer-design-cost-posture.md) |
| 0006 | Four-layer advanced escape/process posture, with selective via fill/cap qualification owed. | agent (A3 / P-delegation) | [decision](decisions/0006-four-layer-advanced-escape-process.md) |
| 0007 | Initial outline and design-only cost assumptions; no purchase authorization. | agent (A3 / P-delegation) | [decision](decisions/0007-outline-and-design-cost-assumptions.md) |
| 0008 | USB tree endpoint paths, 1 mm skew ceiling and no-signal-via policy. | agent (P-delegation) | [decision](decisions/0008-usb-realized-copper-policy.md) |
| 0009 | XMOS-only public-stock surplus exception; JLC population remains required. | user (D10) | [decision](decisions/0009-xmos-public-stock-reserve-exception.md) |
| 0010 | Public records and jlcsearch for design continuation; assembly fulfillment remains unconfirmed. | user (D11) | [decision](decisions/0010-public-records-design-admission.md) |
| A1 | Existing Crow audio/spoke function retained provisionally. | agent (A1 / P-delegation) | log A1 |
| A2 | External carrier power retained provisionally. | agent (A2 / P-delegation) | log A2 |
| A3 | Cable connection, fresh design, populated-PCBA intent. | agent (A3 / P-delegation) | log A3 |

### D2 — 2026-09-22 — firmware posture clarification

Authority: user requested PCB design; `skills/pcb-design/references/commission-and-scope.md` says firmware is forbidden unless explicitly requested, and PCB gates may define the hardware programming interface without expanding scope. The commission exit criteria require an explicit firmware posture and recorded decisions, not an affirmative firmware authorization for every programmable part.

Decision: retain **firmware forbidden** and keep Q2 unanswered. Continue the hardware-only design under the user's existing PCB authorization. The prior coordinator requirement for firmware authorization before any hardware pin freeze was overly broad and is superseded. Before hardware freeze, verify the exact SoC, flash protocol/readiness, documented USB/audio stack capabilities, port resources, clock/data contract, reset/supply behavior and accessible programming interface. Document the board-specific firmware work still required; do not claim that an image exists or that USB capture has run. Firmware creation/build/release and physical functional qualification remain separate deliverables. This does not waive schematic, electrical, placement, routing, sourcing or PCB review gates.

### D3 — 2026-09-22 — current-state reconciliation

Updated intake rows to reflect adopted hardware source and decisions 0002–0004. This is not commission acceptance: [findings.yaml](findings.yaml) retains pending commission, native schematic and routed-layout gates. Source expansion and footprint loading do not prove a built board. G6 evidence is the bounded SOL deliveries and preserved unsuccessful attempts recorded in [commission journal](journal/commission.md) and the source-adoption research dispositions. Q1/Q2 remain unanswered; A1/A2 and firmware-forbidden D2 remain unchanged.

### D4 — 2026-09-22 — source checkpoint reconciliation

The admitted source has 493 references and 85 selected MPNs. Connector SOURCE
passes for 11 instances with 19 explicit physical deferrals and no source
findings. ADC/film-capacitor packaging and the PLL capacitor have been updated
without changing the named signal connectivity. The power rows above now
separate nominal requirements, one-fault screens, current allocations and fuse
rating; none is a bench-current-limit instruction. See the source journal and
[superseding advanced fabrication posture](decisions/0006-four-layer-advanced-escape-process.md); decision 0005 remains the superseded historical baseline.

Commission, architecture, and design-stage sourcing are admitted against the reviewed 493-reference source, current 85/85 two-pool result, accepted 40-page source review, source decision locks, schema and electrical receipts. Native schematic, placement, routing, provider capability, order allocation and physical qualification remain open.
The source power/protection disposition is reviewed; its native-layout and
physical qualifications remain in the open final-design findings. A1/A2 remain the retained
Crow design assumptions; Q1/Q2 remain unanswered. No firmware or purchase work
is authorized by this reconciliation.

### D5 — 2026-09-23 — JLCPCB population and stock requirement
> We need JLCPCB to populate the non through hole components, they need to be in stock

Impact: every non-through-hole component must be supplied from in-stock JLCPCB inventory and populated by JLCPCB. Distributor stock, consignment assumptions, secondary assembly and design-only sourcing-risk acceptance cannot substitute for this requirement. Reopen ADC selection and every SMD sourcing shortfall before physical placement. The prior U_ADC secondary-assembler plan is superseded. Through-hole exceptions may be evaluated separately; none are automatically excluded. No order or expenditure is authorized.

### D6 — 2026-09-23 — release target and model delegation
> mint a new release using the new JCLPCB sourcing and block schematic + block pre-routing and placement. Please use sol and terra where possible

Impact: target a new sealed hardware release, extending the previous design/layout-seal target. D5 remains binding: JLCPCB must stock and populate every non-through-hole component. Use the existing P1–P5 block floorplan, placement, critical-local-route and joint-proof graph with independent engineering acceptance; block metadata alone does not pass placement. Use SOL for bounded engineering and Terra for suitable evidence/audit work. Release requires the existing fabrication, assembly, exact-artifact independent review, archive rehearsal and seal checks. Firmware authoring and purchasing remain outside scope.

### D7 — 2026-09-23 — stock reserve confirmed
> Keep the 150-extra-unit requirement for every part.

Context: the question contrasted retaining 150 extra publicly stocked units per part beyond the five-board build with using build quantity and confirming JLC assembly attrition at order time. The user selected the former. Keep `build_quantity: 5` and `public_stock_surplus: 150`; aggregate quantities by exact part/code. This is now an explicit user constraint, not merely a template default. JLC allocation and actual assembly attrition/minimum quantities still require order-time confirmation. Current AK5578EN (36 versus 155 required), AK5558VN (32 versus 155), and two-per-channel TMUX2819 (199 versus 230) observations do not qualify these candidates. No release or placement admission follows from their engineering feasibility.

### D8 — 2026-09-23 — established USB audio IC preference
> What are reasonable was to resolve this? we want to use a ready IC for this

Interpretation: retain the selected XMOS USB audio controller while investigating sourcing; set aside the general-purpose STM32 USB redesign proposal. XMOS has an established vendor USB audio framework but still needs board-specific configuration and programming; no ready Crow image or functional capture is claimed. D7 remains unchanged: 155 publicly stocked units for the one-per-board controller. JLC replenishment/private-stock sourcing, an XMOS-specific reserve exception, and waiting for public replenishment were presented as options, not adopted decisions. No purchase, supplier contact, private-stock policy substitution, firmware authoring or reserve waiver is authorized.

### D9 — 2026-09-23 — manual assembly of specified through-hole parts
> Plan manual assembly for these through-hole parts

Context: the user selected manual assembly for eight RJ45 connectors and sixteen film capacitors per board after JLC assembles every SMD component. Exact selected parts remain Wurth615008160221 and KEMETR82DC4100CK60J. Public distributor observations clear the five-board quantity plus150 extra per exact part (190 connectors;230 capacitors). Record these24 references in assembly.yaml as user-supplied, excluded from JLC sourcing/BOM/CPL but retained in the complete design and final fitted population. J_PWR is not included in this decision. Refresh external stock before ordering; no purchase, SMD exception, component substitution or reserve reduction is authorized.


### D10 — 2026-09-23 — XMOS-only public-stock reserve exception
> lets make an exception for xmos and keep going

Impact: waive the150-extra-unit public-stock reserve only for the selected XMOS XU316-1024-TQ128-C24 / C6362698 at U_XU. Its prelayout public-stock threshold becomes the quantity for five boards (currently five devices), while JLC must still stock and populate it. Retain150 extra units for every other exact part and retain D9 manual through-hole assembly. Confirm JLC assembly attrition/minimum and actual allocation before ordering; this exception is not an attrition waiver, private-stock substitution, purchasing authorization or firmware authorization. Resume sourcing admission and the requested block schematic/placement/pre-routing release workflow after refreshing exact-source evidence. See decision0009.


### D11 — 2026-09-23 — public records and jlcsearch only
> Please only use public records and jlcsearch

Impact: use public records and jlcsearch for sourcing investigation and public-catalog pre-layout design admission. Do not require or attempt authenticated JLC access or BOM uploads for this engineering workflow. Continue the design using exact public-stock evidence under D7/D10 and preserve D9 manual assembly. This changes the evidence boundary for design continuation; it does not establish supplier allocation, assembly attrition, final pricing or order readiness. No purchasing, supplier contact or credential access is authorized. See decision0010.

### D12 — 2026-09-24 — initial stock check locks part selection
> once we do the stock check at the start lets not worry about it again. its locked in

Impact: for Crow, one dated exact public-stock screen at part selection applies D7's five-board plus-150-unit threshold (and the XMOS exception). Subsequent inventory movement does not reopen an unchanged selected part or force a redesign. The original TI USB data ESD part passed the retained direct JLC screen at 307 versus 155 and may be restored as the selected candidate; later 29-unit stock does not undo that source decision. Recheck a new MPN/LCSC or quantity at its own initial selection. This does not reserve stock, prove eventual JLC assembly allocation, authorize an order, or accept electrical/physical behavior. See decision0012.

### D13 — 2026-09-25 — USB ESD schematic-only prototype boundary

Impact: the locked TI ESD candidate is admitted only for a separately gated engineering schematic prototype. The XU316 powered/rail-off transient and exact-board ESD finding remains open and blocks design-clean/release maturity; ordinary full/reuse, release, and manufacturing order paths refuse the prototype status. The independent review and bounded test plan are hash-bound in critical selection. No prototype fabrication or order is authorized by this decision. See decision0013.

### D14 — 2026-09-25 — clean restart; stop at the first issue
> Can we start the board again from scratch and lets pause at the first sign of issues . we want this to work seemlessly

Working interpretation: restart placement and routing, retaining the brief, selected parts, locked stock policy and schematic as inputs subject to validation. Preserve all existing boards and evidence as history; do not carry forward their placement, routes or admissions as a new layout. Stop on the first concrete input, engineering or tooling issue; do not silently repair it, change the scope, or launch another research attempt. Report the cause and proposed next action before continuing.

Restart input check: `critical_part_selection_admission.py projects/crow-usb-carrier-v1` returned `PROTOTYPE_ONLY` (1/1 selections, ordinary-mode exit 1). U_USB_ESD remains TPD2EUSB30ADRTR/C94934 with deferred XU316 transient protection evidence. This is not a stock failure or proof that the component fails electrically. The existing ordinary build/reuse path rejects this maturity; bounded prototype research is a different path. Restart is PAUSED at this first issue, before creating any fresh placement or board. Next discussion: resolve the electrical evidence and intended prototype-versus-release boundary before selecting the restart execution path. No new layout has been generated.
