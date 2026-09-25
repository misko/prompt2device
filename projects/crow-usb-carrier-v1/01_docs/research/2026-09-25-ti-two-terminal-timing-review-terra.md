# Independent review — exact two-terminal timing crossings

**Disposition: `3ae04d9fd4cc55277f034401ad21586da23c3e5a` is fail-closed and grants no P1 credit.** This review found no checker acceptance, geometry, or capacity escape. It reviews the isolated TI packet only; no canonical P1 attempt was dispatched.

The new source list is exact-field constrained and accepts only two distinct source/native terminals on one net across at least two modular owners. It checks the complete modular endpoint denominator, one-to-one source/native alias identity, live native pad census/net/layer, owner-region containment, and the exact foreign-region blocker inventory. It requires exactly two P2 pad-to-unplaced-tree obligations, a P3 one-edge connected-native-net lower bound, and a P2 filled-reference duty. Extra source fields, source `PASS`, `bbox`, and non-null `capacity_slots` reject.

The matching witness accepts only the representative terminal and exact P2 duty; its reservation accepts only `{id,kind,branch_id,layer,nets}`. Both are geometry-free. The evaluator reports the reservation `INCOMPLETE` with `capacity_slots: null` and reason “two-terminal source crossing, physical route and filled return unproved”; it never supplies route access, a face-to-reservation contact inference, or capacity credit. Reservation and witness denominators remain one-to-one. The prior three-or-more-terminal list remains separate: using it for a two-terminal row rejects on endpoint denominator, while existing legacy tests still pass.

Focused validation passed:

```sh
python3 -m unittest skills.kicad-pcb.scripts.tests.test_p1_coarse_capacity -q
# Ran 85 tests: OK
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-two-terminal-timing-sol/test_packet.py
# Ran 2 tests: OK
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-two-terminal-timing-sol/build_trial.py
# FAIL; p1_accepted=false; routing_realized=false; 13 global errors
```

The isolated replay accounts for the four exact two-pad timing nets but leaves `adc_timing_xmos_bundle` failed because `AUDIO_EN` lacks its per-net witness; nine independent power diagnostics also remain. The README's stated `unittest discover -s ... -p test_packet.py` command fails here because the packet directory is not importable; use the direct `test_packet.py` command above. That is a reproducibility documentation defect, not a checker fail-open.
