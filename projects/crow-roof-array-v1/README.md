# crow-roof-array-v1

System-integration authority for the crow roof array. The original request and
whole-appliance acceptance criteria live in
[`01_docs/BRIEF.md`](01_docs/BRIEF.md); current work lives in
[`01_docs/STATUS.md`](01_docs/STATUS.md). This project deliberately remains on
commissioning hold and does not own a PCB release. The central carrier is
developed in [`../crow-audio-carrier-v1`](../crow-audio-carrier-v1) and the
replicated microphone pod in [`../crow-mic-pod-v3`](../crow-mic-pod-v3), per
[ADR 0009](01_docs/decisions/0009-split-system-into-two-single-board-releases.md).
The publication boundary binds that boardless scope and those two PCB children
through [`01_docs/project-scope.json`](01_docs/project-scope.json); it expands
this parent into both child release checks rather than treating the parent as a
zero-board PCB project.

The first architecture comparison is
[`01_docs/reports/2026-09-01-star-array-architecture-study.md`](01_docs/reports/2026-09-01-star-array-architecture-study.md).
The user's 3D/identity/PoE clarification is analyzed in
[`01_docs/reports/2026-09-01-dimensionality-identity-and-poe-addendum.md`](01_docs/reports/2026-09-01-dimensionality-identity-and-poe-addendum.md).
The subsequent 8 m-diameter, planar and 120-second clarification is analyzed in
[`01_docs/reports/2026-09-01-planar-8m-diameter-120s-follow-up.md`](01_docs/reports/2026-09-01-planar-8m-diameter-120s-follow-up.md).
The final caller-scope clarification is analyzed in
[`01_docs/reports/2026-09-01-within-file-stationary-caller-scope.md`](01_docs/reports/2026-09-01-within-file-stationary-caller-scope.md).
The accepted Raspberry Pi 5 host and network boundary are developed in
[`01_docs/reports/2026-09-01-raspberry-pi-5-roof-appliance-integration.md`](01_docs/reports/2026-09-01-raspberry-pi-5-roof-appliance-integration.md).
The current carrier ADC decision is [ADR 0010](01_docs/decisions/0010-single-cs5308p-audio-carrier.md):
one hardware-controlled CS5308P feeding MCHStreamer TDM8, replacing the
earlier four-stereo-ADC study.
The leading study is now an eight-channel planar seven-outer-plus-center array
feeding a no-custom-firmware, shared-clock Raspberry Pi 5 roof appliance. One
external PoE/Ethernet uplink and a short internal USB audio-module link are
accepted at the system boundary. Recognition is an anonymous source track
inside one 120-second file while the crow remains approximately stationary;
there is no cross-file biological-identity requirement. The nominal 4 m radius
is user-selected, but the actual roof coordinates, stationarity gate, exact Pi
SKU, storage, PoE power implementation and cooling are not yet qualified. The
shared carrier/pod spoke contract is
[`03_src/rules/spoke_interface.yaml`](03_src/rules/spoke_interface.yaml); 4 m
is the nominal array radius, per-port installed lengths remain survey facts,
and 15 m is the unqualified design/bench reference maximum.
The archived pod/central boards are explicitly not reusable as a pair because
their custom-RJ45 power contacts conflict across a straight-through cable.

## Capability

- target: `design` (system integration record; PCB children target `release`)
- signal integrity: `high_speed_digital`
- assembly: `jlcpcb`
- firmware: `forbidden`
- foreign mating: `true`
- enclosure seed: `true`

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

The system commission is incomplete. Read
[`01_docs/COMMISSIONING-HOLD.md`](01_docs/COMMISSIONING-HOLD.md) and preserve its
whole-appliance acceptance boundaries. This boardless parent never runs a PCB
conductor or mints a PCB release. Each child has its own adopted commission,
source, stage checkpoints and rebuild instructions; the parent's remaining
roof/appliance qualifications do not themselves prohibit the child laboratory
prototype work authorized by their own decisions.

For release status, read the child READMEs and this system's status beacon.
From the repository root, verify the combined publication boundary with:

```bash
python3 skills/pcb-design/scripts/pcb_publication_gate.py \
  --project projects/crow-roof-array-v1
```

This expands the parent into both child checks; an unfinished carrier still
fails even when the pod release passes. Immediately before a main-branch
publication, use the gate's exact `--base` and `--head` form as required by
[`contracts.md`](contracts.md). A sealed PCB release is immutable; it does not
establish allocation, an order, first-article results or whole-appliance acceptance.
