# Four exact two-terminal TI timing crossings

**Research-only no-credit P1 diagnostic.** The checker now has an opt-in `unresolved_two_terminal_crossings` source list, with matching `unresolved_two_terminal_crossing` witness and reservation kinds. This is admitted only for exactly two distinct native pads on one cross-owner net, one exact source-to-native identity per terminal, both pad/net/layer and owner-region valid. It requires two P2 pad-to-connection obligations, a one-edge P3 connected-net lower bound, filled-reference debt, one exact representative witness and one matching geometry-free reservation. It rejects extra terminals, aliases colliding on one native pad, missing/wrong owner, missing duties, foreign-region inventory drift, geometry, demand, capacity, and source `PASS` fields. The legacy three-or-more-terminal branch schema is unchanged. An admitted record remains `INCOMPLETE` with `capacity_slots: null`; it is neither route access nor P1 capacity.

`build_trial.py` starts from the hash-bound unified P1 research source/contract and its native board SHA-256 `d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`. It adds exactly four two-pad records to the 14-net/54-pad `adc_timing_xmos_bundle`:

| Net | Exact source/native endpoints |
| --- | --- |
| `AUDIO_MCLK_1V8` | `U_TDM_XLATE.6` ↔ `U_XU.23` |
| `TDM_BCLK_1V8` | `U_TDM_XLATE.4` ↔ `U_XU.22` |
| `TDM_DATA_1V8` | `U_TDM_XLATE.7` ↔ `U_XU.107` |
| `TDM_FSYNC_1V8` | `U_TDM_XLATE.5` ↔ `U_XU.20` |

The unchanged nine timing branches and four new crossings have no timing item diagnostics. The full checker still returns `FAIL`, `routing_realized=false`, and `p1_accepted=false`. **`AUDIO_EN` is the remaining timing source blocker**: `R_AUDIO_PD.1` and `U_AUDIO.6` lie west of their `quiet_power` owner region, and `U_ISO1.2` lies west of `analog_ch1`. It cannot receive an honest existing-schema branch or two-terminal record on this board. The missing per-net witness makes allocation evaluation all-or-nothing, producing 13 derivative global representative-witness errors (nine prior branches plus these four crossings). Nine independent power witness diagnostics also remain. Source/contract outputs are hash-bound in `result.json`; no P1 attempt was spent and no canonical placement, route, or contract was promoted.

The current TI schematic/circuit is canonical, but this board and P1 contract are isolated research subjects. Later coupled timing placement and ADC8N route probes do not supply all 14 native routes, effective clearance, pad entry, or continuous filled return. The next system-level repair is exact `AUDIO_EN` owner placement or a separately validated sparse owner-pocket schema, followed by full timing allocation and route/return proof. A two-terminal no-credit record alone does not change timing acceptance.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-two-terminal-timing-sol/build_trial.py
python3 -m unittest discover -s skills/kicad-pcb/scripts/tests -p 'test_p1_*.py' -q
python3 -m unittest discover -s projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-two-terminal-timing-sol -p 'test_packet.py' -q
```
