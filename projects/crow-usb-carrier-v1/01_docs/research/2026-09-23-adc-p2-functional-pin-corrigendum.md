# ADC P2 functional-pin corrigendum

This note corrects a diagnostic mapping in the preserved [ADC P2 layout-scope audit](2026-09-23-adc-p2-layout-scope-audit-terra.md), whose original tracked bytes remain SHA-256 `a907c8c42cf4d42b91dee06fea371f4882d48b9a25de2eab708876b55914470e`.

The retained ADC authority assigns AVDD to pin 1 and IOVDD to pin 19. The prior diagnostic table treated IOVDD as pin 1 and described AVDD as “1 or 19”; those are not functional-pin measurements. Corrected IOVDD spans from capacitor pad 1 to the owning pin 19 are:

| Device | 100 nF | 10 uF |
|---|---:|---:|
| `U_ADC_A` | 11.982 mm | 14.589 mm |
| `U_ADC_B` | 11.658 mm | 8.580 mm |

These are diagnostics only, not limits or pass/fail evidence. AVDD must be remeasured against pin 1 by the source owner. The updated temporary audit is SHA-256 `4f945dc2ec16a842709a3b4a3f9df3d86294bcf7e33d84ef2db89be5613c5d95`; its appended corrigendum preserves the old hash above.

The rejected full-cell patch `264e37…` used the wrong mapping, was never committed or generated, and creates no source, board, attempt, graph, or acceptance state. The valid 17-ref reset/VMID subset remains a 16/16 predicted numeric result only. Corrected full-cell geometry has not been admitted.
