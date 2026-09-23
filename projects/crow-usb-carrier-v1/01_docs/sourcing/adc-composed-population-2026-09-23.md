# Composed ADC source — D5/D7 population and dated-stock audit

**Scope:** final isolated composition commit
679fdc2def9f0344ca0e1731698a4639f987eaf1 in
/tmp/crow-adc-composition-20260923. Read-only audit; no network requests and no
source changes.

## Bound source census

| Authority | Result / SHA-256 |
|---|---|
| Final exact-parts CSV | 90 MPN rows, 568 references; 06cac75109bc3ef737d46d57da4bba8b871d666729143f854b628df1017526b2 |
| Final diagnostic circuit | 568 source components; b68fd99fad9092260c1e2fd2630cf1a63ce334057802e6c464aa6052b8ab307c |
| D9 assembly policy | Exactly two user_supplied/on_bom:false entries, 24 refs, assembly.yaml lines 135-179 |
| Source-stock receipt | source-stock-refresh-20260923/manifest.json; a0c9b5a2e3efdea626c356bd5d9efa774f369845e2ebae5cdfcbe852feaee87d |
| Newer prospective ADC receipt | adc-prospective-stock-20260923/summary.json; 2748e2b565d810e18cec40bc15a9b23b9aaadca5dd371df0ced83245ae9e1fd6 |

The diagnostic source records preserve J_PWR with JLC C192562. U_ADC_A and
U_ADC_B carry C1852023; U_ADC_I2C_XLATE carries C840107. The D9 records retain
their physical MPNs in circuit source, with empty JLC lists.

## Population result

**PASS for exact coded-population coverage; FAIL for D7 public-stock coverage
because of the selected XMOS line.**

- The only uncoded rows are exactly D9's 24 manual THT references:
  615008160221 at J1-J8 and R82DC4100CK60J at C_A1N/P through C_A8N/P.
  This exactly matches the two governed user-supplied entries.
- The remaining **544 source references / 88 exact coded rows** have a selected
  JLC code, including non-D9 J_PWR.
- Every one of the 88 code/MPN pairs maps to a retained exact-code observation.
  There are no missing-observation rows and no identity mismatches. J_PWR's
  returned normalized model 436500200 is the same selected Molex
  43650-0200 ordering identity.
- D7 threshold is five times each row's board quantity plus 150.

## Aggregate D7 result

**87/88 coded rows pass** the dated public-catalog threshold. The sole failure:

| Selected MPN / code | Qty per board | Five-board demand + 150 | Dated observation | Disposition |
|---|---:|---:|---|---|
| XU316-1024-TQ128-C24 / C6362698 | 1 | 155 | 46 at 2026-09-23T05:20:09.795126Z; raw SHA-256 c87b19b8d0e78351a5f6acd49c8978039151dc7b2f1d07afe38089dde592566b | D7 public-stock failure, short by 109. |

The ADC composition and changed aggregate lines have retained exact identity and
stock evidence:

| Selected composed line / code | Qty per board | Threshold | Dated stock | Evidence disposition |
|---|---:|---:|---:|---|
| TLV320ADC6140IRTWT / C1852023 | 2 | 160 | 188 at 2026-09-23T05:20:03.183280Z | Exact identity; public threshold pass (margin 28). |
| TCA9406DCUR / C840107 | 1 | 155 | 16,905 at 2026-09-23T05:20:07.614806Z | Exact identity; public threshold pass. |
| TMUX4827YBHR / C22428234 | 8 | 190 | 5,437 at 2026-09-23T04:48:04.052809Z | Exact identity; public threshold pass. |
| GRM32ER71A476KE15L / C84494 | 42 | 360 | 56,458 at 2026-09-23T04:48:07.244880Z | Exact identity; public threshold pass. |
| EEEFK1A471P / C178530 | 16 | 230 | 668 at 2026-09-23T05:20:05.410161Z | Exact identity; public threshold pass. |

No candidate is being screened here: all five rows above are read from the
final composed CSV. The earlier source-refresh candidate labels for TMUX4827
and TCA9406 were corrected to the exact suffix MPNs against retained responses;
this audit uses those exact final composed identities.

## Limitations

All observations are dated public LCSC/JLC catalog counts. They become stale
and do not reserve inventory, establish PCBA allocation, prove assembly
attrition/minimum quantity, or establish JLC process/placement acceptance.
This audit therefore does not clear the D5/D7 release gate: the XMOS shortage
requires resolution, and all order-stage JLC uploader checks remain required.

