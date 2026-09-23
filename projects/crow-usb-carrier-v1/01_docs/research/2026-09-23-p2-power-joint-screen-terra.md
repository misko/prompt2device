# TPSM63603 joint C_OUT1/C_IN2 screen

Read-only, in-memory corrective screen against board SHA `c3d906591a343aea8949687c05c0f5ff4372e982c5af70a04df4828b7409fd93` and the 13-pose source hypothesis. The prior hypothesis remains a failed preserved candidate.

Predicate: front-courtyard bounding boxes derived from F.CrtYd graphics, inflated by 0.25 mm, plus different-net pad-edge separation greater than zero against all footprint pads after **simultaneously** applying all 13 owned poses and holding all unowned/fixed refs at their input positions. This is a placement screen, not a manufacturer distance criterion.

Result: no legal C_OUT1 pose was found in the current TPSM63603 output-side local cell scan `(x=48..56, y=91..101 mm, 90°)` under that joint predicate; therefore there is no full legal 13-pose candidate from this bounded screen.

The residual geometry is concrete:

* Failed original C_OUT1 `(52.600,96.100,90)` has courtyard `[50.875,93.325]–[54.325,98.875]`; C_IN2 `(54.000,97.500,0)` has `[51.675,95.875]–[56.325,99.125]`. They overlap, and `C_OUT1.1` N5V_BUCK and `C_IN2.1` N12V_PROTECTED have zero pad-edge separation.
* A pad-clear alternate, C_OUT1 `(53.500,95.500,90)` with C_IN2 `(55.000,96.000,90)`, has 0.225-mm different-net pad edge, but its courtyards overlap: C_OUT1 `[51.775,92.725]–[55.225,98.275]`, C_IN2 `[53.375,93.675]–[56.625,98.325]`. It is rejected by the required +0.25-mm predicate.
* Retaining C_OUT1 `(53.200,92.700,0)` is also invalid once the proposed FB-top is present: its N5V_BUCK pad meets `R_BUCK_FB_TOP.2` BUCK_FB at zero edge, and its courtyard `[50.425,90.975]–[55.975,94.425]` intersects the proposed FB-bottom courtyard `[48.545,90.805]–[50.455,91.795]`.

The constraint is the output/control band bounded by the proposed control satellites and the retained input bank, rather than an ADC or other-block neighbor. A source-authority allocation must choose which currently power-owned island moves (C_IN2, C_OUT1/C_OUT bank, or the feedback/control satellites), then rerun both the existing numeric rows and the joint predicate. No conclusion of geometric impossibility outside this bounded cell is made.
