# Independent source review — TPS62822 DLC candidate `795acf68b1b69ac341972ec237746bac276e9add`

**Verdict: PASS for source adoption of this exact commit.** The exact-source implementation, part identities, land geometry, E-CAP/E-MARGIN record, sourcing evidence, and stale-artifact boundary meet the stated source conditions. This is neither a PCB, generated-CAD, firmware, first-article, or ordering approval.

## Superseded exact-commit finding

The prior review of `124f6d1236fd6b5613d6fcb7c17eb9e851aa232e` was **FAIL** because three raw JLC stock responses were tracked under `01_docs/research/evidence/2026-09-23-dlc-stock/`, contrary to `01_docs/contracts.md`. The final head removes those tracked raw files. `git ls-files` has no entry beneath that former path and the identical raw responses are ignored under local `06_build/cache/dlc-stock-2026-09-23/`.

The replacement committed observation, `01_docs/sourcing/jlcsearch-dlc-screen-2026-09-23.md`, is compliant: each observation is dated, URL-bound, marked M-IMPORT CITED, explicitly non-authoritative for allocation/order, and records the exact raw SHA-256. I recomputed the local raw hashes and they match the table: TPS62822DLCR `6320acef322e86784ce4648a11afd33ca36787ae37355f832dcb7a02df8513ec`, Samsung `f35c17fc002466eb3c55421d6a99ab1d4d079e56ee9eb22e63f2fa311b38249f`, and Viking `3ee6a16c1bffd99e3db31a291f045161b001db02cbde732630d75aa8b0f700f7`. The source memo now points to that observation and its Samsung HTML SHA is complete and matches the committed bytes.

## Passed source conditions

The three source components are exactly bound in TSX, part dossiers, and exact-parts CSV: three TPS62822DLCR/C473385, one Viking ARG03BTC4533/C2686428, and six Samsung CL21A106KOQNNNE/C1713. The CSV quantities and LCSC values agree with the source instances. The retained inductor, output capacitor, 120-pF feedforward capacitors, divider ratios, and `U_1V8_OK → CORE_EN → U_CORE` sequencing are preserved.

The DLC definition is internally consistent. The TSX and native footprint have the exact TI map `1 EN, 2 FB, 3 AGND, 4 NC, 5 PGND, 6 SW, 7 VIN, 8 PG`. Static comparison finds eight native 0.60 x 0.25-mm pads and an exact Y-axis reflection of the TSX land pattern. The native footprint has no center pad, uses a 2.4 x 2.6-mm courtyard, and leaves NC4 and PG8 without source connections. The added invariants bind pins 1, 2, 3, 5, 6, and 7 for all three regulators.

E-CAP is honestly recorded as an estimate. Each TPS62822 input bank resolves to `2 × 10 × 0.30 × 0.90 × 0.85 × 0.90 = 4.131 uF`, above TI's 3-uF minimum, with the exact Samsung MPN and explicit non-guarantee language. The retained output estimates are compared against the TPS62822 5-uF minimum and nominal 0.47-uH/47-uF table cell. E-MARGIN correctly distinguishes retained PWM-derived DC screens from hard device-pin limits and keeps the 100/40/20-mV dynamic allocations as first-article measurements rather than converter guarantees.

The three rails remain source-topologically consistent: N3V3X `3.243..3.394 V`, N1V8 `1.822..1.899 V`, and N0V9 `0.88..0.92 V` now name TPS62822DLCR while the comments bind the downstream 3.00..3.60 V, 1.70..1.95 V, and 0.855..0.945 V at-pin requirements. The 200k alternative is correctly described as failing to guarantee supervisor release at its low corner.

## Stale-CAD boundary and remaining physical holds

No `03_tscircuit/build`, `04_kicad`, `06_build`, or `08_reviews` artifact is modified by this commit. The candidate memo explicitly says historical raw circuit JSON and native CAD outputs do not attest to the unbuilt source candidate; that is the correct boundary. It neither claims a fresh CJ/parity result nor treats stale generated output as evidence.

The source record preserves rather than creates physical gates: exact JLC placement/centroid, assembled capacitor retention, at-pin ripple/overshoot, startup/brownout/rapid restart, CORE discharge, supervisor release, hot thermal behavior and realized layout remain owed before release/ordering. No firmware conclusion or new pre-prototype measurement prerequisite is introduced by this review.
