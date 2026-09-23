subject: crow-usb-carrier-v1 stocked ADC architecture research
date: 2026-09-23
reviewer: independent SOL agent /root/modular_review, ADC architecture
context-given: full-tree
source_commit: 5ea267d3b5f4a9c57aa4daef87086b3c89dbd335
board_sha256: not-generated (research-only)
design_verdict: SOUND (research basis only; source adoption incomplete)
order_verdict: BLOCKED-SOURCING

# Independent D7 ADC architecture review

Date: 2026-09-23
Reviewed: `01_docs/research/2026-09-23-stocked-adc-architecture.md`
Verdict: **ACCEPT as architecture research and the basis for a source implementation proposal.** It does not admit an ADC source cell or close D5/D7.

## Findings

The numeric reference plane is correct. AOM-5024L-HD-R at -24 dBV/Pa produces 63.1 mVrms at 1 Pa; the retained 18/11 transfer gives about 103.3 mVrms at the carrier, and 80 dB capsule SNR corresponds to 10.33 uVrms at that same plane. The report correctly avoids comparing an ADC full-scale SNR directly with the capsule's 1 Pa SNR. Recomputed penalties agree: PCM1865's inferred 13.28 uVrms at 0 dB costs about 4.24 dB; TLV6140's 113 dB planning estimate (4.48 uVrms) costs about 0.75 dB before buffer noise. The 1.2 Vrms interface maximum remains a separate clipping constraint.

The TLV320ADC6140 performance conditions are represented accurately. SBAS992A specifies 2 Vrms differential full scale at the default 2.75 V reference with 3.0–3.6 V AVDD; 112 dB typical SNR for shorted AC-coupled 2.5 kΩ inputs with DRE disabled; and 113 dB typical dynamic range for a -60 dBFS AC signal under that condition. The 122/123 dB figures require DRE, 2.5 kΩ, the documented -36 dB threshold/24 dB maximum gain and weak-signal conditions. At the Crow 94 dB SPL reference, 0.1033 Vrms is -25.7 dBFS, above TI's recommended DRE threshold below -30 dBFS, so the report correctly refuses to credit the 123 dB result there. AC/DC and 10 kΩ results are not interchanged.

TI explicitly supports shared-bus multi-device simultaneous sampling, I2C broadcast, distinct addresses, programmable TDM slots, tri-stated unused slots, common SHDNZ/BCLK/FSYNC, and per-channel phase-delay registers at one modulator-clock step. SBAA383C supplies a two-device slot 0–3 / 4–7 configuration and reset/configuration sequence. This is materially stronger than PCM1865 Figure 59, which establishes two-device TDM multiplexing but gives no maximum cross-chip aperture/group-delay mismatch or deterministic decimator-phase guarantee. Shared PCM1865 MCLK/BCK/LRCK removes frequency drift and independently generated PLL clocks; it still does not create a formal phase bound. The report draws that distinction correctly.

## Safe source implementation direction

Use two exact `TLV320ADC6140IRTWT` devices as the preferred implementation target, subject to a fresh exact-code screen at adoption. Give them distinct I2C addresses; share SHDNZ, BCLK and FSYNC; use one SDOUT line with device A in slots 0–3 and device B in slots 4–7; tri-state every unused slot; keep 32-bit TDM words with 24 valid bits at 48 kHz/12.288 MHz; and reserve an actual hardware I2C control path without authoring firmware. Bind channel-to-slot identity and common reset/power sequencing in source contracts. Use identical linear-phase filter and clock settings on both devices. Treat phase-calibration registers as configurable delay, not evidence of measured mismatch or a sub-step phase guarantee.

For the first source proposal, use **AC-coupled differential inputs, 2.5 kΩ input impedance, and DRE disabled**. This is the deterministic-gain mode with an applicable 113 dB primary specification and avoids independently timed DRE gain transitions across microphones. Retain 0 dB static channel gain: the 1.2 Vrms maximum remains 4.44 dB below 2 Vrms full scale. Do not enable DRE merely to advertise 123 dB. A later DRE option may be evaluated for weak-signal use only after defining its threshold/maximum gain and bounding cross-channel transition gain, phase and latency.

The AC-coupling network is an engineering selection that must be completed before source adoption. There are 16 differential legs. Each selected capacitor must be nonpolar over the actual OPA-to-ADC common-mode difference and signal excursion, have an effective (bias/temperature/tolerance-corner) capacitance that meets the chosen 20 Hz amplitude and phase budget with 2.5 kΩ, and carry a distortion bound appropriate to the ADC target. `22 uF effective` gives a nominal 2.9 Hz single-pole corner and about -0.09 dB at 20 Hz, but the nominal label alone is insufficient for MLCC voltage coefficient and THD. Remove or redesign the ADC-pin 10 kΩ ground pulldowns so they do not fight the ADC internal bias; preserve a defined disconnected-mux state by an analyzed alternative. Qualify OPA output loading, common-mode settling, quick-charge behavior and switch transients with the exact network.

A DC-coupled 10/20 kΩ version remains a legitimate compact fallback, but it cannot inherit the 2.5 kΩ AC-coupled noise rows or the 10 kΩ DRE-on AC test result. It requires a source calculation for OPA common mode/offset/swing and TLV DC input limits, plus either TI characterization or a measured noise/THD result before it can replace the preferred mode. PCM1865 likewise remains a comparator rather than the preferred source: +9 dB is the safer headroom setting (3.38 Vrms nominal; 1.38 dB remaining at the +0.5 dB accuracy corner), but TI gives no +9 dB noise/THD characterization and no formal inter-chip analog-phase bound.

## Remaining source-stage requirements

Before adopting the TLV pair, select and evidence the exact coupling capacitors and all new decoupling/strap parts under D5; create the exact WQFN-24 exposed-pad footprint and thermal/escape dossier; calculate two-chip AVDD/IOVDD/AREG/DREG/VREF rail loads and noise; freeze address, reset, clock, FSYNC polarity/edge, TDM offset and slot registers in the hardware/software interface; prove the chosen controller path exists without assuming the separately stock-blocked XU316 is admitted; and define a quantitative 20 Hz amplitude/phase and added-noise criterion. At native/first article, verify repeated-reset channel identity, simultaneous impulse delay across both ICs, continuous drift, noise/THD, clipping, DC/mux transients and oscillator/clock margins.

Catalog stock remains a dated arithmetic screen, not allocation, BOM-matcher acceptance or JLC placement approval. No weaker ADC or firmware authority follows from this architecture recommendation.
