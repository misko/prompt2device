# Independent review: ADC8/J8 physical-cell lower bound

**Confirmed: current-schema physical cells are UNSAT for the complete `analog_ch8` denominator without an explicit J8 mechanical/outline exception or a connector/outline redesign.** This is a source-authority conclusion only; it provides no P1/P2, route, return, or capacity credit.

I reran SOL commit `c7c1b906`'s `probe.py` against its pinned integrated board SHA-256 `0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93`, current floorplan SHA-256 `c2a6562c…c4c4ecd6`, modular-plan SHA-256 `75c3a517…e3fc35dc`, P1 source SHA-256 `191e5580…050e82a3`, and checker SHA-256 `e0609241…f82a0eb6`. The replay passed its drift guards and reproduced both expected rejections.

The board has 569 footprints, the frozen 27 fixed references, and exactly 36 unique `analog_ch8` members, including J8. Current authoritative region facts are `analog_ch8=[179,42,201,84]`, `analog_ch7=[157,42,179,84]`, `audio_clock_tdm=[145,72,190,99.84]`, `usb_vbus_sense=[195,62,220,82]`, and `usb_frontend=[200,35,238.5,40]` mm. The native outline is `[20,20,240,140]` mm.

J8's full physical envelope is `[198.875,19.955,216.268081,34.495]` mm and its body is `[198.891919,19.975,216.268081,34.475]` mm. It is fixed, has 12 pads (all beginning in-board at y=23.260), but its full envelope is 0.045 mm and its body 0.025 mm above the outline. The minimum J8 rectangle therefore fails `_physical_cells` with `analog_ch8_j8: physical cell off board outline`. Clipping it to y=20 instead produces `J8: native footprint/pad leaves physical cell analog_ch8_j8`.

This excludes every in-outline rectangle workaround: a cell that contains the required J8 envelope necessarily has y1 <= 19.955, while an allowed cell requires y1 >= 20.000. Splitting the 35 other members, changing their source regions, or using disconnected same-owner cells cannot alter either bound. The 36 minimum per-member cells have zero other native full-envelope overlaps, so this conclusion is specifically the J8 outline condition, not a hidden component collision.

An edge exception is not justified by this screen. It must be narrow and identify J8, the allowed body/courtyard overhang, fixed pose, mating/edge registration and pad-access evidence. Absent that mechanical authority, no typed physical-cell schema change should be promoted. Even after such an exception, the packet records 11 channel-8 members with 12 foreign-region incidences, so a coupled regional recut or placement repair remains required.

Verification run:

```sh
python3 01_docs/research/2026-09-25-ti-adc8-exclusive-cell-unsat-sol/probe.py
```
