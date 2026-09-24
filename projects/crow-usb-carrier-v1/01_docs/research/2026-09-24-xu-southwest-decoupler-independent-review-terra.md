# Independent review: SOL XU southwest decoupler probe

## Verdict

**PASS only as a bounded four-exit signal/placement geometry observation;
FAIL for adoption as an XU decoupler, PLL, power-return, or P1 result.**

This is a read-only review of SOL commit `1a9554b3` and
`/tmp/crow-xu-southwest-sol/04_kicad/crow_carrier.kicad_pcb`.
The reviewed saved board SHA-256 is
`423b0aa965b6df8791d549c3cbfe7e56fe68bca1028c140671a5801c2420c207`;
the isolated floorplan SHA-256 is
`18a1b565f4737ed771c378646911f3aaf4050c6e5fe779b301a40081c670d3cb`.
No canonical placement, route, or P1 artifact was changed by this review.

## Reproduced native observations

Direct native-board inspection gives these actual candidate pad centres:

| Relationship | Candidate coordinates | Centre-to-centre observation |
|---|---|---:|
| `C_XU_VDDIO_17.1` (`N1V8`) to `U_XU.17` (`VDDIOL`) | `(208.7000,109.3200)` to `(208.7000,107.6625)` | 1.6575 mm |
| `C_XU_VDD_14.1` (`N0V9`) to `U_XU.14` | `(208.0200,112.4000)` to `(207.5000,107.6625)` | 4.7660 mm |
| `C_PLL_1U.1` (`PLL_0V9`) to `U_XU.41` (`PLL_AVDD`) | `(218.0000,108.8800)` to `(216.1625,103.0000)` | 6.1604 mm |

The saved board has 569 footprints and nine zones. Its DRC JSON SHA-256 is
`eee5430eaac2f6be501ca679bcbc950da4a1ae61652e4f06515970586ac190ba`.
It reports four violations, all intentional `track_dangling` findings at the
four diagnostic TDM-strip ends; it reports no schematic-parity finding and no
courtyard violation. The generated POFV log records eight B2 areas/rules.
This supports the claimed narrow geometry screen, not a usable route.

## Power and proximity assessment

`C_XU_VDDIO_17` is materially better oriented for a future supply branch:
its `N1V8` pad faces directly toward pin 17 and the observed pad-centre
separation is 1.6575 mm. This is promising geometry only. The board has zero
`N1V8` tracks and zero `PLL_0V9` tracks. It therefore has no C17 supply path,
no PLL filter path, and no native evidence that either capacitor ground pad
returns directly to U_XU centre ground or a ground pin. Its filled-zone samples
cannot establish that omitted return path.

Moving C14 makes its observed supply-pad-to-pin separation 4.7660 mm, and
`C_PLL_1U` remains 6.1604 mm from `PLL_AVDD`. XMOS XM-014532-PC v2.0.0 gives
qualitative close/direct-return requirements, not a millimetre limit; these
measurements consequently are not manufacturer pass/fail values. They are,
however, unresolved local supply/return obligations. With no supply or return
copper to review, both rows are unacceptable as adopted placement evidence and
must be closed under the source-owned acceptance contract before coordinates
are admitted.

The note's reported C17--U_XU 0.15-mm bounding-box courtyard separation and
the absence of a KiCad courtyard violation show only non-overlap. They do not
establish assembly margin. No additional manufacturer numerical spacing limit
is introduced here.

## Evidence-integrity and next gate

`/tmp/crow-xu-southwest-sol/probe.json` remains a stale earlier-probe record:
it names C17 at `[211.7,109.4,90]`, whereas the reviewed board has C17 at the
coordinates above. It must not be cited as evidence for this southwest board;
the saved-board SHA, direct native coordinates, and DRC JSON are the valid
artifacts.

Before any adoption, produce an exact-hash board with completed paths for
`C_XU_VDDIO_17.1 -> U_XU.17`, `C_XU_VDDIO_17.2 ->` U_XU centre-ground/ground
pin, and the full `FB_PLL/C_PLL_1U/C_PLL_100N/U_XU.41/.42` filter/return.
Archive segment, via, layer, filled-zone, and reference-continuity evidence,
then obtain qualitative independent review as specified in
`2026-09-24-xu-vddio17-pll-acceptance-contract-terra.md`. First-article rail
waveforms are a separate validation step after a design release and board build.
