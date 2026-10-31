# One carrier / eight pods — manual placement review

**Historical snapshot.** The user subsequently chose home installation of the
18 through-hole parts for the JLC route, and PCBWay quote-only files were
uploaded. The owner labels and prior permission/next-step statements below are
retained as historical evidence; see [the current session report](../../PCBA-SESSION-20261031.md).

**Draft only: not a vendor-ready placement file.** New scope: 351 SMT
placements (127 carrier + 224 pod), 18 JLC manual installations, 17 user
installations = 386 installed parts. The JLC manual operations are 16 Amphenol
RJHSE-5080, one Same Sky PJ-102AH and one RECOM R-78E5.0-0.5. The user
installs one Pico, eight microphones and eight buzzers.

## Format and review

JLC's published pick-and-place instructions require each reference, actual
component centroid in millimetres, side and counterclockwise-positive rotation
for SMT and through-hole parts: https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly
The existing manual schedule binds exact parts, native footprint anchors and
native angles to the released board audit. Anchors are not certified component
centroids and the native angles are not qualified JLC catalog rotations. The
same release already has 25 SMT reference angle offsets, demonstrating that
a native angle cannot safely be substituted for a vendor rotation.

`manual-scope-1c8p.csv` preserves those native anchors, exact identities and
quantities for review. `manual-cpl-template-NOT-UPLOAD.csv` shows the required
field mapping with centroids and rotations explicitly blank. It is deliberately
not a usable placement file. Referencing the native board and verified source
identity does not independently prove JLC centroid or orientation mapping.
Vendor-specific footprint origin, datum, zero rotation, polarity and JLC manual
handling must be established, then compare each placement preview. The original
release and SMT CPL bytes remain unchanged. No independent engineering review or
vendor acceptance is claimed.

## Quote state

The carrier draft remains for five bare boards / five assembled; JLC Economic
offers assembly quantities 2 and 5, and Standard displays custom quantity range
2–5. One assembled carrier could not be represented; no larger build was adopted.
Changing Standard temporarily for inspection was reverted to Economic. Closing
the carrier missing-CPL error caused JLC to advance to its BOM matching screen
with manual parts omitted; this is an incomplete portal state, not approval or
a changed installation decision.

The pod draft retains ten bare boards and now displays eight assembled under
Standard PCBA. Standard proposes JLC-added rails; that setting is conditional,
not an accepted process change. No eight-bare-board quantity was established.
Manual J1 matching has not been restored, so this is not a complete pod quote.
No placement preview, all-in cost, arrival date, cart, purchase or manufacturing
commitment obtained. User scope, protected acoustic handling and user-owned
Pico/acoustics remain intact.

Preferred next step: establish actual manual-part centroid/rotation and the
reviewer/vendor convention; produce and independently review combined BOM/CPL
inputs, then check the vendor placement preview. Separately determine a feasible
1-carrier assembly quote with JLC; 2–5 is what the inspected screen displayed,
not authorization to buy or assemble two. Alternative: separate SMT and manual
pricing only if JLC can explicitly include all 18 manual operations without a
manual CPL; label all missing costs and acceptance. No supplier contact is
authorized by the quote-only instruction.

## Follow-up geometry and one-carrier research

Reopened both native boards using KiCad pcbnew 10.0.4 and retained exact board
hashes, 11 reference anchors, pad coordinates, native angles, layers and F.Fab
shape bounds in `manual-native-geometry.json`. Every one of the 11 footprint
origins coincides with pad 1. For example carrier J101 is at (8, 8.5), and
its eight signal contacts extend to x=15.112 mm; J1 is at (188, 2.2) with the
other numbered contacts at (188, 8.2) and (192.7, 5.2); U10 is at (182, 38)
and its three pins extend to x=187.08. Coordinates are native +Y down. These
are useful evidence that treating footprint anchor as a verified body centroid
would be unjustified, not JLC CPL coordinates. F.Fab is an engineering drawing
layer, and the RJ footprint explicitly describes its outline as conservative;
its box center is not a manufacturer-certified centroid. Native angle zero is
not evidence for the JLC library zero-rotation/pin-one convention.

Sources: official Amphenol P-RJHSE-5080 Rev J drawing
https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/p-rjhse-5080.pdf ;
RECOM exact module and package drawing https://recom-power.com/pdf/Innoline/R-78E-0.5.pdf ;
JLC component data format https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly .
The maker drawings provide mechanical dimensions/pin positions but do not
establish JLC's exact catalog placement origin or rotation mapping. No
manufacturer source or JLC preview was found to certify all three mappings.
A fully reviewed combined file cannot be responsibly produced from these facts
alone. Remain within the explicit no-guessed-coordinates stop.

JLC's official prototype-assembly guidance states a two-board minimum:
https://jlcpcb.com/solutions/pcb-prototype-assembly ; the observed Economic
and Standard controls also excluded assembly quantity one. This is not a
quote for one assembled carrier. No special one-unit exception, alternate
provider quote, or permission to assemble two is established. An exact
1+8 quote through this JLC interface remains unresolved. The 8-pod conditional
Standard draft, ten bare boards and proposed rails remain as recorded above.
No THT file was uploaded, no customer-support message sent, and no order made.

## One-carrier alternative found

PCBWay states an assembly minimum of one board:
https://www.pcbway.com/helpcenter/pcb_assembly_ordering/What_s_the_min_quantity_of_assembly_.html
Its public services list SMT and through-hole assembly. This is a plausible
route to a 1-carrier / 8-pod quote, not a priced offer or proof of the exact
stack, controlled assembly, manual operations, orientation, stock or lead times.
No Crow files were disclosed to PCBWay: prior scoped quote-upload authority
was for JLC, not this different destination. Separate authority is needed before
any vendor submission/contact or uploading the design to another supplier.
