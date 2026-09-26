# brief: crow-usb-carrier-v2

status: draft
prompt_sha256: 5b4bf606a77fbfb700f834caf36af9b33d23c14a249a5f26ecff0b5293290d60
current_release: no

## Original prompt

<!-- prompt-verbatim-begin -->
please design a new crow carrier board with onboard IC to connect directly VIA USB to raspberry pi. please delegate work to SOL agents

<!-- prompt-verbatim-end -->

- date: 2026-09-22
- channel: Codex task goal, preserved from v1 without editing its words

## End goal — definition of done

A separately reviewed Crow USB carrier with an onboard USB audio IC, eight-channel Crow interface, JLCPCB-populated SMD design and a sealed hardware release. Firmware authoring and purchase remain outside this project authorization.

| # | Criterion | Source | Status |
| --- | --- | --- | --- |
| G1 | Onboard USB IC, cable connection to Raspberry Pi | Original prompt | unmet |
| G2 | Eight synchronous Crow channels at the inherited 48 kHz, 24-bit operating point; external carrier supply | A1/A2 from [v1 BRIEF](../../crow-usb-carrier-v1/01_docs/BRIEF.md) | unmet — v2 revalidation owed |
| G3 | JLCPCB stocks and populates every SMD; five-board quantity | Earlier user D5/D6 in v1 BRIEF | unmet — v2 sourcing admission owed |
| G4 | Manual assembly for the eight RJ45s and sixteen film capacitors | Earlier user D9 in v1 BRIEF | unmet — v2 population declaration owed |
| G5 | Sealed hardware release, independently reviewed | Earlier user D6 in v1 BRIEF | unmet |

## Spec tensions

Unreviewed at v2 commission. USB ESD transient suitability and stack/USB geometry are explicit open decisions; no safe value is inferred from v1.

## Commission fact-lock

| Fact | Retained value or missing evidence | Source |
| --- | --- | --- |
| Audio | Eight synchronous channels, 48 kHz, 24-bit; inherited design assumption, not user-confirmed numeric requirement | A1 from [v1 BRIEF](../../crow-usb-carrier-v1/01_docs/BRIEF.md) |
| External outputs | Eight simultaneous Crow spokes, each 0.10 A, at inherited 10.8–13.2 V connector-plane envelope; exact connector/mate and realized delivery need v2 review | A1 and [v1 power source](../../crow-usb-carrier-v1/03_src/rules/power_tree.yaml) |
| Input envelope and off states | Inherited independently isolated 11.4–13.2 V carrier input; 2.85 A hot continuous allocation, 4 A fuse, bounded source fault at 3.4 A peak then 2.85 A/off. USB VBUS is sense-only. Revalidate source/cable, sequencing and rail-off behavior in v2 | A2 and [v1 power source](../../crow-usb-carrier-v1/03_src/rules/power_tree.yaml) |
| Protection | USB ESD decision OPEN; v1 TI TPD2EUSB30ADRTR is only `prototype_only` | [v1 D13](../../crow-usb-carrier-v1/01_docs/decisions/0013-usb-esd-prototype-boundary.md) |
| Sourcing/population | Five boards; JLCPCB stocks/populates all SMD; 150 extra public units per exact part except selected XU316/C6362698 at five units; specified 24 through-hole parts manually assembled | v1 user D5/D7/D9/D10; [v1 stock lock](../../crow-usb-carrier-v1/01_docs/decisions/0012-initial-public-stock-lock.md) |
| Source evidence | Public records and jlcsearch for design; unchanged exact initial stock selection remains locked against later stock movement, but order allocation OWED | v1 user D11/D12; [v1 public-record decision](../../crow-usb-carrier-v1/01_docs/decisions/0010-public-records-design-admission.md) |
| Integration | Onboard USB IC, current v1 XU316 and two TLV320ADC6140 ADCs; v1 schematic is review evidence, not v2 admission | original prompt; [current v1 analog source](../../crow-usb-carrier-v1/03_tscircuit/src/crow_retained_analog.tsx) and [exact-parts list](../../crow-usb-carrier-v1/01_docs/sourcing/exact-parts.csv) |
| Stack/cross-section | OPEN; neither v1 7628G nor 3313A research selected | [restart](RESTART.md) |

## Mating fact-lock

USB cable/connector and all Crow spoke mate/service dimensions are OWED for v2; no v1 footprint pose or physical fit grade is inherited. Acquire vendor/physical evidence before placement.

## Log

### D1 — 2026-09-25 — latest user directive
> Can you please start this board from scratch

Impact: create this new project, reset layout/routing decisions, and pause at the first issue. The [restart record](RESTART.md) lists retained constraints and the first stop. The original prompt above remains verbatim.

### A1 — 2026-09-25 — carry-forward boundary

Retain earlier user sourcing, XMOS exception, manual through-hole, public-record and initial-stock-lock directives as requirements, with exact v1 evidence linked above. Do not copy v1 geometry, route, stack, process or admissions. Escalate if an exact MPN/LCSC or quantity changes, or if retained functionality conflicts with the new user's direction.

### A2 — 2026-09-25 — inherited operating envelope, unconfirmed

Retain v1's eight synchronous 48 kHz/24-bit channels, eight concurrent 0.10 A spokes, 10.8–13.2 V spoke connector target and 11.4–13.2 V isolated external input as design assumptions. These preserve the known functional/load envelope while restarting layout; v2 must revalidate source faults, realized voltage drops, thermal behavior and mating before admission. See the [v1 fact-lock](../../crow-usb-carrier-v1/01_docs/BRIEF.md) and [power source](../../crow-usb-carrier-v1/03_src/rules/power_tree.yaml). Escalate if the user changes the audio, power or connector requirement.

## Decision register

No v2 engineering selection has been accepted. USB ESD is the first open selection; stack/USB cross-section follows. The [commissioning hold](COMMISSIONING-HOLD.md) remains active.
