# Input protection repair disposition

Status: source candidate implemented; electrical and source-policy checks pass.

The existing `2920L330/24DR` is not an admissible 70 C input protector for the
2.185 A one-fault screen. Littelfuse publishes only 2.25 A hold at 70 C, leaving
65 mA (2.97%) before tolerance, enclosure heating, or source variation. Its
temperature table is also explicitly reference guidance rather than a
production minimum.

The preferred replacement architecture is a non-resettable 4 A, very-fast
surface-mount fuse, provisionally Littelfuse `0451004.MRL` from the 451 series.
The manufacturer requires the usual 25% continuous-current derating, and its
temperature curve is an additional derating. At 70 C the plotted temperature
factor is approximately 95%, so the engineering continuous screen is
`4 A * 0.75 * 0.95 = 2.85 A`, 0.665 A (30.4%) above 2.185 A. The exact curve is
graphical rather than a guaranteed numeric table, so this is a design screen;
first article still measures fuse temperature and connector voltage at the
full operating load. A 3.15 A member is rejected because the same calculation
leaves too little hot margin.

This upstream fuse is deliberately not expected to open for one regulated
spoke fault. The TPS26625 branch regulates to the datasheet's 0.145–0.159 A
24 V/1 V-drop table screen while the input fuse remains intact. The input fuse
instead clears catastrophic common-trunk or TVS failures when the compliant
external source can supply sufficient fault current. Exact minimum clearing
current and time remain a source-load-line and first-article test because the
product does not specify an external supply MPN.

The existing SMBJ15A defines only a component pulse envelope: 15 V stand-off,
16.7 V minimum breakdown, and 24.4 V maximum clamp at 24.6 A for the stated
10/1000 us pulse. It does not establish an IEC, automotive, lightning, or
continuous-overvoltage rating. The allowable connector contract remains
11.4–13.2 V continuous. Any positive transient claimed absorbable must be
bounded to the SMBJ15A pulse-power/current curve and energy, the fuse I-squared-t,
the DMP6023LFG-13 60 V VDS limit, the TPSM63603 36 V recommended input limit,
and TPS26625 60 V input limit. The 24.4 V tabulated clamp is below every active
part's absolute input voltage, but this alone does not prove pulse energy or
temperature. Negative connector voltage is blocked by Q_IN; no negative-surge
waveform is claimed.

The current Littelfuse endpoint returned HTTP 403, so the immutable local copy
is the manufacturer-authored PDF mirrored by Fuse-Tech. Its exact 4 A row,
voltage/interrupting rating, time-current curve, hot derating curve, package
drawing and recommended land were reopened. Current exact identity and active
status were cross-checked independently against DigiKey and Farnell. The PDF
hash, exact dossier, native/source footprint, TSX replacement, power-tree
screen and surge contract are included in this candidate.
