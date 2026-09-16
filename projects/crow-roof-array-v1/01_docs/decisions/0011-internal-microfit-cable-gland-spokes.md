---
id: 0011
date: 2026-09-01
status: superseded
---
# 0011 — Internal Micro-Fit terminations behind sealed cable glands

> Cable selection superseded by ADR0012 on2026-09-12. Internal Micro-Fit,
> sealed glands and the non-Ethernet pinout remain in force.

## Context

ADR 0003 correctly rejected custom-powered RJ45, but left a circular outdoor
connector unresolved. The two PCB releases need one exact, non-Ethernet board
interface now, while the enclosure and roof-installation geometry are not yet
qualified. Belden 6541PA is a 5.44 mm-OD shielded two-pair cable with a 53 mm
minimum bend radius. Molex Micro-Fit 43650/43645 is an internal wire-to-board
assembly, not a weather bulkhead.

## Options

- Put an unselected M12/circular receptacle directly on each PCB; rejected
  because no exact mate, panel cutout, pigtail, shield or service envelope is
  currently authoritative.
- Use uninterrupted spoke cable through sealed strain-relieving glands, with a
  short internal tail to Micro-Fit at both boards; selected for v1.
- Use exposed Micro-Fit as the outdoor connector; rejected because it is not a
  weatherized panel interface.

## Decision

Use the exact internal board/cable contract in
[`../../03_src/rules/spoke_interface.yaml`](../../03_src/rules/spoke_interface.yaml).
Each carrier and pod enclosure admits the uninterrupted 6541PA cable through a
sealed, strain-relieving gland. Both internal ends terminate in 43645-0400
housings and mate to 43650-0400 PCB headers. The cable shield bonds to chassis
at the carrier entry before the PCB header, is insulated at the pod, and never
occupies a Micro-Fit cavity. No spoke is RJ45, Ethernet or PoE.

## Consequences

The PCB connector and electrical pin map can be frozen independently of the
enclosure. The exact gland, locknut, chassis bond hardware, strip/crimp process,
cavity-view drawing, strain relief, service volume, installed per-port lengths,
weather seal and pull test remain explicit whole-appliance/first-article holds.
Neither PCB release may describe the spoke harness as order-ready while those
fields remain `OWED`.

The protection contract is also explicitly layered. Carrier
`1812L035/60MR` protects the cable/pre-pod path with a 0.70 A trip ceiling;
pod `0ZCJ0010FF2E` is the 0.25 A-trip downstream-board tier. The 22 AWG cable,
7 A contact and 1.0 A carrier trace class screen above the carrier ceiling,
but neither PPTC is a precision limiter or interrupting fuse. Source
prospective-current behavior, hot coordination, fault energy, recovery and
one-fault/seven-healthy behavior remain measured holds.
