# TPS26625 channel-8 coupled support-group target

**Scope:** source-bound refloorplan target only.  This does not move a part,
change a canonical source, or establish P1/P2 acceptance.

## Exact authority and membership

The frozen TI netlist is
`06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/06_build/netlists/crow_carrier.net`,
SHA-256 `a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd`.
It identifies `U_SPOKE8` as **TI TPS26625DRCR**, DRC0010J VSON-10 with
PowerPAD.  The retained primary dossier is TI `SLVSDT4F`, SHA-256
`ff038eaa557fb618f93c0b6276a5ae08d0d3d9fbff1dddf0c45974a89120aefa`
(sections 10.3.2, 11, and 12.1; Figure 10-14).

The one inseparable channel-8 eFuse support group is:

| Function | Exact members and net/pin contacts |
| --- | --- |
| eFuse / local reference | `U_SPOKE8`; IN.1=`N12V_PROTECTED`, UVLO.2=`SPOKE_UVLO8`, OVP.3 and RTN.5/PowerPAD.11=`SPOKE_RTN8`, GND.6=`GND`, ILIM.7=`SPOKE_ILIM8`, dVdT.8=`SPOKE_DVDT8`, OUT.10=`N12V_POD8` |
| Input bypass | `C_SPOKE_IN8` 100 nF: `.1`=`N12V_PROTECTED` to U.1; `.2`=`GND` to U.6 |
| Output bypass | `C_SPOKE_OUT8` 100 nF: `.1`=`N12V_POD8` to U.10; `.2`=`GND` to U.6 |
| Current-limit loop | `R_SPOKE_ILIM8` 44.2 kΩ: `.1`=`SPOKE_ILIM8` to U.7; `.2`=`SPOKE_RTN8` to U RTN |
| Ramp loop | `C_SPOKE_DVDT8` 10 nF: `.1`=`SPOKE_DVDT8` to U.8; `.2`=`SPOKE_RTN8` to U RTN |
| UVLO loop | `R_SPOKE_UVLO8` 1 MΩ: `.2`=`SPOKE_UVLO8` to U.2; `.1`=`N12V_PROTECTED` to U.1 |

`TPS26625DRCR` is the exact current MPN; the board's source configuration is
the datasheet's simple IN-to-UVLO resistor arrangement, so there is no
channel-8 OVP-divider component to add to this group.  Here OVP.3 is tied to
the RTN net. RTN.5 and PowerPAD.11 must terminate in the same local RTN
island, while system GND at pin 6 remains distinct.

## What the manufacturer does and does not specify

TI provides these numeric requirements/guidance, none of which is a numeric
component-to-component placement distance:

* C(IN) is at least 0.1 µF ceramic; if the supply is more than a few inches
  away, TI recommends greater than 0.1 µF.
* High-current paths must carry at least twice full-load current.
* The current source already chooses C(IN)=100 nF, C(dVdT)=10 nF, R(ILIM)=
  44.2 kΩ, and R(UVLO)=1 MΩ.  The dossier binds 44.2 kΩ to a 0.145–0.159 A
  overload-current range under its stated conditions.

TI's placement statements are qualitative: put the IN/GND bypass closest to
the pins and minimize its loop; locate R(ILIM), C(dVdT), and UVLO/OVP
resistors close to their connection pins, returning their far ends to RTN by
the shortest trace; keep the ILIM trace short and uncoupled from switching
signals; place the PowerPAD directly on RTN copper.  TI provides **no mm
maximum** for any of these statements.

The current part dossier adds a project-owned `max_mm: 2.5` copper-gap ceiling
for `U_SPOKE8`↔`C_SPOKE_IN8` on `N12V_PROTECTED` and
`U_SPOKE8`↔`R_SPOKE_ILIM8` on `SPOKE_ILIM8`.  It labels both as engineering
ceilings implementing TI's qualitative guidance.  They are not TI limits and
the current source has no corresponding numeric ceiling for C(OUT), C(dVdT),
UVLO, or their GND/RTN return contacts.

## Exploratory target and current review boundary

Treat the six references above as one movable **support group**.  A candidate
must move the eFuse and every listed support component together, retain its
existing functional `analog_ch8` ownership, and prove each paired contact
above with native pad identities and a local RTN island.  The first screen
explored a direct copper-gap ceiling of **2.5 mm** for every listed contact.
That was a deliberately strict *research proxy* extending the two existing
project ceilings; the [reviewed trial](2026-09-25-ti-tps26625-whole-group-review-terra.md)
failed it. It is **not** an adopted source or P2 acceptance rule, and TI does
not supply that number. The current
[evidence rubric](2026-09-25-ti-tps26625-six-member-acceptance-rubric-terra.md)
retains only the existing IN/ILIM project ceilings and requires actual native
routed GND/RTN loops, measured paths and loop areas, and PowerPAD/RTN island
proof for the other contacts.

The same candidate must show: C(IN) and C(OUT) loop areas, short
IN/OUT high-current paths, RTN island/PowerPAD continuity, full native
envelope clearance, and independent route/return/thermal evidence.  It must
also retain the existing fixed J8 pose and cannot use a J8 cell exception as
electrical-locality credit.  This target intentionally does not prescribe a
placement or a region shape.
