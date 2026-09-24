# Independent review: isolated XU PLL route probe

## Verdict

**PASS as a useful local `PLL_0V9` routing feasibility probe; FAIL for PLL
filter/return acceptance.** The 0.20-mm filtered-node route clears the fixed
C45/C39 pad gap and reaches U_XU.41 without a signal via, but FB_PLL has no
N0V9 input route and the capacitor returns are plane-via stubs rather than an
extracted direct local path to U_XU.42/device ground.

Reviewed saved board:
`/tmp/crow-xu-pll-route-sol/04_kicad/crow_carrier.kicad_pcb`, SHA-256
`6d3edf8bbdf2e48a5fab6b2ec3aaa063e67ad1a3fadbb98c007d19ce1315b075`.

## Reproduced copper facts

There are seven `PLL_0V9` F.Cu tracks, all 0.20 mm and no vias. They connect
`U_XU.41 (216.1625,103.0)` through `(217.2,103.0)`, up to `(217.2,101.9)`,
then east to `(219.52,101.9)` and into `C_PLL_100N.1`; that filtered node also
connects to `C_PLL_1U.1` and `FB_PLL.2`. Thus the desired *downstream* node
is contiguous and no N0V9 copper bypasses the bead on this probe.

However, `FB_PLL.1=N0V9` has **zero N0V9 tracks**. The filter has no actual
upstream supply entry, so it cannot demonstrate that FB_PLL is the sole N0V9
entry when the rest of the rail is routed.

The C45/C39 passage is physically clean for this diagnostic route. The
0.20-mm horizontal segment is at y=101.9; `C_XU_VDD_45.1` ends at y=101.36
and `C_XU_VDD_39.2` begins at y=102.44. Its nominal copper-edge spacing to
each pad is 0.44 mm. Native DRC reports only the four intentional dangling
TDM ends, not a clearance/width/courtyard finding. This establishes local
passage feasibility, not a source-specified clearance margin or route
acceptance.

`C_PLL_100N.2` reaches `(220.48,101.9)` and a GND via; `C_PLL_1U.2` reaches
`(220.48,106.0)` and another GND via. The only nearby U_XU ground evidence is
an EP/ground route to a GND via at `(208.5,103.1)`. The saved In1 GND plane may
connect those vias electrically, but no extracted copper/plane current path
shows each capacitor ground side returning directly and shortly to
`U_XU.42=(216.1625,102.6)` or device centre ground. This does not close XMOS's
ground-return requirement.

## Source boundary and required next evidence

XMOS XM-014532-PC v2.0.0 requires PLL_AVDD to be isolated from noisy supplies
and filtered locally, and calls for direct/short decoupler ground paths. It
does not publish a 0.20-mm width, C39/C45 clearance number, via count, or
capacitor distance limit. The probe's width and gap are therefore engineering
geometry facts only.

Before any admission, supply exact-hash evidence that `FB_PLL.1` is connected
to N0V9, FB_PLL is the sole entry to the downstream node, and no hidden plane
or copper branch bypasses it. Extract both capacitor-return paths through the
filled plane to U_XU.42/device ground, then independently review their local
topology and measure PLL_AVDD relative to PLL_AGND on first article. USB/TDM
and full-board route gates remain outside this probe.
