# Source-admission audit — 2026-09-22

Audited source commit 124cc621 without running either held rebuild conductor. The owning escape checker reports 20 problems across all 85 selected dossiers (exit 1). This is separate from the source layout-guidance/precedent checker, whose two PASS categories do not test escape. The full 92-dossier check also includes unused historical selections; the selected census is the admission scope reported here.

```text
FAIL ASFL1-24.576MHZ-EC-T: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL FA-238 24.0000MD30X-W5: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL FTSH-105-01-L-DV-K: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL LT3045EDD#PBF: unknown escape condition(s) ['exposed_pad_thermal_vias', 'outward_escape'] (known: ['escape-corridor', 'outward-only-local'])
FAIL SN74AUP3G34DCUR: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL SN74AXC4T245PWR: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL SN74LVC1G04DCKR: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL SN74LVC1G125DCKR: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL SN74LVC1G332DBVR: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL SN74LVC2G74DCTR: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL TPD2EUSB30ADRTR: unknown escape style 'sot' (known: ['bga', 'connector', 'dfn', 'leaded', 'module', 'passive', 'qfn', 'through_hole'])
FAIL TPS26625DRCR: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL TPS3808G09DBVR: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL TPS389018DSER: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL TPS389030DSER: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL TPS6282518DMQR: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL TPS6282533DMQR: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL TPS62825DMQR: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
FAIL TPSM63603V5RDHR: declared tier_required 'jlc_4layer_standard' but the math says 'jlc_4layer_advanced' (qfn @ 0.5mm, 8 escapes worst side) — stale/copied block
FAIL XU316-1024-TQ128-C24: multi-pin part has NO escape block (D-ESC: declare style+pitch, run escape_check)
```

Fresh source-only gates: module-first 3/3, RF contract one applicability decision/port/cross-section/claim, electrical-invariant schema 15/15, source rules 6/6 classes. Label-survival schema accepts zero rows: this proves syntax only, not net-label coverage. Control protocol is explicitly N-A because its source contract is absent. No generated or physical gate is claimed.

Repair ownership: SOL digital dossier task covers selected digital/control/oscillator escape facts; independent admission reviewer covers power packages and the LT3045 tier/condition mismatch. Existing primary footprints and process limits must establish feasibility before any dossier correction; no unconditional tier relaxation is authorized by this report. Sourcing remains 69/85 two-pool. Commissioning hold stays present. Raw selected escape output: 06_build/verification/source-admission-124cc621/escape-selected.log.
