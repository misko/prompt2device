# Passive distribution model adoption

Crow now explicitly declares passive_pptc and the exact 1812L035/60MR identity. Its manufacturer reference hold current is 0.20 A at 70 C against 0.10 A normal load. Removed the deliberately invalid hard-current-limit fields: Itrip is not a hard current clamp. The normal topology verdict identifies the reference grade and explicitly excludes fault clearing.

Adopted the SOL reader after two review corrections. Fault checks reject absent qualification, hot/current interpolation, typical-only trip/leakage evidence, missing sustained-safe-current bounds and aggregate N-A declarations. They require an exact cold-corner trip point, prospective-current and energy bounds, and leakage below the protected path's continuous-safe capability. Grades and source locators still require engineering review; the reader does not authenticate manufacturer assertions or infer protection technology from arbitrary MPN text. Untyped legacy active records remain compatible.

These checks are not comprehensive physical fault qualification. PPTC recovery/retry thermal duty is not graded by the added reader, and Crow has no accepted branch/source fault envelope. Its E-FAULT intentionally fails. The proposed active-limiter architecture is a separate engineering investigation; this change does not implement it.

Root validation: topology regression 65/65 (38 known-bad, one existing declared E-OFF blind spot); early-design regression 52/52 (40 known-bad). Crow E-TOPO passes 13/13 rails and 5/5 converters. Crow E-FAULT fails for missing passive_distribution_faults; E-MARGIN still fails all eight spoke voltage margins. Project contracts pass, zero violations. No schematic/PCB admission or protection acceptance is claimed.
