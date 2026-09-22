---
id: 0008
date: 2026-09-22
status: accepted
---
# 0008 — USB realized-copper path, skew and layer policy

## Context
ADR 0002 fixes the USB endpoint identities and power boundary but deliberately
leaves signal-integrity acceptance open. The XU316 hardware guidance requires
90-ohm differential routing, continuous reference and no more than 1 mm pair
skew. The reversible USB-C receptacle places A6/B6 on USB_DP and A7/B7 on
USB_DN. TPD2EUSB30A pins 1/2 are same-net shunt-clamp leaves, not series
boundaries. Consequently each signal is a tree and a two-terminal chain would
omit physical copper that affects the realized path.

The selected source geometry is the existing 0.410 mm width / 0.150 mm gap
masked pair on the JLC04161H-7628G candidate stack. Its model and order-time
qualification obligations remain owned by `03_src/rules/rf.yaml`; this
decision does not recalculate or broaden that authority.

## Decision
Route USB_DP and USB_DN together on F.Cu over the continuous In1.Cu reference,
with no signal vias. For each corresponding P/N endpoint path, require realized
copper-length spread no greater than 1.0 mm:

- Type-C A contacts: J_USB.4/A6 and J_USB.5/A7 to U_XU.60/59.
- Type-C B contacts: J_USB.12/B6 and J_USB.13/B7 to U_XU.60/59.
- Shunt ESD leaves: U_USB_ESD.1/.2 to U_XU.60/59.

Model these as two single-net tree members with the three path identities
above. Do not claim congruent pad entry, do not treat the ESD device as a
series split, and do not substitute total copper inventory for endpoint-path
length. Any copper edge outside the declared paths, any signal via, or any
matching path whose P/N spread exceeds 1.0 mm is a failure.

## Evidence and consequences
`03_src/rules/nets.yaml` owns the independently graded realized-copper group;
`03_src/route.yaml` owns the coherent F.Cu differential-wave and no-via source
intent. The shared copper-length reader measures the three matching path IDs,
rejects off-path copper and grades the per-net via ban after native routing.

This is a source policy. It does not accept placement, prove that routing is
possible, approve a native board, certify return continuity or impedance, or
replace order-time stack/width confirmation and first-article TDR/USB eye
validation.
