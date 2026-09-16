# CS530x effective-capacitance source record

Retrieved 2026-09-01 from the official Cirrus Logic package:

- URL: <https://statics.cirrus.com/pubs/software/DC5302P_4P_4S_8P_8S-ADC_Schematic_Layout.zip>
- ZIP SHA-256: `2b4f99aad0eb5a562f25aacb8ab5147f4eeadbef7c2e35aea0abc4acb9aabda7`
- inner path: `CS530x Schematic Layout Guidelines.pdf`
- inner PDF SHA-256: `a97e3cfbe311caf603bd56b7aeab189dd38727104168c26bb67dd24add07b62f`
- document: Cirrus Logic, *CS530x Schematic and Layout Guidelines*, July 2025

The load-bearing requirements are in sections 1.6–1.9 (PDF pages 5–6):

| Function | applied voltage | effective minimum |
|---|---:|---:|
| LDO_A_FILT | 1.8 V | 0.8 µF |
| LDO_D_FILT | 1.2 V | 0.8 µF |
| ADC_VMID nominal 0.22 µF position | 1.65 V | 0.1 µF |
| ADC_VMID nominal 2.2 µF position | 1.65 V | 1.0 µF |
| ADC_FILT nominal 0.47 µF position | 3.3 V | 0.22 µF |
| ADC_FILT nominal 4.7 µF position | 3.3 V | 2.2 µF |

The document gives minima but no maximum for these MLCC positions. Increasing
nominal values is therefore a first-article candidate, not an inferred
production stability guarantee. `03_src/rules/power_tree.yaml` charges the
selected ±10% X7R parts by 50% DC-bias, 15% temperature, and 10% lifecycle
loss and keeps LDO startup/stability, VMID settling, reference ripple and THD
as physical holds.
