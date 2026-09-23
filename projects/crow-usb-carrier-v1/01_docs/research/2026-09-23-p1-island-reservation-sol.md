# Crow P1 island reservation proposal — read-only, 2026-09-23

**Disposition:** proposed source change for a later, newly admitted floorplan campaign. No producer, PCB edit, routing, placement acceptance, or attempt-budget reset was performed here. The patch is `/tmp/crow-p1-island-reservation-proposal.diff`; `git apply --check` passes against the current project worktree. It transforms floorplan SHA256 `62be425f350d8d0c9bd33834f99d3d1827e5f190480e4bb75ad95a70830e53af` into proposed YAML SHA256 `26686cd23dd26e945d855c49f6413795519a4ab1b98f191bea9b3aa8fa4106b8`. The measured second repaired-trial board is SHA256 `37b455203fcdae0c20880a94b17a4bcfb61103fa2b8b9df9ecf095c9c97aa519` at `/tmp/crow-p1-repaired-trial-20260923/04_kicad/crow_carrier.kicad_pcb` (identical bytes in the root `06_build/modular/repaired-trial` copy). Its source floorplan SHA256 `084063400a90dcaef9629ba8a98c3839d9ded6dbcb2431f551c2862fe5bc2bcd` matches the rejected first-candidate floorplan; the proposed YAML patch therefore still uses the same geometry. The prior first-board analysis is preserved separately in `/tmp/crow-p1-island-reservation-sol.first-subject.md`.

## Source mechanism and exact proposal

`generate_board_generic.py` calls `placement.legalize` after initial placement. Its `clear_at` evaluates every **floating** footprint against each `placement.forbid` rectangle plus `margin`; an overlap with the tested footprint bounding box rejects that candidate location. Anchors and any future `keep`/`post_anchors` bypass this search. Regions alone provide initial centers and cannot reserve an island.

The patch carries the rejected P1 candidate's 16 fixed can centers, 11 connector anchors, 46 functional support/ADC/ISO seeds, two documentary bank regions, and 120-ring search limit. It removes the cans from the broad `quiet_power` pattern and gives each bank an exact can pattern. It adds three global floating-part exclusions:

```yaml
  forbid:
  - rect: [24, 113, 74, 137]  # left eight-can bank
    margin: 0.25
  - rect: [76, 113, 126, 137] # right eight-can bank
    margin: 0.25
  - rect: [74, 113, 76, 137]  # central 2 mm component-free gap
    margin: 0.25
```

The three rectangles form a continuous 102 × 24 mm component exclusion for floating parts, including the center gap. The left and right named banks are 50 × 24 mm each. The 16 Panasonic can courtyards measured 11.69 × 8.69 mm on the retained native candidate. Their fixed centers yielded courtyard spans x=25.005–72.995 and 77.005–124.995, y=116.105–133.895; nearest-row/column courtyard gaps were 0.41 mm. Pad 1 was 3.55 mm left of every can origin at rotation 0. These are measurements of the rejected candidate, not a fresh trial of the proposed exclusions.

The 11 non-can anchors are J1–J8, J_PWR, J_USB, and J_JTAG. Their retained positions lie outside all three forbidden rectangles; they remain exceptions to `forbid` by design and still need exact native edge, mate, service, and pad/NPTH review. No quiet-power support or ADC-reference part is pinned in the proposal. Future anchors or `keep` refs inside a bank would bypass `forbid` and must be reviewed explicitly.

## Capacity and displacement owed

`modular_plan.json` owns 69 `quiet_power` refs: 16 cans and **53 non-can support** refs. The proposed seed set starts only 12/53 supports explicitly; 41 still start from the broad quiet-power region center. The exact second board has **23** support courtyards intersecting the left bank and **one** (`C_LDO_IN`) intersecting the right bank. Their full courtyard bounding-box area sums are 97.98 and 19.51 mm² respectively; those sums are not the exact overlap areas. All 53 were placed somewhere by the prior legalizer, but the new exclusions must evict those 24 intrusions and preserve a D_HOLD → precharge → bank → LT3045 feed/return path.

