# ADR-0003 — isolated-input protection and spoke-power topology

Status: accepted for first-article source; physical qualification owed
Date: 2026-09-01

The carrier accepts regulated, protected, galvanically isolated 11.4–13.2 V at
J9. It does not implement PoE or Ethernet and does not create the safety
isolation barrier. Eight branches independently feed the pods and preserve the
parent connector pin identity.

Each branch uses exact Littelfuse `1812L035/60MR` as the first-article
resettable protector. The 2024 manufacturer table gives 0.35 A hold and 0.70 A
trip at 20 C, 0.20 A hold at 70 C, 0.16 A hold at 85 C, and 1.700 ohm `R1max`.
The shared contract therefore permits a carrier trip ceiling of 0.70 A while
retaining the 0.10 A continuous spoke requirement.

The delivery proof does not apply common devices at branch current. It charges
0.200 ohm of input PPTC, PFET and common-copper budget at a rounded 1.0 A trunk
bound, deriving 11.16 V at `12V_PROTECTED` after the required 20% margin. It
then charges 2.200 ohm of branch PPTC, per-spoke copper/joints and output-header
budget at 0.10 A. The resulting 10.896 V carrier-header floor is 96 mV above
the 10.8 V contract floor. The cable contract separately requires at least
10.5 V at the pod after the qualified maximum drop.

Protection is two-tier: the carrier part covers cable and pre-pod faults; the
pod's `0ZCJ0010FF2E` covers downstream-board faults with 0.10 A hold and 0.25 A
trip at 23 C. The carrier's 0.70 A trip bound is below the Belden 6541PA 22 AWG
2.2 A-per-conductor rating, the 7 A `43030-0007` contact rating and the carrier
1.0 A `POD_POWER` trace class. Those comparisons screen continuous capacity;
they do not prove fault clearing. `1812L035/60MR` is rated for 10 A maximum
fault current, and its 0.15 s maximum trip point applies only at 8 A. The
selected COTS source must therefore be characterized at no more than 10 A
prospective short current, and no 8 A installed-harness test is authorized.

This selection is not field-qualified. Exact cold/hot resistance, eight-port
steady loading, inrush, source foldback, branch/common-PPTC selectivity,
one-short/seven-healthy behavior, fault energy and recovery time must be
measured before any order-ready claim.

J9's exact source-phase assembly is Molex `43650-0200` plus `43645-0200`, with
red `214761-2122` and black `214761-1122` factory-precrimped 150 mm 18 AWG
leads carrying `43030-0038` contacts. HellermannTyton `113-00022` / `T18MR0C2`
provides internal restraint only after the Molex-required 12.70 mm minimum
unconstrained wire. The free ends are tinned pigtails to the protected COTS
12 V appliance output; J9 has no cable gland and is not a PoE boundary. The
pair is polarized, shrouded, and positive-latching, not described as keyed.


## 2026-09-13 complexity-weighted U_BUCK decision

Retain AP63205WU-7 as the fixed5V converter. Its complete local external support
inventory is nine: D_BUCK_IN, C_BUCK_IN/IN2/IN3, C_BUCK_BST, L_BUCK and
C_BUCK_O1/O2/O3. Ports are12V_PROTECTED input,5V_BUCK output and common GND.
Native source confirms direct EN/VIN and fixed-output FB bindings: no external
feedback divider, compensation, switch transistor or enable resistor is omitted.
DS41326 Rev3-2 describes integrated switching MOSFETs/current-mode control and
internal compensation; its fixed5V application supplies the local boundary.
Nine is below the unchanged ten-support threshold, so a complexity rationale
is used, not a fabricated module survey or module-failure assertion.

The complete outside boundary is explicit: J9, F_IN, Q_IN, D_IN, D_QIN_GS and
R_QIN_G implement the shared protected12V input for both buck and all eight
spoke feeds. J1..J8/F1..F8 belong to those parallel spoke branches. Those parts
are retained whether5V conversion uses a module or this IC. Downstream5V loads
and rail conditioning (D_HOLD, Q_PRE/Q_PRE_EN with bias parts, hold capacitors,
U_PWR/U_AUDIO monitoring, discharge control, LT3041 and its supports) remain
outside the converter ports and remain required with either implementation.
They are explicitly enumerated outside the252-ref ADC/front-end boundary
in ADR0001 and remain required shared dependencies. The converter inventory includes its reverse-isolation
diode and all six power capacitors, even though some modules would integrate
some of them. No selected subset is used to get below threshold.

This small fixed-output implementation uses the existing board and avoids an
additional module mounting/interconnect/height boundary. The protected isolated
12V appliance and MCHStreamer remain COTS modules; no bare mains/PoE/USB
replacement is introduced. No new stock search or claim that an unexamined5V
module fails a binding requirement is made. Thermal, EMI, startup/hold timing
and current limits retain the existing route and first-article obligations.
