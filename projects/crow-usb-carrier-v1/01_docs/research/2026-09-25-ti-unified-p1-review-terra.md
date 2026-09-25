# Independent review: unified P1 diagnostic packet

**Verdict: faithful research-only FAIL; no P1/P2 credit.** I replayed
`build_trial.py` from `9f8ca953` against its declared board SHA-256
`d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`.
The replay returned `FAIL`, `p1_accepted=false`, `routing_realized=false`,
nine global errors, and nine item diagnostics, matching the packet’s asserted
shape. It writes only its research packet.

## Exact accounting and credit

The regenerated endpoint ledger has unique net and native-pad denominators:

| Family | Verified denominator | Result |
| --- | --- | --- |
| USB | one linked DP/DN path; VBUS tree 8/8; presence tree 3/3 | `INCOMPLETE` |
| ADC analog | 18 unique nets, 88 unique terminals, 18 geometry-free branches | `INCOMPLETE` |
| ADC7 portal | two nets, eight P2 duties, null capacity | `INCOMPLETE` |
| ADC timing | 14 unique nets, 54 unique terminals; 9 branch, 4 two-terminal schema gaps, 1 owner-containment failure | `FAIL` |

No double capacity credit is present. All USB and analog tree reservations
have `capacity_slots: null`; timing has no ordinary reservations; and the ADC7
portal has `capacity_slots: null`. The USB linked path reports two separate
rough stages but retains aggregate capacity `null` and `INCOMPLETE` status.

## Blocker classification

The advertised **14 primary source/accounting entries** is correct in its
stated scope: five timing failures (four unsupported two-terminal nets plus
`AUDIO_EN` owner containment) and nine independent power witness diagnostics.
The nine global timing denominator errors are derivative of the nine otherwise
valid timing branch representatives after that allocation fails its complete
witness denominator. They do not add routes, reservations, or a second
failure denominator.

One qualification should remain visible in review: there are also five
foreign-region physical blockers inside no-credit timing ledger rows. They are
not extra primary checker errors, because the unresolved-branch schema records
them as P2/P3 physical debt rather than rejecting owner containment:

* `ADC_DOUT1` at `R_ADC_DATA_PD.1` enters `analog_ch7`.
* `XU_I2C_SCL_1V8` and `XU_I2C_SDA_1V8` at their audio pull-up pads enter
  `analog_ch7`.
* `ADC_DIGITAL_BAD` at `U_ADC_CLOCK_OK.1` enters `analog_ch7`.
* `AUDIO_EN` at `R_AUDIO_PU.2` enters `input_buck`, in addition to its three
  outside-owner pads that make it the primary timing containment failure.

Thus the packet does not hide these as accepted geometry; they are present in
`endpoint_ledger.json` and every relevant tree keeps null capacity and explicit
route/return debt. The README’s “14 primary” label should be read as
source/accounting failures, not as a count of every recorded physical blocker.

## Owner/cell screen

The unified packet declares physical cells only for `clock_flash_debug` and
`xmos_core`; it declares no `analog_ch8` physical cell and makes no such claim.
The 18 analog branches therefore check current functional owner rectangles,
which is the current unresolved-branch checker behavior.

Two isolated negative perturbations confirm the no-credit branches do not
mask a failed declared model:

1. Reducing `analog_ch8.x2` from 201 to 199 mm and invoking the exact branch
   validator fails `C_ADC_AC8N1.2: branch pad outside source owner region`.
2. Adding a single complete `analog_ch8` physical-cell row to the unchanged
   source fails `C_FILTER8P1: native footprint/pad leaves physical cell
   analog_ch8`.

The second result is the known need for a multi-cell source redesign, not an
accepted cell contradiction. A future physical-cell model must pass its own
complete member, exclusive-region, and supported-witness checks; unresolved
branches do not validate a `physical_cell_id` under current checker code.

Native routes, pad access, filled In1.Cu return, connected-net proof, USB
launch qualification, and all listed P2/P3 debts remain open. This review
does not change the packet’s fail result or acceptance state.
