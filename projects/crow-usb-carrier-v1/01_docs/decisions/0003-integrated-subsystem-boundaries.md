---
id: 0003
date: 2026-09-22
status: accepted
---
# 0003 — Integrated subsystem boundaries

The user requests a new Crow carrier with an onboard USB IC. Select XU316 at IC level and retain CS5308P for synchronous eight-channel conversion. The TPSM63603V5 is an integrated power module, including its inductor. These decisions do not constitute completed circuit, thermal or layout approval.

The architecture contract enumerates the complete retained analog boundary excluding U_ADC (296 supporting references) and the digital plus USB-front-end boundary excluding U_XU (104 supporting references). The analog count intentionally includes shared quiet-power and spoke infrastructure; it is not described as a minimal ADC requirement. The digital count includes regulation, reset, flash, clocks, programming, VBUS/ESD and the quiet-rail-safe ADC interface. The18-reference external-input/power-module boundary is an additional shared dependency for both.

MCHStreamer is a digital bridge and cannot supply the analog front end; as an external bridge it also conflicts with the new onboard-IC requirement. Cirrus DC5308P and XMOS XK-AUDIO-316-MC remain evaluation/reference platforms. Neither substitutes for the integrated Crow spoke and USB carrier requested here. Primary references are retained in the existing research and component dossiers; previous solved board geometry and reviews are not reused.

Implementation consequences: retain firmware-forbidden scope under BRIEF D2 while specifying accessible hardware programming; finish native schematic review, supply-state proof, exact stackup and layout/routing verification. Module preference does not waive these obligations. The contract records selected architecture and complete support boundaries, not a fabricated prototype result.