The `adc_reference` block owns **64** refs. Only 26/64 have explicit seeds in the proposed source; 38 retain the ADC region-center start. In the exact second board, 56 ADC centers landed in x75–145/y85–113. **Four defined ADC courtyards** intersect the right bank: `C_ADC_START_DELAY`, `Q_ADC_DELAY_DISCH`, `Q_RST1`, and `R_VMID1_BOT` (34.51 mm² of full courtyard bounding boxes). **A fifth ADC footprint bounding box**, `U_ADC_READY_BAD`, also intersects the right bank (41.75 mm² bounding box); its board footprint has no F.CrtYd polygon. Thus five ADC *footprint bounding boxes* intrude, while only four have native courtyard polygons. No ADC box intersects the left bank. This explains the prior five-versus-four discrepancy: the earlier memo counted only existing courtyards on the first subject, and the fifth is a missing-courtyard footprint visible by fallback body/bounding box on the second subject.

The 53 support courtyard bounding boxes total 373.16 mm²; the 58 ADC boxes with courtyards total 266.13 mm². The other six ADC footprint bounding boxes total 510.73 mm², for 776.86 mm² across all 64 when fallback boxes are counted; these fallback boxes are not courtyard clearances. These are coarse bounding-box occupancy proxies, not validated packing loads; they omit clearances, hot copper, thermal copper, verified model bodies, and access. The existing quiet-power seed region is 50 × 29 = 1,450 mm². Its overlap with the left exclusion is 49 × 21 = 1,029 mm², leaving just 421 mm² of that *original* region outside the left bank before clearance. Thus the 41 unseeded support refs cannot be treated as safely accommodated merely because the legalizer finds coordinates; a later campaign must allocate support space across the buck boundary/right-hand LDO slice and inspect the resulting feed/return corridors. The ADC seed region is 70 × 49 = 3,430 mm²; its overlap with the right exclusion is 50 × 21 = 1,050 mm². Nominal remaining area is 2,380 mm², but 64-part adjacency and analog handoff geometry remain unproved.

## What `forbid` does and does not guarantee

The rule rejects a floating pose when the legalizer's **centered bounding-box approximation** overlaps a forbidden rectangle plus margin. It does not enforce the final courtyard polygon directly. On the exact second board, all 53 support parts have F.CrtYd; their courtyard bounding boxes are centered on footprint origins. The 58 ADC parts with F.CrtYd have observed courtyard offsets within 0.20 mm. Six ADC board footprints (`U_ADC_A`, `U_ADC_B`, `U_ADC_DIGITAL_BAD`, `U_ADC_PWR_BAD`, `U_ADC_READY`, `U_ADC_READY_BAD`) still lack F.CrtYd, and their fallback footprint bounding-box offsets reach 1.55 mm. The source courtyard repair already landed at commit `7193695a`; **regenerated native evidence is owed**, rather than another source fix. The 0.25 mm margin is **not** an all-part courtyard/body guarantee, particularly for the stale six and other floating footprints. The next board must be scanned independently for every footprint's actual courtyard/body/3D intrusion.

`forbid` creates no KiCad keepout, copper rule area, route corridor, fill, or physical mating proof. It does not constrain anchors; it does not reserve net-specific escape capacity. The 120-ring search offers candidate positions out to 59.5 mm from a seed and may still fail, or scatter related parts too far for electrical placement. No new generic generator knob is proposed because the existing mechanism expresses the intended floating-part exclusion; the exact geometry gate must judge its result.

## Independent checks before any new P1 admission

1. Begin a **newly admitted** bounded campaign under the existing backtrack/attempt policy. Reopen the accepted schematic/netlist, alias mapping, source generator, and current footprint identities; do not infer reuse from this patch.
2. Generate a scratch native board from the proposed source. Verify 568/568 refs, all 16 can coordinates/rotation/pad-1 polarity, all 11 connector anchors and service-facing axes, and no actual floating courtyard/body intrusion into the three rectangles. Report missing courtyards separately.
3. Recount the 53 support and 64 ADC placements and measure D_HOLD/precharge/bank/LT3045/ADC supply loops, local bypass, differential handoff, return continuity, thermal/Kelvin access, and copper route corridors. A successful legalizer is only a position finder.
4. Run the owning placement, pad-map, model, geometry, and prepared-board DRC gates on the exact candidate. Preserve the connector FULL physical holds and independent P1 review before any P2 or route dispatch.

The first board's default diagnostic DRC and first-trial failure remain forensic evidence in the preserved first-subject memo. The second repaired-trial board measured here is still pre-regeneration for the source courtyard repair. This proposal has no measured generation outcome.
