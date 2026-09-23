# DMQ0006A 0.10-mm land conflict — bounded public-record options

**Scope.** Read-only investigation, 2026-09-23. It covers the three present
adjustable `TPS62825DMQR` instances: `U_3V3X` (3.243–3.394 V, 1.0 A), `U_1V8`
(1.822–1.899 V, 0.30 A), and `U_CORE` (0.88–0.92 V, 1.2 A), all from the
5-V buck parent. Each presently has a 0.47-uH inductor, a 47-uF output bank,
and external feedback; CORE is enabled by `CORE_EN`. The project has already
recorded the exact MPN as JLC C2650334 and a dated 5,819-piece public-stock
observation, not allocation.

No files in the project were changed; no PCB was generated and no JLC account,
order, or upload was used.

## Finding

TI's DMQ0006A page-33 example is the only primary manufacturer land pattern
found for `TPS62825DMQR`: 0.60×0.25-mm left lands and 1.00×0.25-mm right lands,
with 0.100-mm opposing copper clearance. I found **no TI-published alternate
DMQ0006A land pattern** that preserves the current package and reaches JLC's
generic 0.15-mm different-net SMD-pad spacing. Therefore an unmodified
TPS62825DMQR has no public-record geometry resolution. JLC's part page says
the component is supported for PCB assembly, but that says nothing about this
specific land clearance.

The least disruptive technically credible remedy is a package replacement,
but none below is ready to adopt: each needs its exact primary drawing checked
against 0.15 mm, a new footprint/placement review, stock evidence, and
converter-loop qualification. Do not shrink the right DMQ lands or add a
blanket clearance exception; neither has a cited basis.

## Ranked options

| Rank / disruption | Option and public proof | What it preserves | What remains owed before adoption |
|---|---|---|---|
| 1 — lowest, **not a resolution** | Retain TPS62825DMQR and seek a *specific* JLC disposition for TI drawing 4222645/E page 33. JLC's public capability page states 0.15-mm different-net SMD-pad clearance, so public evidence cannot itself pass the 0.100-mm feature. | Exact MPN, C2650334, rail topology, setpoint dividers, inductor and capacitor design screens. | A fabricator disposition that explicitly covers the exact land pair, then native/TSX parity, mask/paste, thermal and full DRC. The project’s recorded stock snapshot must be refreshed at order; it is not reservation. |
| 2 — moderate, geometry passes but stock fails policy | **TPS62822DLCT** (TI DLC, 2.0×1.5-mm VSON-HR/QFN-8). TI documents 2.4–5.5-V input, adjustable 0.6–4 V, 2-A output, 4-uA typical Iq, 2.2-MHz DCS-Control, EN/PG, output discharge, and a 470-nH inductor family. Its primary DLC0008B land is 8×0.60×0.25 mm on 0.50-mm row pitch and 1.30-mm opposite-pad center separation: minimum copper gap is `0.50-0.25=0.25 mm` within a row and `1.30-0.60=0.70 mm` across rows. It clears 0.15 mm. | 5-V input range, 0.47-uH nominal inductor class, adjustable feedback concept, 2.2-MHz operating class, EN/PG functionality and 2-A rating. | It is not pin-compatible with DMQ (8 vs 6 pins). Rework pin mapping, feedback/PG/EN connections, compensation/cap network against its own datasheet, thermal/loop placement and rail startup/load-step tests. Public jlcsearch found exact TPS62822DLCT stock **38**, below the existing three-per-board × five +150 = **165** policy. |
| 3 — higher, actionable public-only candidate | **TLV62569PDDCR** (TI PDDC, six-pin SOT-23-thin). TI documents 2.5–5.5-V input, adjustable 0.6 V to VIN, 2-A output, EN and open-drain PG, 1.5-MHz typical operation, and 35-uA typical Iq. Its primary DDC0006A land is 6×1.10×0.60 mm on 0.95-mm row pitch and 2.70-mm opposite-pad center separation: minimum copper gap is `0.95-0.60=0.35 mm` within a row and `2.70-1.10=1.60 mm` across rows. It clears 0.15 mm. Public jlcsearch found exact PDDCR stock **2,233**, above the 165-piece policy. | All three rails’ 5-V input / voltage / 2-A output envelopes, external-divider architecture, EN and optional PG. Current source labels TPS62825 pin 2 `PG_NC` and leaves it unconnected, so retaining PDDC PG unconnected does not remove an existing rail/reset function. | New pinout and footprint, 1.5-MHz inductor/capacitor and converter-loop design, feedback thresholds, output-discharge/PG behavior, thermal review at 1.2-A CORE, startup/load-step/ripple/EMI tests, and fresh order-time stock/PCBA confirmation. The catalog result is not allocation. |
| 4 — higher, less attractive | **TLV62569DBVR** (five-pin DBV SOT-23) has a primary 5×1.10×0.60-mm land on 0.95-mm row pitch, so its row copper gap is 0.35 mm and it clears geometry. It has **no PG pin**: DBV pins are EN/GND/SW/VIN/FB. That does not break the present rails because their existing DMQ PG is explicitly `PG_NC` and unconnected, but no DBV stock result was obtained in this bounded screen. | Current EN, GND, SW, VIN and FB functions, and the rail voltage/current envelope. | Same 1.5-MHz power-stage, thermal, footprint, stock and first-article work as PDDC. Prefer PDDC while its public stock remains above policy because it retains optional PG and has an observed catalog result. |
| 5 — higher, less attractive | **TPS62A0569** is TI’s newer 2-A adjustable SOT-563 successor suggested on TI’s TLV62569 page (2.5–5.5-V input, 0.6–5.5-V output). It does not establish a clearance advantage because SOT-563 is still densely packaged. | Nominal rail voltage/current envelope only. | Primary package drawing, 0.15-mm clearance calculation, pinout, inductor/capacitor/loop, thermal, EMI and stock are all unreviewed. It is a candidate screen, not a solution. |

