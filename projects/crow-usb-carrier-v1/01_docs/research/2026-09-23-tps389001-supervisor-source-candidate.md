# TPS389001 adjustable supervisor source candidate

This isolated candidate replaces two TPS389018DSER and three TPS389030DSER fixed-threshold supervisors with exact TPS389001DSER/C1509297 adjustable devices. U_PWR and U_AUDIO already use that part; final candidate population is seven per board. All seven retain TI DSE0006A six-pad pinout. The five changed devices preserve VDD, MR, CT, open-drain RESET and downstream reset-net connections; only SENSE moves behind a local divider. No actual regulator replacement, routed board, waveform, or order allocation is claimed here.

The five new dividers use 52.3 kΩ/100 kΩ for U_1V8_OK and U_ADC_1V8_OK, and 169 kΩ/100 kΩ for U_XU_3V3_OK, U_ADC_3V3X_OK and U_ADC_OK. Yageo exact-MPN PDFs in `02_parts/RT0402BRD0752K3L` and `02_parts/RT0402BRD07169KL` specify ±0.1%, ±25 ppm/°C and 0402/1005. Existing 100 kΩ RT0402BRD07100KL/C852472 is the bottom part. New SENSE nets are local to each owning block; no other rail or reset net changed. Source census rises from 490 to 500.

TI TPS3890 SLVSD65A gives adjustable VITN=1.150 V, VITP=1.157 V nominal, ±1% threshold accuracy and up to 100 nA SENSE current. Model resistor initial ±0.1% plus independent opposing ±25 ppm/°C over a 100°C delta: ±0.35% each. For a trip, use 0.99×1.150 V, low top/high bottom and -100 nA. For release, use 1.01×1.157 V, high top/low bottom and +100 nA. `Vrail = Vsense×(1+Rtop/Rbottom)+Isense×Rtop` yields:

| Sense rail | Min falling trip | Max rising release | Source-stage functional window |
| --- | ---: | ---: | --- |
| 1V8 | 1.72457 V | 1.78927 V | Winbond W25Q128JWSIQ min 1.70 V; proposed TPS62825 adjustable DC screen min 1.82216 V. |
| 3V3X and 3V3_ADC | 3.03230 V | 3.17429 V | XMOS USB_VDD33 min 3.00 V; proposed 3V3X adjustable DC screen min 3.24332 V; LT3045 3V3_ADC current declared min 3.22 V. |

The proposed regulated-rail DC minima are **coupled to a separate adjustable-TPS62825 candidate**, not changed in this branch. Before integration, recheck these inequalities against its accepted final rail bounds and source-current/thermal accounting. Relative to fixed 1.73/1.740 and 2.89/2.907 V nominal thresholds, the new windows are intentional functional changes: the 1V8 worst trip is above flash's 1.70 V floor, while the old 2.89 V 3V3X trip sat below XMOS USB's 3.00 V floor. The higher 3V3 trip still releases below the 3.22 V held analog floor.

Allocate **≤20 mV combined output ripple and local-ground offset** as a *source engineering design and first-article qualification target*, not a guaranteed regulator specification. Under that target, 1V8 DC-low-minus-budget 1.80216 V exceeds worst release by 12.89 mV, and lowest trip-minus-budget 1.70457 V remains 4.57 mV above flash minimum. 3V3_ADC 3.22−0.020=3.20 V exceeds worst release by 25.71 mV, and lowest 3V3 trip-minus-budget 3.01230 V stays 12.30 mV above XMOS USB minimum. These small residuals require actual local measurement, including return offset at the SENSE/GND pins. Proposed regulator maximums 1.89808 V and 3.39319 V plus a separate **≤40 mV combined overshoot/ripple/ground** target remain below flash 1.95 V and XMOS 3.3 V USB 3.60 V maxima; board transients must verify this. No supplier guaranteed ripple/max-delay claim is made.

CT connections are unchanged. U_1V8_OK retains 10 nF (~10.7 ms nominal release), U_XU_3V3_OK and U_ADC_OK retain 1 nF (~1.09 ms nominal), and the two ADC-domain digital-rail monitors retain open CT (~25 µs typical). Their exact delay minima depend on CT effective C/leakage and TI 0.90–1.35 µA current/1.17–1.29 V threshold corners. TI lists only *typical* 8/18 µs falling SENSE propagation. On abrupt isolated digital-rail collapse, output-bank capacitance alone gives microsecond-scale time from trip to the flash/USB voltage floors at declared maximum load; this source screen does **not** claim RESET is guaranteed to assert before an arbitrarily collapsing rail leaves its operating range. The held 3V3_ADC monitor supply, source-approved 100 µs analog detection/isolation engineering allowance, startup, normal-powerdown, clock-gating and reset waveforms remain P3/first-article obligations. Do not transfer the analog 752 µF hold screen to digital rails.

Exact serialized direct JLC catalog observations (UTC 2026-09-23; public stock, not PCBA allocation):

| Code / exact MPN | Stock | Candidate demand for five boards | Raw JSON SHA-256 |
| --- | ---: | ---: | --- |
| C1509297 TPS389001DSER | 591 | 35 | `fbe1ce413957030ac5d8b7298ca925a8a661a775522435d35de0e3eaa300dcdf` |
| C852832 RT0402BRD0752K3L | 28,007 | 10 | `38e72a1dbcb931fe49a168e00925c9aeae5cc4f39600194c3b5a9efd083ac21e` |
| C852555 RT0402BRD07169KL | 40,993 | 15 | `01abbf5ad13857e0628cc0fcfa0d890bd5b8e9567bfc9e776929c7d42d7c27db` |
| C852472 RT0402BRD07100KL | 788,042 | 30 in this candidate (six per board, including existing core-feedback top); **40** if the separate two-adjustable-buck candidate adds two more bottoms | `1d16e053a8f8145064d349d282e86e143970227c4c9a8930d801269592c1274f` |

Raw direct snapshots with exact UTC timestamps: `/tmp/crow-tps389001-jlc-20260923/{code}.json`. Order-time allocation is still required. Primary local datasheets: `02_parts/TPS389001DSER/TPS3890_SLVSD65A.pdf`, `02_parts/W25Q128JWSIQ/Winbond_W25Q128JW_RevH.pdf`, `02_parts/XU316-1024-TQ128-C24/XM-014532-PC-v2.0.0.pdf`, plus the two retained Yageo PDFs. The independent source-stage reviewer found no requirement that external RESET beat an arbitrarily abrupt rail short; that case remains a waveform qualification limitation, not an unclaimed guarantee.
