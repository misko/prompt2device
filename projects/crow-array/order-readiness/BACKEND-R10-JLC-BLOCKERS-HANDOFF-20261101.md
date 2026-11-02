# Backend handoff — r10 stackup and connector registration

Review the [MacBook session report](JLC-R10-MACBOOK-SESSION-20261101.md), [r10 handoff](MACBOOK-R10-HANDOFF.md), [r10 instructions](R10-INSTRUCTIONS.md), [independent repair review](power-jack-r10-review/REVIEW.md), and [render review](render-review-r10/REVIEW.md). Work is quote-only: no purchase, reservation, substitution, vendor messages or manufacturing commitment. Preserve both existing drafts and all release artifacts. Do not silently adopt a tolerance concession or use a 3D picture as placement approval.

## 1. Resolve the carrier stackup question

The intended JLC04161H-7628A option prompted JLC to state actual thickness **1.5542 mm ±10%**, instead of 1.6 mm, and request acceptance of a 0.05 mm difference. The MacBook agent selected **No**. The live carrier draft must not be assumed to have the intended stackup selected; its $228.99 is conditional on its current settings and is not a confirmed 7628A quote. JLC also says this special stackup excludes economic assembly; standard assembly is selected.

Using source-bound electrical, mechanical, connector and enclosure constraints, assess the full tolerance range, stack/impedance assumptions and finished-hole, seating and retention implications. Identify precisely whether the warning is acceptable under existing requirements or requires a decision or vendor clarification; distinguish calculations from measurements. If it is not supportable, document what must change and any user decision needed. Do not select or waive it yourself on unsupported assumptions. Identify the precise inputs and quote settings needed for the MacBook follow-up.

## 2. Resolve JLC placement-model registration

The r10 carrier [draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=ace1600497a949bebfdd38f3ef826f7f) uses the r10 Gerbers, r10 carrier CPL and validated grouped-v2 BOM; JLC displays all 23 groups and 136 factory references. The retained [pod draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=71c384e886a94642a54e0c804cea3a97) uses the unchanged pod set and lists all 20 groups/29 references. The carrier and pod RJHSE-5080 model openings previously appeared inward in the 3D view despite native footprints and diagnostic renders specifying outward openings. The r10 carrier model remains visually suspect. Do not rotate by 180 degrees merely to make the model look correct: establish JLC part model axes, numbered pin 1 and both locator-peg positions relative to the native pad/hole pattern, physical manufacturer drawing and actual vendor placement convention. Determine whether the issue lies in the 3D model, CPL centroid/angle conversion or physical board geometry. If evidence cannot distinguish them, propose a concrete evidence-gathering path and retain the placement hold.

Also assess the new carrier PJ-102AH J1 against the **r10** native pad mapping: pin 1 VIN12 (188, 14.7), pin 2 GND (188, 8.7), pin 3 NC (183.3, 11.7), all mm in native coordinates; CPL body center (188, -8.2), 180°. The intended mouth points toward native -Y, outward. Verify all three terminals and holes, connector seating and vendor mapping. Do not mix r9 carrier Gerbers/CPL with r10. The MacBook did not obtain sufficient numbered-hole/model witnesses to approve these orientations; no saved close-up screenshots are claimed.

Produce a source-bound, reproducible diagnosis and, if supported, a reviewed candidate correction and verification plan. Preserve 136 carrier and 29 pod factory references, r10 component identities and the 20 home installs. Keep all existing manufacturing, mechanical and first-article holds. Any corrected upload needs a full reference audit, placement preview and refreshed quote, with user authorization where required.

## 3. Quote and remaining questions

Current displayed estimates: carrier $228.99 and retained pod $161.98, **$390.97** combined before shipping, tax and HOME parts. The pod display is not a fresh stock commitment. Both screens show PCB 3 days and assembly 5–6 days, not a committed arrival. The itemized session report records components, setup, feeders, SMT and manual charges. Confirm actual job settings, sourcing/attrition, stock, usable arrival, manual THT acceptance, shipping, tax, and price after stackup/placement reconciliation. Neither charge line proves acceptance of all specified manufacturing operations.

Return concrete findings, exact affected file hashes and references, unresolved decisions and a concise MacBook quote-only follow-up. No redesign or component substitution is authorized by this handoff.
