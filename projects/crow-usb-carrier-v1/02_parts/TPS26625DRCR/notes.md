# TPS26625 spoke candidate evidence boundary

The exact TI SLVSDT4F PDF is retained beside this record. TPS26625 is the
adjustable-OVP, auto-retry, input-and-output reverse-polarity member. The source
uses every required pin: UVLO receives the mandated 1 Mohm feed from IN, OVP
is tied to RTN, SHDN is held high from IN, ILIM and dVdT return to RTN, GND is
system ground, and both RTN pin 5 and PowerPAD pin 11 join the local RTN island.
FLT is the sole unconnected device pin because the pin-functions table
explicitly directs leaving this open-drain output floating when unused.

The electrical table's 44.2 kohm row is 0.145/0.152/0.159 A only under its
stated 24 V and 1 V device-drop condition. The candidate uses that row as a
normal-load engineering reserve against 0.100 A, not as a guaranteed hard-short
or 12 V source-containment number. The resistor's independent tolerance and TCR
expand the screening interval slightly; they do not fix the missing operating
condition.

Section 9.1 calls the 0.3 us reverse-current response typical. Section 9.3.5.2
describes fast-trip behavior, while the timing table gives 220 ns without a
min/max production bound. The 1.6 A comparator entry likewise has no min/max
bound. The 512 ms values are nominal and the overload text adds CdVdT and
thermal dependencies. None is used as a guaranteed transient load on the
shared source.

Open before adoption: exact source MPN and load line/hiccup/recovery; F_IN hot
coordination; every pod startup and output-capacitance state; cable R/L; local
input-bulk ESR/ESL; RTN/PowerPAD copper and junction rise at 70 C; retry-induced
rail disturbance; exact authorized-source allocation and cost; and physical
fault testing with seven healthy spokes operating.
