# crow-audio-carrier-v1

First-article-only eight-channel analog-audio carrier for the crow roof array. It accepts eight active-balanced microphone-pod feeds, digitizes them synchronously with one CS5308P, and presents TDM8 to a cable-connected miniDSP MCHStreamer. Raspberry Pi 5, PoE/Ethernet, and USB data remain off-board COTS functions.

**DO NOT ORDER. No carrier release is sealed.** Public-data laboratory-prototype
development is admitted by ADR-0007; the corrected source awaits fresh exact
schematic reviews, while
physical-pin/layout reviews, routing and release verification remain required. Authenticated
JLCPCB allocation and physical first-article qualifications are separate,
unmet boundaries. The original request and acceptance criteria live in
[`01_docs/BRIEF.md`](01_docs/BRIEF.md); current work lives in
[`01_docs/STATUS.md`](01_docs/STATUS.md).

## Capability

- target: `release`
- signal integrity: `high_speed_digital`
- assembly: `jlcpcb`
- firmware: `forbidden`
- foreign mating: `true`
- enclosure seed: `false`

The machine-readable authority is [`01_docs/capability-profile.json`](01_docs/capability-profile.json).

## Start

Run this from the project root. If this project is outside the circuits checkout, export `CIRCUITS_ROOT=/absolute/path/to/circuits` first.

```bash
export CIRCUITS_ROOT="${CIRCUITS_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}"
test -f "$CIRCUITS_ROOT/skills/pcb-design/SKILL.md" || { \
  echo "set CIRCUITS_ROOT to the circuits checkout" >&2; exit 2; }
python3 "$CIRCUITS_ROOT/skills/pcb-design/scripts/skill_reference_router.py" \
  --profile "$PWD/01_docs/capability-profile.json" \
  --at-stage PCB-COMMISSION --json
```

The first-article source commission is adopted: the brief/fact locks,
architecture, part dossiers, source electrical contracts, floorplan and routing
intent are authored. Connector qualification is phase-split without changing
the base receipt: the source phase admits only 20 typed physical-qualification
unknowns over a closed 3-assembly/11-ref census, while the future full phase
still requires zero unknowns. J9 identity, cable and internal restraint are now
document-closed; installed fit, route, reaction, tolerance and operation remain
physical holds. The miniDSP manual, CS5308P data sheet and OPA1656 data sheet
are retained locally with exact digests. All 58 used MPNs now have local
PDF/hash bindings; independent pin/footprint review and the qualifications in
`02_parts/README.md` remain separate.

The current schematic candidate has 299 components, 205 native nets and 868 pin
entries including 40 intentional NCs, presented on 19 pages. The previous
ink-clearance correction had accepted topology/render reviews. The subsequent
authority batch binds 25 manufacturer PDFs and corrects the input fuse to
2920L260/33DR, retaining its manual-supply exclusion. Root's independent
comparison found all 868 native pin/net memberships unchanged and only that
ordering-text change among all 299 components. All 84 project tests pass;
native ERC reports 0 errors with 2076 retained warnings. The old reviews are
preserved verbatim but STALE for the new PDF/parts/rules subject; no current
readability or full-ratings acceptance is claimed. See
[`08_reviews/DISPOSITIONS.md`](08_reviews/DISPOSITIONS.md) and
[`01_docs/SOURCE-CORRECTION-20260908-ink-clearance.md`](01_docs/SOURCE-CORRECTION-20260908-ink-clearance.md)
for earlier measured identities and limitations, and
[`01_docs/SOURCE-CORRECTION-20260908-authority-batch.md`](01_docs/SOURCE-CORRECTION-20260908-authority-batch.md)
for the new stopped subject. The saved PCB contains
299 fitted components (306 total footprints), but is **not placement-accepted**.
Its single bounded generation stopped at P-MODEL: 252/299 bodies resolve;
35 references lacked six library files and 12 lacked four custom-model bindings.
The subsequent source repair now resolves all47 of those references across
ten families; root independently adopted its six passing tests and unchanged
non-model footprint/electrical identity. See
[`01_docs/MODEL-SOURCE-20260908.md`](01_docs/MODEL-SOURCE-20260908.md).
The nominal/conservative bodies and isolated coupon results do not constitute
current-board model registration or exact connector/service-fit acceptance.
The saved project is partial (Default netclass only), and old DRC/policy
reports are stale. See
[`01_docs/BOARD-REALIZATION-20260908-initial.md`](01_docs/BOARD-REALIZATION-20260908-initial.md).
The old 213-footprint board and generated evidence are preserved recoverably.

The exact 51-code request is `06_build/sourcing/prelayout_request.json`: an
internal checklist, not a JLC-native upload. Public catalog evidence captured on
2026-09-08 from 04:03:21Z to 04:04:42Z passed the build-5 quantity floor for
51 codes/265 assembly-listed refs; 34 manually handled refs remain excluded.
It was revalidated during the 04:05:56Z public-only resume. ADR-0006 permits this design-only path;
the screen does not establish authenticated PCBA allocation or cart economics.
Its freshness and exact BOM must be rechecked whenever the driver resumes.

Connector SOURCE admission covers 3 assemblies/11 references with 20 explicitly
deferred physical unknowns. ADR-0007 permits prototype development before those
measurements; the base FULL receipt remains incomplete. Startup/partial-power,
thermal/protection, analog-quality, connector/service-fit and first-power
procedure qualifications remain owed. Public information cannot substitute
for those eventual physical observations, but they are not the former blanket
`CONNECTOR-FULL` stop on prototype layout work.

For a new source generation, use `bash 03_src/rebuild_all.sh`; preserve and
retire any existing request/checkpoint identity before rebuilding as required
by the driver. The authority batch has regenerated through prelayout to a
fresh schematic-review boundary; checkpoints verify 407 inputs/11 prelayout
files/7 schematic files. The older saved PCB remains stale. Before another
review commission, a fresh source owner will correct the demonstrated local
bypass/feedback placement deficiencies and declare their machine-graded
proximity budgets. Source changes require governed regeneration again; see
[`01_docs/research/20260908-authority-source-batch.md`](01_docs/research/20260908-authority-source-batch.md).
Do not resume unchanged stale checkpoints. A fresh run deliberately stops at
the first evidence checkpoint. The public-only
design path is `--resume-after-public-prelayout`; the authenticated-provider path
remains `--resume-after-prelayout`. After exact schematic reviews are accepted,
continue with `--resume-after-schematic-review`; the conductor preserves which
prelayout authority was used. A sealed release is immutable and does not by
itself mean this board was ordered.
