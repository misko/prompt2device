# Independent review — TPS26625 channel-8 current accounting

**Disposition: accounting is source-consistent; it does not qualify a U_SPOKE8.1 route, pad launch, or thermal design.** This review checks SOL packet commit `ca56665da917bc545b90ee7fd1d630b3bd090e19` against current source and TI SLVSDT4F revision F (retained `TI_TPS2662_SLVSDT4F.pdf`, SHA-256 `ff038eaa557fb618f93c0b6276a5ae08d0d3d9fbff1dddf0c45974a89120aefa`). It makes no P1/P2 or source-rule claim.

## Reconciled accounting and segment meaning

`nets.yaml` makes **every** `N12V_PROTECTED` segment `INPUT_TRUNK`: 1.2 mm minimum, 0.2 mm clearance, 2.85 A, with ampacity and hot source-to-spoke drop still owed. `power_tree.yaml` explicitly records the 2.12-A normal allocation, plus eight table-conditioned maximum quiescent currents of 482 uA = 3.856 mA, hence **2.123856 A**. Its one-branch screen replaces one 0.100-A spoke allocation with the conditional 0.159-A value: `2.123856 - 0.100 + 0.159 = 2.182856 A`, conservatively rounded to **2.185 A**. The calculation and labels agree with source.

The 2.85-A hot-continuous allocation and the source-entry 3.4-A / 10-ms excess episode are separate governed screens. They apply at the input/source episode, including stated capacitor-discharge and retry scope; they are not a U1 branch waveform. A routed segment can be treated as channel-8-only only after native copper proves a fanout boundary and shows that no common feed, tap, neck, via, or capacitor recharge path precedes it. The present placement and the geometry-only U1 launch do not provide that proof.

## Device-record check and boundary of inference

TI's electrical table gives **0.145 / 0.152 / 0.159 A** only for 44.2 kohm, `VIN - VOUT = 1 V`, under the table's 24-V test environment. It is a defensible conditional regulated-overload screen, not an all-state maximum at the project's 11.4–13.2 V boundary. The 1.6-A fast-trip threshold has only a typical table entry. The 220-ns fast-trip delay is likewise typical and conditioned on `6 < VIN <= 57 V` and `VIN - VOUT >= 2.6 V`; the same table gives slower conditioned cases. The packet correctly withholds a guaranteed peak-current or pulse-charge inference.

The 10-nF calculation is arithmetically correct: TI describes `tCL(dly) = 512 ms + 3.3 * CdVdT / 2 uA`, yielding about 528.5 ms. It remains an estimate in the overload mode: TI says thermal shutdown can occur first, and thermal auto-retry waits 512 ms after the junction cools below `T(TSD) - 13.5 C`. It cannot establish sustained 0.159-A delivery, repeated-fault duty, or a thermal safe-operating point.

One statement needs careful reading rather than promotion: a local input capacitor *may* supply part of a fast edge, but no present source or packet quantifies its ESR/ESL, charge state, path inductance, or current split. It is a layout reason to preserve the local bypass/return loop, not evidence for an allowed local route-current reduction.

## Exact next qualification evidence for U1

Keep the existing `INPUT_TRUNK` rule unchanged. A U1 current/thermal decision needs a single native-board evidence set that contains:

1. A signed copper-topology map from `Q_IN` through each fanout to `U_SPOKE8.1` and `C_SPOKE_IN8.1`, enumerating every shared segment, neck, via, pad/fillet contact, return branch, and downstream load set. It must leave the 2.85-A classification on all aggregate segments.
2. Hot four-wire resistance/drop and calibrated current captures at the common trunk, channel-8 fanout, U1.1, and `C_SPOKE_IN8`, for simultaneous normal load, one regulated branch fault, startup, fast short, and repeated auto-retry. Include external source/cable impedance and capacitor charge/discharge; report the conditional 3.4-A episode separately.
3. A 70-C ambient thermal qualification using the realized copper, vias, soldered PowerPAD-to-RTN network, and distinct GND6 versus RTN5/EP11 returns. Correlate measured or validated junction/board temperature and transient `I²t` against the captured waveform, including cooling between retries.
4. Fabricated-land evidence for the U1.1 trace contact: mask/paste/fillet geometry, fabrication tolerance, current crowding, and local temperature. Native DRC connectivity and the prior polygon-overlap screen are insufficient.

Until those four artifacts agree, neither the conditional 0.159-A row nor the aggregate 2.185-A source screen supports a local width exception or an electrical/thermal acceptance claim.
