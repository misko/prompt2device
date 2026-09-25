# AUDIO_EN sparse branch-owner pockets: isolated P1 replay

**Research-only, no P1/P2/P3 or route credit.** `build_trial.py` replays on the exact 569-ref 15-part TI board SHA-256 `d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`. It starts from the committed four-crossing timing packet, pins the modular plan SHA-256 `02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8`, floorplan SHA-256 `7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0`, and alias SHA-256 `a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e`. The generated source, contract, and result here make the checker result reproducible without editing canonical Crow files.

The new opt-in `branch_owner_pockets` source rows bind an owner, complete native ref envelope and every pad, exact branch use, and the board/floorplan/alias hashes. The three measured pockets are:

| Pocket | Functional owner/ref | Bounds (mm) |
| --- | --- | --- |
| `audio_pd` | `quiet_power` / `R_AUDIO_PD` | `[22.0,104.0,24.5,106.2]` |
| `audio_ic` | `quiet_power` / `U_AUDIO` | `[21.3,108.2,24.1,110.8]` |
| `iso1` | `analog_ch1` / `U_ISO1` | `[21.3,65.5,25.3,69.7]` |

The validator rejects clipped bodies or pads, any other native footprint/pad, foreign source regions or placement patterns, wrong owner/ref, duplicate pocket assignment, stale hashes, and unused pocket declarations. The unresolved branch requires exact source/native terminal uniqueness and full native net census. Pocket IDs must appear on their exact endpoint and P2 pad-to-unplaced-tree obligation; the representative witness also names its pocket. Pocketed source, witness, and reservation records have exact keys and reject capacity, `PASS`, and route claims. Other unresolved branches keep their legacy behavior.

`result.json` is **`INCOMPLETE` with zero errors**, not acceptance. `AUDIO_EN` retains exactly 11 native/source terminals, ten minimum tree edges, all 11 P2 pad-access duties, a P3 one-connected-native-net duty, and P2 continuous filled In1.Cu GND reference debt. The single exact source-region blocker is still `R_AUDIO_PU.2` intersecting `input_buck`. The checker does not claim that these pockets prove usable placement clearance, trace access, effective capacity, routing, DRC, or filled return; the full physical-cell partition and other circuit-wide reservations remain separate work.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-audio-en-branch-pockets-sol/build_trial.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-audio-en-branch-pockets-sol -p 'test_packet.py' -q
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/kicad-pcb/scripts/tests -p 'test_p1*.py' -q
```