## Why no “alternate DMQ land” option is ranked

The local TI TPS62825 PDF and current TI product record identify DMQ as the
1.5×1.5-mm six-pin VSON-HR. Its documented board-layout example uses the
asymmetric land pattern currently in the native footprint. The asymmetric
1.00-mm side land is what creates the 0.100-mm clearance from the 0.60-mm
opposite land: with the shown centers, its inward edge is 0.10 mm from the
opposite inward edge. Reducing the 1.00-mm land to 0.90 mm would create a
nominal 0.15 mm gap, but TI does not publish that as an approved alternate.
This investigation therefore does not recommend it.

The current 0.47-uH/47-uF arrangement is specifically documented in the
project as a TPS62825 screen. Even the electrically similar TPS62822 cannot
inherit that evidence automatically: its own data sheet and layout guidance
must be checked. The same is more strongly true for TLV62569/TPS62A0569,
whose switching behavior differs.

## Evidence

* [TI TPS62825 / TPS6282x Rev. I data sheet](https://www.ti.com/lit/ds/symlink/tps62825.pdf), package drawing 4222645/E and example board layout page 33: DMQ0006A lands; product specs.
* [TI TPS62825 product page](https://www.ti.com/product/TPS62825): 2.4–5.5 V, 2 A, 0.6–4 V adjustable, 2.2 MHz and 1.5×1.5-mm QFN/VSON-HR family record.
* [JLC capabilities](https://jlcpcb.com/capabilities/Capab): generic different-net SMD pad-to-pad clearance 0.15 mm.
* [JLC C2650334 part record](https://jlcpcb.com/partdetail/TexasInstruments-TPS62825DMQR/C2650334): identifies exact TI MPN/package and says JLC supports its assembly; no conclusion about the project footprint follows.
* [TI TPS62822 product page](https://www.ti.com/product/TPS62822): active 2-A, 2.4–5.5-V, 0.6–4-V adjustable, 2.0×1.5-mm VSON-HR/QFN-8 family.
* [TI TLV62569 product page](https://www.ti.com/product/TLV62569): active 2-A SOT-23/SOT-563 family; specifications used above and TI’s pointer to TPS62A0569.
* Current project constraints: `03_tscircuit/src/crow_usb_digital.tsx`, `03_src/rules/power_tree.yaml`, `02_parts/TPS62825DMQR/part.yaml`, and `01_docs/research/2026-09-23-adjustable-digital-rails-source-candidate.md`.

**Decision for source repair.** Keep the DMQ issue open rather than treating
the manufacturer example as a generic-rule waiver. If a public-only repair is
required now, investigate the exact DLC and DBV drawings first; the first one
whose manufacturer land pattern demonstrably meets 0.15 mm and whose JLC
population is evidenced is the least disruptive viable replacement. Until
then, no option here supports a geometry edit or an adopted part substitution.

## Correction and bounded geometry/stock follow-up

The earlier DBV row incorrectly said it had PG. The primary TLV62569 pin table
shows DBV five-pin SOT-23 has EN=1, GND=2, SW=3, VIN=4, FB=5 and **no PG**;
PG exists only on the six-pin `TLV62569P` PDDC/DRL variants. The current
`Buck()` source already labels DMQ pin 2 `PG_NC` and makes no pin-2 connection
for `U_3V3X`, `U_1V8`, or `U_CORE`. Thus DBV's missing PG has no present
rail/reset-net effect, but PDDC better preserves an optional PG terminal.

Primary land calculations above are taken directly from TI DLC0008B,
DBV0005A, and DDC0006A example layouts. They establish bare copper clearance
only; solder-mask, thermal, placement and routed switching-loop acceptance are
separate work.

Public read-only jlcsearch observations at 2026-09-23T18:33:02Z:

| Exact MPN | Catalog result | Stock | Policy result | Evidence |
|---|---|---:|---|---|
| TPS62822DLCT | LCSC `C2072011`, VSON-8(1.5×2) | 38 | below 165 | response SHA-256 `790cca8f40d38867a4892590c892e7ba091e24e991834c80bfc2f72f570a2675` |
| TLV62569PDDCR | LCSC `C398365`, SOT-23-THIN-6 | 2,233 | meets 165 | response SHA-256 `5322fd71991ff651ec9b5c5ef209a8893d9ffd7871472572a996585cd723afe3` |

`TLV62569PDDCR` is consequently the first actionable **public-only**
replacement investigation path: its primary land clears the selected
0.15-mm rule and its public catalog observation clears the current numeric
stock policy. It remains an unadopted source candidate until all listed
electrical, thermal, placement, routing and order-time checks pass.

## Retained coordinator evidence

Downloaded public inputs are retained locally in `06_build/verification/dmq-public-screen/manifest.json`, with exact source URLs and SHA-256 hashes. These are candidate investigation inputs, not adopted part dossiers. The electrical replacement screen is still pending; no part substitution has been made.

## Completed electrical-screen follow-up

See `2026-09-23-regulator-replacement-electrical-screen-sol.md`: direct TLV62569 substitution fails. Checking packing suffixes found TPS62822DLCR / C473385 with 1,979 public units and TPS62823DLCR / C2693497 with 7,232. These supersede the initial DLCT-only stock conclusion and prioritize the closer DLC family for redesign investigation. No substitution is adopted; new pin mapping, capacitor/rail margins, sequencing and hot thermal evidence remain owed. Raw public inputs are retained locally under `06_build/verification/regulator-replacement-public-screen/`.
