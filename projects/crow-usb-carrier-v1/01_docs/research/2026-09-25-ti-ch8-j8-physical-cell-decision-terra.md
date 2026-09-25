# Decision packet — channel-8 physical cells and fixed J8

**Disposition: the fixed J8 overhang alone blocks a typed `analog_ch8` physical-cell admission, not the current formal P1 root.** This packet is read-only. The reviewed three-support pose moves only `R_SPOKE_UVLO8`, `C_SPOKE_OUT8`, and `C_SPOKE_DVDT8`; it cannot change the J8/outline contradiction or turn a planning datum into mechanical authority.

## Scope correction

The live `p1_corridor_requirements.yaml` remains `INCOMPLETE` and declares `physical_cells` only for `clock_flash_debug` and `xmos_core`; it declares none for `analog_ch8`. The checker's optional-cell path therefore does not evaluate J8 unless a candidate opts `analog_ch8` into that extension. Existing channel-8 branch checks use the primary modular `regions[analog_ch8]`, and their current exact endpoints are ADC/ISO/VMID pads rather than J8. Accordingly, J8's overhang does not independently prevent dispatching or evaluating the present formal P1 root; the existing root still has its unrelated incomplete/failed obligations. It does prevent a current-schema typed channel-8 cell candidate, and remains an unresolved P2 connector-placement/return and connector-FULL concern.

Reproducible source check:

```sh
python3 - <<'PY'
import yaml
d=yaml.safe_load(open('03_src/rules/p1_corridor_requirements.yaml'))
print(d['status'])
print(sorted({x['owner_block'] for x in d['physical_cells']}))
print([x['id'] for x in d['physical_cells'] if x['owner_block']=='analog_ch8'])
PY
# INCOMPLETE
# ['clock_flash_debug', 'xmos_core']
# []
```

## Exact lower bound

The retained native TI census has 569 footprints, 27 fixed references, and 36 unique `analog_ch8` functional members. `J8` is one of both denominators. The outline is `[20,20,240,140]` mm; its native full envelope is `[198.875,19.955,216.268081,34.495]` mm and body `[198.891919,19.975,216.268081,34.475]` mm. Thus the full envelope projects **0.045 mm** and the body **0.025 mm** above the north edge. All 12 pads start in-board at y=23.260 mm.

That is by itself a monotone current-checker obstruction. A cell containing the full envelope must begin at y≤19.955 and fails the outline predicate; an in-outline cell beginning at y=20 omits J8 native geometry and fails containment. Splitting the other 35 members, assigning disconnected occupied same-owner pockets, or recutting unrelated regions cannot alter either inequality. The existing minimum-cell screen found no other native footprint-envelope collision among the 36, so this is not a hidden collision claim.

The 0.045 mm is a nominal native-CAD/full-envelope observation, not a manufacturing allowance. The missing datum is an accepted J8 edge-registration receipt: with the board top Edge.Cuts as datum A, measure and retain the signed body/mouth projection at left, centre, and right of the fixed J8 mouth, before and after soldering, with instrument uncertainty. Bind the result to board/outline/footprint/model/pose hashes, jack and board lots, finished thickness and edge-routing process; also record pin, shield-tab and locating-post seating/registration. The Würth 615008160221 drawing rev 001.003 and matching STEP support planning only. Mated Telegärtner 100009141 service evidence remains a separate connector-FULL gate.

## Smallest honest source redesign

Keep all 36 refs functionally owned by `analog_ch8`; a remote connector does not become `usb_frontend` or `usb_vbus_sense` merely to satisfy a rectangle. When the measured receipt exists, the minimum typed partition is:

1. an `analog_ch8_j8_connector` occupied pocket containing **only J8**, fixed pose, with the exact north-edge attachment bounded to x=198.875..216.268081 and y=19.955..20.000;
2. an `analog_ch8_adc8_local` occupied cell for `C_ADC_AC8N1`, `C_ADC_AC8N2`, `C_ADC_CM8N`, `C_ADC_CM8P`, `C_FILTER8N1`, `C_FILTER8N2`, `C_FILTER8P1`, and `C_FILTER8P2`, to keep the ADC handoff components together without claiming an ADC route or return; and
3. occupied same-owner cells for the remaining 27 declared members, grouped only after each full native envelope, pad, foreign-region exclusion, and local-coupling check. Empty transit cells are optional and only needed for an actual empty reservation path; disconnected occupied pockets are permitted by the checker.

This is an accounting model, not permission to use bare envelope cells as routing area. Every declared member must occur once across the cells, and `analog_ch8` remains the primary endpoint-owner region unless and until an endpoint-specific cell binding is implemented and verified.

A cell manifest cannot repair current foreign-region debt. The next floorplan variant must separately resolve these exact 11 refs / 12 incidences without reassignment: `C_A8N`, `C_FILTER8P1`, `R_IN8N`, `R_OUT8P`, and `U_AFE8` against `usb_vbus_sense`; `C_ISO8`, `C_SPOKE_DVDT8`, `C_SPOKE_OUT8`, `R_SPOKE_UVLO8`, and `U_ESD8` against `audio_clock_tdm`; and `R_IN8P` plus `U_ESD8` against `analog_ch7`. In particular, `U_AFE8` reaches x=201.545, so moving the VBUS boundary merely to x=201 is insufficient; `C_SPOKE_OUT8` reaches y=74.825, so an audio y=72 cut is insufficient; and a shared channel-7/8 divider cut must avoid `C_FILTER7P1` at x=179.145. These are region/placement recut constraints, not candidates for foreign ownership.

## Exact next test

First obtain the Stage-B measurement receipt above; until then, leave `physical_cells` absent for `analog_ch8`. After it exists, make one disposable source overlay with the J8 attachment plus a complete 36-ref cell manifest, but no route reservations. Run native full-envelope/pad containment, outline, exact-one-owner, foreign-region, fixed-27, and 569-pad tests. Reject it if the receipt is absent or hash/drift-bound, any J8 pad/drill leaves the in-board pocket, any foreign member enters a channel-8 cell, or any of the 12 listed foreign incidences remains. Only a passing geometry overlay may be marked `INCOMPLETE`; ADC8 endpoints, P2 pad access, filled In1 return, all routes, connector FULL, and P1/P2 remain unaccepted.
