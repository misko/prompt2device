# P-LAND native kernel author result — NOT ACCEPTED

This bounded authoring task is incomplete and must not be adopted as a public
P-LAND repair. `land_witness.py` is a concrete pcbnew loader/native-shape
candidate kernel, but it does not yet implement native rule-area evaluation,
the prescribed adaptive 30 um sample construction, local/footprint override
precedence, or a complete maintained native fixture matrix. Its two-test T1
suite only covers parser controls and is not evidence that those missing guards
are closed.

Input audit completed before the first source edit: envelope SHA-256
`685e0425178ef2c62ca57a56deedecd62c0468d0fcefbdb1f64b9e244b40db43`;
all 666 packet members and all 483 preimages (470 frozen) matched size and SHA.
Private durable audits are under `/tmp/pland-native-kernel-20260910T223440Z/`.

The independently rerun native entry used the exact accepted complete fixture
on private copies with `--severity-all --all-track-errors`: base has 0 physical
findings and 0 opens; hostile has exactly two clearance records, Track TARGET
to X1.3 and X1.4, and 0 opens. This entry did not use `--exit-code-violations`,
so its actual return code is 0. Full JSON/stdout/stderr are retained privately.

Implementation measurements retained all outcomes: the first reduced temporary
fixture failed (base rc5; transient fixture itself was deleted by its temporary
directory, but its full log remains); 2/2b found missing candidate Track class
attributes; 2c was an IndentationError; 2d improved to a base native witness
and hostile rejection on the exact fixture. The final parser T1 passed 2/2,
including one known-bad. `escape_check.py` and `t1_escape_tier.py` retain their
required SHA-256 values exactly.

Changed live paths are `land_witness.py`, `t1_land_witness.py`, their two
contract/readme homes, and the compact handoff. The final input mutation
inventory names the three originally packeted administrative/contract files;
all other 663 packet members remain byte-identical. No board, source, routing,
checkpoint, model, review, release, or frozen executor was changed or rerun.

`pcb_flow.py handoff` and `validate` both returned 0 after the compact handoff.
The result remains an explicit blocker pending a fresh, complete native-kernel
implementation and later public integration/canonical restart.

## Resumed implementation update

The initial close was rejected and this same task resumed before its original
deadline. The source was rebased onto the verified native prototype structure:
strict `.dru` s-expression/condition parsing, actual native rule-area capsule
checks, preserved pad lifetimes and physical/copper/noncopper/unreadable census,
native start containment, one-layer candidate `PCB_TRACK` shapes, and final
`SHAPE.GetClearance` pairs. The production library no longer imports
`escape_check.py`; it owns the project clearance reader and adaptive 30 um
point generator. Obstacle local precedence now follows PAD optional then
FOOTPRINT optional; a nonzero selected local value is board-minimum clamped,
explicit zero falls through, and custom below-board minima are named rejected.

The maintained T1 now safely reopens the immutable accepted fixture archive,
rejecting links, traversal, duplicates and non-files. It verifies library base
`VALIDATED_CONSTANT_WIDTH_WITNESS`, hostile `NO_VALIDATED_WITNESS`, plus fresh
native CLI base rc0/0 and hostile rc5/exact two Track-to-X1.3/X1.4 findings/0
opens under `--severity-all --all-track-errors --exit-code-violations`. Final
T1 is 3/3 with one known-bad; pycompile passes. `t1_contracts` and
`t1_gate_contract` both fail only their existing untracked-file governance
ratchet in this unadopted worktree, with full logs retained.

The adopted 36-station archive was also exercised. A native composed class is
resolved as the maximum of its declared scalar members for the clearance
baseline only; `NetClass` expression comparisons remain fail-closed. With that
native scalar handling, base is 18/18 witness and hostile is 18/18
`NO_VALIDATED_WITNESS`. The maintained T1 reopens that archive safely and
asserts the full 36-result matrix. A focused known-bad also proves a B-side
area term in a width condition is rejected before Boolean partial folding.

The final focused T1 is 5/5 with two known-bads. Root's independent baseline
comparison corrects the earlier contract-suite attribution: its five failures
are inherited and identical on HEAD and live (jlc_pcba_availability G-RED,
commission_project G-COVER, project_report_audit G-COVER, and enclosure_layout
audit G-COVER/G-RED); no out-of-scope gate changed. Fixture extraction now uses
non-deleting harness scratch paths, verifies archive SHA/member safety, and
retains native JSON/stdout/stderr/argv/rc beside the exact fixture copy.

Final focused validation is 6/6 with three known-bads. It includes a native
circle control: the evaluator's 0.220 mm circle-to-track gap rejects a private
0.221 mm target-only clearance rule, where the retained polygon estimate
0.221921 mm would have falsely accepted.
