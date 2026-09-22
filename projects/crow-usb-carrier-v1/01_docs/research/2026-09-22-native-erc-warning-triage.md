# Native schematic warning triage — 2026-09-22

Scope: diagnostic baseline, not independent schematic acceptance or a waiver.

The actual all-severity KiCad ERC invocation reported 3,459 warnings:

| Class | Count | Observed cause / next boundary |
|---|---:|---|
| endpoint_off_grid | 2088 | Converter pin/wire endpoint coordinates fall off the connection grid. Exact exported connectivity was checked separately; human editability and independent review remain owed. |
| lib_symbol_issues | 878 | All messages name absent library `elt`; generated symbols are embedded in the native schematic. This does not prove datasheet correctness. |
| footprint_link_issues | 493 | Project footprint libraries are not yet registered beside the schematic. The board generator owns fp-lib-table emission; native board library/parity checks remain owed after placement admission. Earlier independent footprint loading covered85/85 selected MPNs. |

No warning was suppressed. Zero error-level ERC findings were measured separately before this diagnostic run. The canonical human document is the40-page tscircuit PDF; this native schematic serves the machine backend. Neither result accepts physical placement or routing.

Native schematic SHA256: `46da223ce42ed3f8d546a8c055d7bb0d4d5684d8e766c22ba57e42dfc0c23138`.

Raw local report: `06_build/erc.rpt`, SHA256 `6c6720482b0bd07a737fd0d1bffb77f25c1174dcc4c3f58e59bbd5f9fef9a0b4`.
