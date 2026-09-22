# Independent source-admission documentation review — 2026-09-22

**Verdict: CONDITIONAL ACCEPT after two wording repairs and the listed final checks**

Reviewed base: `d0c4a4ab752014b9ea97cbcf1e9eb71dd20116a4`  
Reviewed patch: `admission-close.patch`, SHA-256 `32569a0cc58e0424a3c9671ac6dca1ed74a10899b523123096f1015a23fef61f`  
Evaluation: `evaluation.md`, SHA-256 `f41bc2bafabfe0e1f21c72459a094e1954ef47cfea6a72f8465d8e128a04996f`

## Scope conclusion

The six-file patch is appropriately limited to the commission/source-admission ledger. It changes BRIEF from `draft` to `agreed`, passes only `USB-commission`, moves STATUS to the schematic stage, records the checkpoint, and removes the conductor hold. It does not pass `USB-schematic` or any native, placement, routing, provider, allocation, publication, firmware, order, or physical gate.

The BRIEF wording correctly distinguishes the 85/85 design-stage two-pool result from allocation and order-time availability. It preserves the board-specific firmware implementation as owed and unauthorized. Its fabrication row keeps selective LT3045 processing subject to uploader/vendor acceptance and the ADC secondary assembler subject to provider capability evidence before part freeze or placement spend. The admitted mechanical outline remains a reversible initial-placement assumption, not a fit claim.

The cited review files exist for the 493-reference source pages, CKG bank, USB contract, and schema normalization. The journal identifies RF geometry as `NOT_GRADED` only at source while retaining the ordinary USB route contract's nonempty protected group. That is acceptable only with the narrowed early-only RF implementation described in `evaluation.md`; it must never become a realized or `--require-geometry` 0/0 pass.

## Required wording repairs

The conductor does not proceed directly to the native schematic review checkpoint. Its first expected stop is `J-PCBA-PRELAYOUT`, which requires the exact provider request/response before schematic review. Repair these two lines before applying the atomic documentation change:

1. In `STATUS.md`, replace the proposed `next:` text with:

   `next: Commit the reviewed admission checkpoint, run the conductor to J-PCBA-PRELAYOUT, obtain and retain the exact provider availability response, then resume to native schematic review before placement.`

2. In the new journal entry, replace the proposed final `next:` sentence with:

   `Commit this green checkpoint, run bash 03_src/rebuild_all.sh to J-PCBA-PRELAYOUT, obtain and retain the exact provider availability response, then resume and stop at the native schematic review checkpoint before placement.`

These corrections describe sequencing only. They do not require provider contact or an order as part of source admission, and they do not claim that prelayout availability already exists.

## Conditions before hold removal

1. Integrate an independently accepted RF repair that permits `CONTRACT_ONLY / NOT_GRADED` only at the source/early boundary, validates the enabled contract, rejects malformed authority, and fails when geometry is required or realized but absent.
2. On the final source bytes, rerun locked DDA and obtain 493/493 assembly owners, the reviewed USB protected group with six paths, and zero findings.
3. Reopen the accepted 40-page source review and CKG review bindings against unchanged final source identities. Changed bound inputs require new review.
4. Rerun the stated source battery, including schema, early electrical, source rules/policy, RF focused controls, connector SOURCE, selected escape, native footprint-load source checks, modular coverage, and the 85/85 owning sourcing composition with zero unparseable rows.
5. Apply the repaired documentation patch atomically, verify every evidence path and prompt/decision binding, and commit the checkpoint before invoking the conductor.

Subject to those concrete checks and the two wording edits, removing `COMMISSIONING-HOLD.md` and passing only `USB-commission` is supported. The missing native PCB and publication failure remain expected at this stage. No geometry, native schematic, placement, routing, order readiness, provider qualification, firmware implementation, or physical performance is accepted by this review.
