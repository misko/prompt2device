# US1B-13-F — local buck VIN reverse isolator

See ADR0022. DS16008 Rev.11-2 is the primary authority; no other US1x
voltage or forward-drop column is substituted. Stock KiCad D_SMA preserves
the manufacturer's land centres, gap and outer span with 0.05mm extra pad
width on each edge. Its cathode is pin1. Native footprint and package review
remain downstream; no generated board is accepted by this dossier.

At 9.86V local input, the allocated 0.30A x5.15V /85% load draws
0.184346A, below the published0.8A capacitive-load derated average at the
stated terminal-temperature condition. With1.3V engineering drop this is
0.240W, implying about7.2C junction-to-terminal rise using30C/W, not a
board-to-ambient thermal prediction. Startup and repetitive inrush require
their own waveform and temperature checks; the30A half-sine rating is not
an arbitrary pulse limit. The input bank's37.95uF upper initial model stores
500.94uC/3.306204mJ at13.2V, which does not determine peak current.

Public exact catalog hit at2026-09-09T07:21:34Z: C154439, Diodes
Incorporated, US1B-13-F, SMA, expand; stockCount21794,
canPresaleNumber21727, leastPatchNumber5, lossNumber4,
assemblyComponentFlag false. This dated observation is not order acceptance,
allocation or a requirement that stock remain unchanged.
