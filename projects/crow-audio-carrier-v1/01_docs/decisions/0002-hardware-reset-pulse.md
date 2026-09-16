# ADR-0002 — hardware high-delay-low-high ADC reset

Status: accepted for first article
Date: 2026-09-01

CS5308P requires RESET deasserted after power, at least 2 ms high, then asserted low for at least 1 ms, then deasserted. A normal supervisor low-to-high POR cannot implement this sequence, and firmware is outside this PCB’s authority.

TPS3839K33 supervises 3V3_ADC and releases CLR after 120–350 ms. CLR rising triggers SN74LVC1G123. Its Q turns on a 2N7002 to pull ADC_RESET_N low; a 10 kΩ pull-up restores high when Q expires. Rext 100 kΩ and Cext 220 nF intentionally produce a pulse far longer than the minimum. TI does not guarantee the minimum generated pulse width, so the exact physical waveform remains an order-blocking first-article measurement.
