# r9 RJ45 orientation — diagnostic review, placement hold retained

Input commit: `4eb497aa79cad200246257aec73af01e5bfd0d15`.
Reviewed the JLC selection/quote follow-up, merged v2 candidates, native r9
carrier/pod boards, CPLs and retained Amphenol drawing. This is diagnosis only:
no design/export/UI correction, stage acceptance, vendor message or purchase.

## Conclusion

**Native numbered pin/peg geometry and CPL body centers agree with the maker
drawing. A JLC model/zero-angle interpretation mismatch is plausible but not
proven. Do not rotate the native footprint or blindly add 180 degrees to CPL.**
The report's inward-facing preview remains an unresolved assembly discrepancy.
No new complete quote or production acceptance is claimed.

## Independently reopened local evidence

The user-supplied Amphenol P-RJHSE-X080 Rev A drawing (2019-05-22), SHA256
`e96d3f6cde115981be470e0edd3159dfda3ebe1a453db0c45d525e629668a756`, was
rendered and visually inspected. The 5 option is the 50-microinch-gold variant.
Its recommended PCB layout is explicitly **component-side**, not underside.
The published [exact-part Rev J drawing](https://cdn.amphenol-cs.com/media/wysiwyg/files/drawing/p-rjhse-5080.pdf)
was also accessible through web extraction and corroborates pin/peg dimensions;
direct PDF download returned403, so visual comparison used the retained Rev A.

Mapping the drawing pattern into our top-side frame requires a planar180-degree
rotation, not reflection. Pegs are toward the mouth; signal tails are behind.
Reopened all9 footprint instances using KiCad: carrier J101–J108 and pod J1.
Each has native angle0, numbered pads1–8 at1.016mm pitch with alternating rows
separated by1.780mm, locator holes12.700mm apart and2.540mm ahead of pin1's row.
The maximum nominal drawing-to-native coordinate discrepancy is0.004mm due to
rounding. Signal drill0.890mm and locator drill3.250mm agree at this rounding
level. This is not a finished-hole/tolerance or physical fit acceptance.

CPL X is native X and CPL Y is negative native Y. Nominal body center from pin1
is (+3.556,-0.127)mm, derived from the primary inch dimensions, not pad centroid.
All9 CPL centers, zero angles and Top sides match that pose.

| Witness, native top view (X right, Y down), mm | Pod J1 | Carrier J101 |
| --- | --- | --- |
| Pin1 | (7.000,8.500) | (8.000,8.500) |
| Pin8 | (14.112,10.280) | (15.112,10.280) |
| Left locator hole | (4.210,5.960) | (5.210,5.960) |
| Right locator hole | (16.910,5.960) | (17.910,5.960) |
| Nominal body center | (10.556,8.373) | (11.556,8.373) |
| Nominal mouth plane | Y=0.880, facing decreasing Y | Y=0.880, facing decreasing Y |

Carrier J102–J108 have the same Y geometry, with anchors X26.7,45.4,64.1,82.8,
101.5,120.2,138.9mm respectively. The mouth plane follows8.5-(.100+.200)*25.4.

A literal180-degree rotation of the physical part about this body center puts
the peg row at native Y10.786 rather than5.960mm: a4.826mm mismatch. Thus simply
reversing the actual connector is not compatible with the board holes. This
counterfactual does NOT determine JLC's numeric correction: a vendor model may
have a different definition of zero, or an incorrectly registered origin/model.

## BOM and package checks

Merged v2 BOMs preserve exact manufacturer/MPN/footprint/C-code/assembly-route/
supply-route mappings for all136 carrier and29 pod factory references. No
duplicates were found on expansion. Changes to comments/grouping/order are not
geometry changes. Candidate SHA256 values reproduce the MacBook report:

- Carrier: `39ec9078f5e01fb6177d1114878e99c06e552118da2c0f8c4f1932241145e2bf`
- Pod: `d297047101ca69a0d3466518a5c2e85e9ab6f7d900e3f265640d1d1066b78131`

`r9_quote.py verify` still passes all113 payload files with105 r8 files preserved.
No BOM/CPL/Gerber/native package bytes were changed during this investigation.

## Browser evidence limitation

[Read-only TinyFish run](https://agent.tinyfish.ai/runs/79378fbe-75eb-48c9-b247-7a9d1b5d7233)
accessed the existing pod and new carrier draft. It claimed outward mouths,
contrary to the retained MacBook report, but did not provide actual screenshot
URLs or identify physical pin1. It also called this unshielded part's features
"metal shield pegs", described nonexistent U1–U9 PCM1864 ADCs on the carrier,
and inferred no carrier CPL upload merely from a visible upload button. The
actual carrier has two ADCs U1/U2, and the MacBook report documents the CPL.
These inconsistencies make the browser's orientation conclusion insufficient.
Do not repeat its speculation that the user misread a triangle as a finding.
No position/rotation values or registered model-to-hole measurements were
established. The browser reports no edits or approvals; both holds remain.

## Recommended next actions, in order

1. **Preferred: obtain a reproducible JLC placement close-up before correction.**
   On the MacBook, capture one pod J1 top/underside/tilted preview with the actual
   placement table center/rotation, visible board-hole positions and model
   terminals/pegs. Include a view with the connector body hidden/transparent if
   the UI supports it. Record whether X/Y are panel-relative (rails may offset
   the display). Compare pin1, pin8 and BOTH pegs to the table above, not just the
   mouth. If available, export/download the exact JLC model and its transform
   through a read-only control. Repeat on carrier J101 and verify all8 carrier
   references share the same convention. This can distinguish a global zero
   offset from a bad model/origin without changing valid copper.
2. **If the preview cannot expose those witnesses: request JLC placement review**
   with the manufacturer drawing and required pose. Ask them to confirm pin1 and
   both pegs seat in the specified holes and mouth faces native-Y edge. A message
   requires user authorization; none was sent. Obtain the production-placement
   interpretation, not only a cosmetic screenshot.

Only after establishing the transform should a candidate vendor-specific CPL
rotation/center correction or model correction be proposed and independently
checked. Keep native PCB geometry unchanged unless numbered-hole evidence
actually identifies a board error. Do not mark placement approved on visual
mouth direction alone. Carrier stackup (currently No Requirement), all other
placements/process controls, shipping/tax and assembly acceptance remain open.
The reported USD391.09 is still a draft total excluding shipping, tax and home
parts, not a complete delivered or confirmed-stack quote.
