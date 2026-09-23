subject: crow-usb-carrier-v1 Coilcraft inductor source candidate
date: 2026-09-23
reviewer: independent SOL agent /root/crow_stocked_opa_crystal, source and physical land
context-given: full-tree
source_commit: 1b2eb6e380fd5489754cb2e831a3c3486b6eafcc
board_sha256: not-generated (source-only)
design_verdict: SOUND (source/land delta only)
order_verdict: BLOCKED-SOURCING

# Independent review: stocked Coilcraft TPS62825 inductor candidate

Date: 2026-09-23 03:44 UTC. Candidate `1b2eb6e3` against parent
`5ea267d3` in isolated worktree `crow-stocked-inductor-candidate`.

**Verdict: ACCEPT as a source and exact-land candidate only.** It does not
qualify the complete TPS62825 power stage, PCB placement/routing, EMI,
thermal rise, or fabrication release.

## Evidence checked independently

- The retained [Coilcraft XFL4015 primary sheet](https://www.coilcraft.com/getmedia/84927b8b-f089-421b-a7f4-a0fa23afe908/xfl4015.pdf), Document 769-1/2 dated 2026-03-10, has SHA-256 `6535ab70d0ef65ba03d4b0800e206fc7867f26464e2d9dfd5dd931a2bcb0c7c1`, matching the new dossier. Its exact `XFL4015-471ME_` row is 0.47 µH ±20%, 8.36 mΩ max DCR at 25 C, 89 MHz typical SRF, 3.5/5.4/6.6 A for 10/20/30% inductance drop at 25 C, and 9.1/11.2 A for 20/40 C temperature rise in Coilcraft's test setup. Its ordering note defines trailing `C` as the 7-inch machine-ready reel; this closes `XFL4015-471MEC` against TI's electrical family name.
- The retained [TI TPS62825 primary sheet](https://www.ti.com/lit/ds/symlink/tps62825.pdf), SLVSEF9I Table 8-5, recommends `XFL4015-471ME` at 0.47 µH / 6.6 A / 8.36 mΩ and about 4×4×1.6 mm. TI's example BOM lists `XFL4015-471MEB`, another packaging suffix of the same electrical part. The candidate dossier correctly distinguishes these identities.
- Coilcraft Document 769-2 page 2 visually shows 0.98×3.4 mm recommended lands on 2.37 mm pitch. The TSX authored pads are x=±1.185 mm, y=0 and 0.98×3.4 mm. `pcbnew.FootprintLoad` independently parsed the new KiCad footprint and returned pad 1 at (-1.185,0), pad 2 at (+1.185,0), both 0.98×3.4 mm. The TSX and native land agree. The manufacturer's top-view mark identifies the start/short lead and directs high-dv/dt to it for lowest EMI. The candidate designates pad 1 as the start lead on its marked side, and each L_U_* source connection assigns pin 1 to its U_*_SW node; assembly rotation and realized current-loop geometry remain to be checked.
- A fresh direct [JLC component endpoint](https://jlcpcb.com/parts/componentSearch?searchTxt=C18221164) POST for exact C18221164 at 2026-09-23 03:43:20 UTC returned Coilcraft `XFL4015-471MEC`, SMD 4×4 mm, extended library, **3,047 stock / 3,008 presale**. The candidate's earlier 3,051 observation was time-accurate but has already moved. Both are above three per board × five boards + the user-required 150 extra = **165**. Stock remains an observation, not uploader allocation.
- A fresh `tsci build --disable-pcb src/crow_carrier.tsx` exited zero and generated 493 source components, 1,627 source-port records, 1,498 source traces and zero `*_error` records. All three `L_U_1V8`, `L_U_3V3X`, `L_U_CORE` carry exact `XFL4015-471MEC/C18221164`; their pin-1 nets are respectively `U_1V8_SW`, `U_3V3X_SW`, `U_CORE_SW`, and pin-2 nets `N1V8`, `N3V3X`, `N0V9`. Comparing candidate generated ports to the tracked build JSON shows **zero pin-net differences**. The tracked build JSON is older than the parent source for OPA/crystal identities, so its twelve identity differences comprise those nine prior source selections plus exactly these three inductors; the commit diff against `5ea267d3` itself changes only the three inductor instances and exact-parts CSV row. No new circuit error diagnostic appears.

## Unclosed gates

The candidate's 1.79 A screened peak is below the Coilcraft listed Isat points, and the typical L(I) curve is plausible at that load; neither is a guaranteed hot minimum nor a board thermal result. Coilcraft itself calls its Irms temperature rise reference-only and board dependent. The native mark does not prove that the assembled part will be rotated so its physical start lead is on SW; inspect CPL/first article. Prove switch-loop escape, local copper temperature, EMI, and 2.2 MHz filter behavior in the realized layout. The base source still has **2×47 µF per TPS62825 output**, whereas TI Table 8-3's 100 µF cell is blank; the separately pending one-capacitor candidate must be composed and reviewed before claiming the complete LC matrix checked. Keep the D5 admission hold until all remaining parts and assembly evidence close.
