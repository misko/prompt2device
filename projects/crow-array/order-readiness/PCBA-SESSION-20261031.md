# PCBA quote session — 31 October 2026

**Status: no complete PCBA quote, no purchasing authorization.** This report
supersedes the current-scope recommendations in earlier handoffs, not the sealed
release or historical observations. The user wants one assembled carrier and
eight assembled pods and accepts investigating extra bare/assembled boards if
needed for a quote. No substitutions, purchases, reservations, payments or
manufacturing commitments. Do not turn a partial quote into a build decision.

## Current assembly decision

The user decided to install the through-hole components at home, instead of
asking JLC to install them. For exactly one carrier and eight pods this adds
16 Amphenol RJHSE-5080 jacks (carrier J101–J108 and pod J1 on each of eight),
one Same Sky PJ-102AH power jack (carrier J1), and one RECOM R-78E5.0-0.5
module (carrier U10). These exact parts must be sourced separately; none were
ordered. Extra populated carriers each require eight additional RJ45 jacks,
one power jack and one RECOM module. The previously user-installed Pico,
eight microphones and eight buzzers remain user-installed. JLC's intended
scope for 1+8 is 351 SMT placements; JLC must leave the through-hole positions
open and the existing acoustic/Pico exclusions and process controls intact.

## JLC browser state

The existing two JLC quote drafts were updated using the reviewed per-board
`carrier-smt-bom.csv` and `pod-smt-bom.csv` from
`quote-draft/r1-20261031/`, paired with their existing SMT CPLs. They processed
past the previous through-hole-missing-CPL warning. The current carrier draft
has five bare/five assembled carriers (Economic); the pod draft has ten bare
boards/eight assembled pods (Standard). JLC-proposed tooling/rails and other
portal defaults remain conditional and do not demonstrate release-process
acceptance. The desired build remains one assembled carrier/eight pods; no
order of the extras has been authorized.

In the matching screen, eight previously unchecked carrier capacitor rows and
two pod resistor rows were selected using their exact already-matched part
numbers (carrier Samsung CL21B104KBCNNNC and Murata GRM21BR71A106MA73L;
pod Vishay CRCW06031K00FKEAHP). No substitutions were selected. JLC displayed
five inventory-shortage lines in the carrier and three in the pod; lines overlap.
Exact parts shown short were:

| Exact part | Draft scope and displayed shortfall |
|---|---|
| TDK C3216X7R1V106K160AC | Carrier: 10 |
| Murata GRM21BR71A105KA01L | Carrier: 20; pod: 20 |
| Littelfuse 1206L010/30WR | Carrier: 35; pod: 3; each screen showed 7 available, which must not be double counted |
| TI PCM1864DBT | Carrier: 10 |
| CTS CB3LV-3I-12M288000 | Carrier: 5 |
| TDK C2012X7R1V225K125AE | Pod: 10 |

The shortfalls are portal purchasing quantities, including its allowances,
not per-board installed quantities. Exact TDK C2012X7R1V225K125AE was searched
in the pod matcher and displayed zero public and account inventory. Clicking
Next on the pod produced an explicit warning that unselected parts would not
be placed. **Select parts** was chosen, not **Do not place**. Neither draft has
a complete SMT quote or an approved placement preview. Inventory and the
browser's selected state must be rechecked before relying on them.

The older seven-shortage estimate of $227.71 covered a 5-carrier/10-pod
sourcing scenario, not the present SMT-only quote. It included RECOM, now a
home-installed part. The historical $37.40/$14.00 PCB figures and $227.71
must not be represented as a complete or current PCBA price. Earlier JLC
Global Sourcing and regular-replenishment offers are candidates, not stock
allocations, and payment or non-cancelable procurement is outside scope.

## PCBWay browser state

Two files-only quote inquiries were submitted, each with unchanged Gerbers,
the full per-board BOM and SMT-only CPL. The cart displayed **Subject to
audit**, zero awaiting payment and zero in production. Inquiry
`T-5D1W1109696A` is one carrier; `T-1N2W1109696A` is eight pods. PCBWay
displayed provisional assembly-only amounts of $29 and $88 respectively;
these exclude fabrication and components, are subject to audit, and are not
complete quotes. The upload screen indicated review in 1–2 days, not a build
or delivery promise.

**PCBWay has the previous work split:** its submitted notes ask PCBWay to
install ten through-hole parts on the carrier and one per pod, while excluding
the Pico, microphones and buzzers. The user subsequently chose home assembly
of those through-hole parts for the JLC route; do not assume the PCBWay
inquiries were updated or that the user decided to change their scope. For an
apples-to-apples comparison, identify and explicitly label the difference;
obtain user direction before changing the already-submitted PCBWay inquiries or
contacting its staff. Both PCBWay inquiries are assembly-only; no separate
fabrication quote was obtained. At the PCBWay form the user confirmed its
stated export-control certification and authorized the linked policy; this
is not an independent export-classification determination.

## Engineering holds and evidence

The unchanged release, GERBERs, exclusions, mechanical/acoustic limits,
carrier 7628A and pod 7628 stack requirements remain subject to vendor and
engineering acceptance. The SMT CPLs carry earlier JLC-specific rotations;
neither vendor's final match or placement preview is approved. Exact sourcing,
usable inventory, attrition, fees, fabrication, shipping, taxes and dates are
unresolved. The home-installed components must be checked for orientation,
mechanical seating, protected holes and soldering before power-up.

`quote-draft/r2-1c8p-manual-review/` preserves the earlier native geometry,
manual-scope table and deliberately incomplete NOT-UPLOAD template. Its owner
labels and recommended JLC manual-install path are **historical** and are
superseded by the user's home-install decision above. Native pin-1 anchors are
not verified supplier centroids; do not upload the blank template as a CPL.
Existing `JLC-QUOTE-20261031.md` and JSON describe the earlier 5/10 warning,
not the latest browser state. The remote quote package remains byte-identical.
