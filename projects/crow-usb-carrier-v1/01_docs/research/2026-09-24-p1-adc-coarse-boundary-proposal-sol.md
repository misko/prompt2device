# Proposed coarse P1 analog boundary witnesses

The companion [provisional JSON](2026-09-24-p1-adc-coarse-boundary-proposal-sol.json)
is a review proposal, not an active P1 capacity contract. It retains all 18
`adc_analog_boundary` nets and the source's 44 exact ref.pad endpoints per
nine-net bank as the downstream denominator. It replaces the impossible P1
whole-footprint pocket promise with five coarse region-face witnesses per
bank: the south faces of its four 22-mm analog channel cells (y=84 mm) and
a disjoint north-face window of `adc_reference` (y=85 mm). Witnesses name
their owner, region face, bbox, and covered nets. They are **interface
planning windows**, not pad entries, routing endpoints, or proof that all
VMID branches can fit.

The two board-scale F.Cu reservations are `[25,71,112.75,85]` for channels
1–4/VMID1 and `[113.25,71,201,85]` for channels 5–8/VMID2, in mm. The
0.50-mm seam at x=113 keeps the named bank areas disjoint. Each is 14 mm
tall against a nominal nine-slot/5.04-mm demand. The windows touch their
respective channel south-face witnesses and ADC north-face witness at the
y=85 boundary. The ADC region is `[75,85,145,134]`; its internal handoff
from the north face to the two ADC bodies, collars, and VMID bank remains
P2 local. The eastward channel cells' handoffs into bank 2's north trunk
are also P2 local. Their all-pad entries and copper returns remain P3 work.

On the exact live-source isolated board SHA-256
`4849d58d58c984401340e99cfbaf37e68345be34f87bcbd6bc33078ee2867285`,
the existing `p1_corridor_capacity.py` rectangle primitive gives the
following **optimistic, noncontract** F.Cu screen at 0.56 mm pitch. It
excludes each bank's 37 endpoint footprint refs and has no clearance or
pad-access guarantee.

| Reservation | Current native connected width / raw slots | With only verified `placement.anchors` and existing copper |
| --- | ---: | ---: |
| Channels 1–4/VMID1 | 5.875 mm / 10 of 9 | 14.000 mm / 25 of 9 |
| Channels 5–8/VMID2 | 3.575 mm / 6 of 9 | 14.000 mm / 25 of 9 |

No fixed `placement.anchors` body/pad and no existing F.Cu copper item
intersects either proposed trunk. The second column is a capacity ceiling
**if all non-anchor placement in the windows changes**, not a realizable
route. Bank 2's currently intersecting movable refs include its channel
support groups `C_A5N`–`C_A8N`, `C_ISO5`–`C_ISO8`,
`C_OPA5`–`C_OPA8`, `C_SPOKE_DVDT5`–`C_SPOKE_DVDT8`,
`C_SPOKE_OUT5`–`C_SPOKE_OUT8`, `R_IN5N`–`R_IN8N`,
`R_SPOKE_ILIM5`–`R_SPOKE_ILIM8`, `R_SPOKE_UVLO5`–`R_SPOKE_UVLO8`,
and `U_AFE5`–`U_AFE8`, `U_ESD5`–`U_ESD8`. Cross-owner local
floaters in the same reservation include `U_AFE4`, `U_ADC_CLOCK_OK`,
`U_ADC_I2C_XLATE`, `U_FSYNC_FF1`, `U_FSYNC_OR`, `R_ADC_OK_PU`, and
`R_ADC_OK_TOP`. These are P2 placement debts, not verified fixed blockers.
The source seeds for `U_ISO5`–`U_ISO8` are likewise not fixed anchors; their
qualification/placement must be revisited with the bank 2 handoff.

The current ADC-A/B capacitor collars and VMID banks are inside the ADC
reference region and are P2-local obstacles. Native probes documented in
`2026-09-24-p1-adc-vmid-one-change-isolated-sol.md` leave only 1/9 and 3/9
raw slots at the ADC-A/B collar approaches; moving the VMID cells alone
does not improve those necks. Protected connector, power, and XU anchors
are outside both reservations and must stay fixed for this proposal.

Both isolated boards have an unfilled In1.Cu GND zone. No filled reference,
effective line capacity, branch topology, pad pockets, DRC, or independent
P1 acceptance follows. The proposal should remain **INCOMPLETE** until a
source-controlled P2 local-cell arrangement, exact-hash native board,
and separate return/capacity review make the coarse allocation actionable.
