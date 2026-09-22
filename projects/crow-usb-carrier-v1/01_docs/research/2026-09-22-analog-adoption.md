# Selective analog source adoption

## Delivered source

`03_tscircuit/src/crow_retained_analog.tsx` is a reusable draft module for the retained eight-channel receive path. It instantiates J1–J8 pod connectors, per-spoke protection, eight OPA2320/filter paths, eight TMUX2821 isolation stages, the CS5308P analog/reference/hardware-mode network, and the retained quiet-power and hardware-reset functions. The complete expanded reference-to-MPN map (297 references) is in `adoption.json`.

The module exposes these parent-board boundaries:

- power: `12V_PROTECTED`, `5V_BUCK`, `GND`, and `CHASSIS`;
- digital clocks into the ADC: `ADC_MCLK`, `ADC_BCLK`, and `ADC_FSYNC`;
- ADC data out: `ADC_DOUT1`;
- each pod: `12V_POD1..8`, `AUDIO_P1..8`, and `AUDIO_N1..8`.

The 8-channel, 48 kHz, 24-bit and external-12-V values are provisional commissioning defaults from `inputs/brief.md`, sufficient for reversible source preparation. They are not inherited design approvals. The draft provides one CS5308P serial data output boundary; the parent bridge design still has to prove that its selected clocking and serial format implement those defaults.

## Selective adoption decision

| Donor slice | Decision | New ownership or gate |
|---|---|---|
| J1–J8 pin roles, fuses, ESD, AC coupling, bias, OPA2320 and filters | Retain as draft source | Recheck connector mechanics, ESD return, signal integrity and analog performance on the new board |
| TMUX2821 isolation and `AUDIO_EN` | Retain | It prevents a powered or discharging analog path from driving the ADC; validate timing with the new supply transients |
| CS5308P reference filtering, straps and reset pulse | Retain | Parent bridge supplies MCLK/BCLK/FSYNC and consumes DOUT1; prove legal ratios and reset ordering |
| Held 5 V, LT3041 quiet 3.3 V, supervisors and dump | Retain for review, not freeze | Protects quiet startup/shutdown behavior; simplify only after same-carrier transient and hold-up analysis |
| External bridge connectors, presence detect, OE/Ioff isolation and cable clock buffers | Remove | Onboard bridge replaces these functions |
| Donor 12 V entry/protection and 5 V buck | Stop at boundary | Parent owns `12V_PROTECTED` and `5V_BUCK`, including current and sequencing budgets |
| Donor placement, copper, routes, transforms, board poses and review receipts | Do not adopt | New board needs new placement and review evidence |

This partition specifically avoids carrying the donor’s external-bridge power-state machinery into the new carrier. The retained supervisors act only on the quiet analog state. The onboard USB bridge and core supplies must not draw from `5V_LDO_HOLD` or `3V3_ADC`; VBUS sensing, backfeed policy, bridge regulators, and their sequencing belong to the parent design.

## Physical ownership

The source keeps functional blocks reusable without treating them as geographic placement groups. `C_ADC_CM1P..C_ADC_CM8N` are ADC-input pin-local parts. `R_ADC_PD1P..R_ADC_PD8N` retain the donor’s separate requirement to sit within 1.5 mm of the corresponding TMUX output. Each TMUX channel, its pull-down pair, its ADC common-mode capacitor pair, and the ADC endpoint form a joint routing/proof group, while each part retains its endpoint-specific proximity duty.

## Parts and assets

Only dossiers for MPNs instantiated by this module were copied into `02_parts`. Only used component footprints, component-local 3D models, the ADC channel map, and the locked TypeScript dependency graph were copied. `03_src/model_bindings.yaml` binds models by component reference and explicitly carries no inherited transform, board pose, or registration proof. The full asset list records source path, byte count, SHA-256, and byte-identity in `adoption.json`; `06_build/evidence/adopted-assets.sha256` is the flat checksum record.

The film-capacitor and LT3041 land patterns are selective package-geometry functions inside the TSX module, derived from the donor source without any placement coordinates. Other custom footprints are copied byte-for-byte under the new `crow_usb_analog` library name.

## Validation and limits

The reusable source passed a TypeScript no-emit check using the donor’s locked local toolchain. From this adoption workspace, rerun exactly:

```sh
/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-audio-carrier-v1/03_tscircuit/node_modules/.bin/tsc --noEmit --jsx preserve --moduleResolution bundler --module preserve --target es2022 --skipLibCheck --types /home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-audio-carrier-v1/03_tscircuit/node_modules/tscircuit/globals.d.ts 03_tscircuit/src/crow_retained_analog.tsx
```

This check establishes TSX readability and type compatibility only. A native schematic/PCB build, ERC, electrical simulation, clock validation, power transient proof, mechanical validation, placement, routing, EMC, and thermal review were outside this commissioning task and were not claimed.

## Dependencies the parent must close

1. Select and prove the onboard bridge clock-master topology, CS5308P serial format, and legal 48 kHz clock ratios.
2. Define bridge/core rails, 5 V current capacity, USB VBUS sensing and backfeed behavior, without loading the quiet analog rails.
3. Re-evaluate whether the retained precharge/hold/dump timing can be simplified on a same-carrier supply while preserving ADC quiet startup and shutdown.
4. Author and validate board-specific bridge firmware only after authorization. This packet contains no firmware and does not imply an available programming image.
5. Complete fresh connector, outline, placement, copper, ESD, signal-integrity, thermal, and review evidence for the new carrier.

## Coordinator integration disposition

Delivery runtime PASS; all113 copied-asset hashes independently verified before adoption. Eight inherited dossier footprint-library prefixes were changed to `crow_usb_analog` to match the supplied native library. The delivered `model_bindings.yaml` has no current generator consumer, so its six component-local rules were translated to existing `floorplan.yaml` placement-pattern `model_override` entries. No transforms or board coordinates were transferred. Template floorplan values remain under the commissioning hold. Original packet remains preserved in the isolated campaign and build scratch. Electrical and complete schematic admission remain owed.

Contract corrections: primary-source records were merged into their permitted part `notes.md` files. The donor channel-map JSON has no new-project consumer and is retained as evidence in build scratch; the TSX explicitly owns the same pod-to-ADC order `[4,3,2,1,5,6,7,8]`. No donor checker or unused live configuration was adopted.

A further footprint check found TPS389001DSER dossier/TSX disagreement: the dossier retained `GNDToe018`, while the supplied TSX/library used `TI_DSE0006A_Exact`. The draft dossier now names the supplied Exact footprint. The donor toe/mask layout optimization and associated acceptance are not transferred; new-board pin/escape/paste/grounding review is owed.

Expanding the actual JSX confirmed297 analog references but found a missing dossier for `RC0402FR-07100RL` used by R_OPA_BLEED1/2, despite its presence in the delivered ref manifest. The coordinator selectively added its donor dossier/PDF and provenance. Source expansion with the USB front end totals301 unique references; this is a source inventory check, not native connectivity or electrical acceptance.

## Independent source topology comparison

Coordinator recursively expanded the donor TSX and the adopted module without invoking the CAD generator. Of297 retained components,296 match donor exact MPN, resistance/capacitance and connected pin-to-net mappings. The sole difference is the intended U_ADC pin25 boundary rename from `TDM_RAW` to `ADC_DOUT1`; its other pins match. The donor expansion contains333 components. This establishes retained source-level topology/value identity, not native ERC, analog performance, placement or inherited engineering approval. Exact comparison output is `06_build/tmp/analog-adoption/donor-electrical-diff.json`.
