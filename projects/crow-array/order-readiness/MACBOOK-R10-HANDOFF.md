# MacBook handoff — r10, quote only

Update the JLC quote for **5 fabricated / 2 assembled carriers** and
**10 fabricated / 8 assembled pods**. Keep exact specified components and the
authorized factory/home split. No purchases, payments, reservations, substitutions,
noncancelable sourcing, vendor messages or manufacturing commitments. Stop before
any confirmation that releases production or creates a financial obligation.

## Get and verify the published files

Use the existing repository and shared branch `codex/crow-jlc-source-review-20261030`.
Fetch first; do not reset, stash or overwrite unrelated MacBook work. In a clean
checkout already on that branch, fast-forward only:

```sh
git status --short
git fetch origin codex/crow-jlc-source-review-20261030
git merge --ff-only origin/codex/crow-jlc-source-review-20261030
python3 projects/crow-array/order-readiness/r10_upload_check.py
```

If the checkout is dirty or on a different branch, use an isolated worktree or
ask before changing it. Confirm this handoff and `r10_upload_check.py` exist in
the fetched revision. The Python-only check must report
`PASS_UPLOAD_INTEGRITY_ONLY`,213 payload files,105 protected r9 files and the
476 SMT/28 factory THT/20 HOME installation split. It checks exact review/native
bindings and upload identities; it does **not** rerun electrical or mechanical
engineering. Full replay on the server used KiCad10.0.4; if compatible KiCad is
available, also run `python3 projects/crow-array/order-readiness/r10_quote.py verify`.
Do not modify manifests or regenerate files to bypass a failed check.

Read [r10 instructions](R10-INSTRUCTIONS.md), [independent review](power-jack-r10-review/REVIEW.md)
and [render index](render-review-r10/REVIEW.md). The repair is approved only as a
controlled prototype quote derivative, not a new production release.

## Exact upload set

All paths below are relative to `projects/crow-array/order-readiness/`.

| Job | Gerbers | BOM | CPL |
| --- | --- | --- | --- |
| Carrier | `quote-draft/r10-2c8p-outward-power/carrier-gerbers.zip` | `quote-draft/r9-merged-bom-candidates/carrier-bom-merged-v2.csv` | `quote-draft/r10-2c8p-outward-power/carrier-cpl.csv` |
| Pod | `quote-draft/r10-2c8p-outward-power/pod-gerbers.zip` | `quote-draft/r9-merged-bom-candidates/pod-bom-merged-v2.csv` | `quote-draft/r10-2c8p-outward-power/pod-cpl.csv` |

The existing **v2 grouped BOMs** are intentionally preferred here because they
previously exposed every reference in JLC's matching UI. The portable check
proves per-reference manufacturer, MPN, footprint, catalog code and installation/
supply route equality to the canonical r10 BOMs; descriptive comments/grouping
differ, not parts. Carrier has136 factory references, pod29. Do not use the first
non-v2 merged candidates. Canonical r10 BOMs remain in the package for audit.

**Never use r9 carrier Gerbers or CPL:** the new jack has different hole/copper
positions, not just a visual rotation. The pod files are unchanged; its existing
draft can be retained if its exact files and quantity settings are verified.
Preserve the old carrier draft as history and create a new r10 carrier quote
draft. Record its new URL and the actual uploaded filenames/hashes.

Historical account drafts, not r10 approvals:
[carrier](https://cart.jlcpcb.com/smt-order/?pcbFileNo=5e6ccfa5ec0b4bac8f06c7b79760b061),
[pod](https://cart.jlcpcb.com/smt-order/?pcbFileNo=71c384e886a94642a54e0c804cea3a97).

## Browser review checklist

1. Set fabricated/assembled quantities separately, as above. Retain ENIG,
   required outline/rail/process controls and **Do not confirm automatically**
   for production-file and placement review. Reconcile carrier
   **JLC04161H-7628A** (not "No Requirement") and pod **JLC04161H-7628**.
   Do not acknowledge a new finished-thickness/mechanical concession without
   authorization; record the exact warning if it blocks the quote.
2. Match all exact parts; verify136 carrier and29 pod factory references,
   including all through-hole jacks/regulators. Do not trust confirmed-row
   counters alone. No required factory reference may become "Do not place" to
   bypass a shortage. X1/Pico/microphones/buzzers are intentionally HOME; C4 is
   factory fitted. Do not upload home-install files as factory BOM/CPL.
3. For carrier J1, verify native pin1 VIN12(188,14.7), pin2 GND(188,8.7),
   pin3 NC(183.3,11.7). CPL body center is(188,-8.2),180deg. Mouth faces outward
   native -Y. Check actual pad/hole registration, not simply appearance or
   angle number. All three terminals, including NC, need soldering.
4. Check carrier J101–J108 and pod J1 RJ openings face outward; verify pin1
   and both locator pegs against the retained manufacturer drawing/native
   footprints. Local orientation passes, but the earlier JLC inward-facing
   model discrepancy is still open. Do not rotate parts by180deg just to make
   the preview look right. If witnesses are unavailable or inconsistent, save
   evidence and keep placement approval on hold.
5. Review the rest of each placement list for position, rotation, polarity,
   package and population. Compare with the [diagnostic views](render-review-r10/REVIEW.md),
   recognizing their illustrative bodies are not exact manufacturer CAD.
6. Keep the documented jack hole/annulus/seating/pose, three-terminal solder,
   through-fill and retention requirements open until reconciled. Retain TRACO
   localized THT, LUTE reflow/no-unqualified-wash, rail/finished-edge, stencil and
   accessible home-clock lands controls. No automatic waiver of a constraint
   that the portal cannot represent; report it without contacting JLC.
7. Obtain current exact stock, gross quantities/attrition, sourcing fees and
   usable arrival dates where the quote-only UI allows. Stop before any
   noncancelable pre-order/reservation. Obtain itemized PCB, components, SMT/THT,
   setup, sourcing, shipping and tax prices for each job. The old combined
   **$391.09 is historical**, not the updated r10 total.

## Return evidence

Save a dated session report with both draft URLs, exact upload filenames/hashes,
job settings, reference coverage, screenshots showing J1 numbered-hole mapping
and RJ pin/peg orientation, unresolved warnings, stock observations and itemized
prices/lead times. Distinguish observed quotes from pending fees or acceptance.
Report what prevents a complete quote without changing scope or buying parts.
No full production approval follows from a complete browser price.
