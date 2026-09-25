# One bounded channel-8 TPS26625 support-group placement

**Verdict: reject this candidate against the proposed 2.5 mm direct pad-copper-gap research target.** The target comes from Terra's six-member authority at `a2ddd7b6` (`2026-09-25-ti-tps26625-ch8-support-group-terra.md`); TI itself specifies qualitative placement/loop guidance, not a 2.5 mm limit. This result is a rejection of the one tested layout, not proof that a different placement or a deliberately routed GND/RTN return loop is impossible.

`probe.py` source-generates the complete 569-footprint TI integrated board from the pinned frozen source/netlist and the reviewed placement union. It preserves the prior `C_ADC_AC8N1` (198,59.65) and `R_B8P` (193.75,60.8) poses and moves exactly the six named group members:

| Reference | Candidate center (mm), rotation |
| --- | --- |
| `U_SPOKE8` | (190.00,47.50), 0° |
| `C_SPOKE_IN8` | (189.75,44.00), 0° |
| `C_SPOKE_OUT8` | (194.20,46.70), 0° |
| `R_SPOKE_ILIM8` | (194.00,49.50), 0° |
| `C_SPOKE_DVDT8` | (185.80,48.90), 0° |
| `R_SPOKE_UVLO8` | (185.80,46.80), 0° |

All six retain their `analog_ch8` source owner, lie wholly inside its rectangle, have no native full-envelope collisions or foreign-cell intersections, and preserve native pad number/net/layer/shape identities. All other footprint poses and all 27 P1-fixed refs are unchanged. The generated unfilled board SHA-256 is `895a608c242c99eda00805364c1795160e871b12dfff1d69849a64b5b76a8020`.

Exact native F.Cu pad-shape gaps in this pose (mm):

| TI-named contact | Gap | Contact | Gap |
| --- | ---: | --- | ---: |
| U.1 IN → C(IN).1 | 1.655273 | U.6 GND → C(IN).2 | **3.661193** |
| U.10 OUT → C(OUT).1 | 1.050108 | U.6 GND → C(OUT).2 | **3.186949** |
| U.7 ILIM → R(ILIM).1 | 1.512450 | U.5 RTN → R(ILIM).2 | **5.563658** |
| U.8 dVdT → C(dVdT).1 | **5.619506** | U.5 RTN → C(dVdT).2 | 1.747740 |
| U.2 UVLO → R(UVLO).2 | 1.720274 | U.1 IN → R(UVLO).1 | **2.741088** |

PowerPAD.11 (`SPOKE_RTN8`) is 3.636474 mm from R(ILIM).2 and 2.615660 mm from C(dVdT).2. The **first decisive pair** is U.6 GND→C(IN).2: the input supply contact passes, but its return contact misses the proposed ceiling by 1.161193 mm. These are pad-to-pad copper-shape separations, not routed path lengths or loop-area proofs. U.6 and the two bypass return pads are `GND`; U.3/.5/PowerPAD.11 and the ILIM/dVdT returns are the distinct `SPOKE_RTN8` net. The candidate does not establish the required local RTN island, GND/RTN route topology, high-current paths, or thermal copper.

The previously reviewed 0.20 mm ADC8N local route remains connected from `C_ADC_AC8N1.2` to `C_ADC_CM8N.1`, with 0.200001 mm clearance to `usb_vbus_sense` and 0.205001 mm to the nearest nonendpoint native envelope. Its filled In1.Cu GND return is continuous over the entire route ribbon. Full archived `.kicad_pro`/`.kicad_dru`/POFV/V-PROCESS replay reports **199 violations and 499 opens** for both baseline and this candidate, with +0/−0 issue identities and no V-PROCESS failures. The unchanged opens do not supply the missing spoke loops or complete ADC8N net.

Reproduce with `python3 probe.py`; the pinned frozen TI packet must exist at the path in the script. The committed filled board is the sole native artifact. Its byte hash is observational because generated rule-area UUIDs drift; the script checks source SHA, native identities, rule profile, and issue-set delta. No canonical source, P1, or P2 promotion follows from this research packet.
