# crow-usb-carrier-v1

PCB commissioning scaffold. The original request and acceptance criteria live in [`01_docs/BRIEF.md`](01_docs/BRIEF.md); current work lives in [`01_docs/STATUS.md`](01_docs/STATUS.md).

## Capability

- target: `design`
- signal integrity: `high_speed_digital`
- assembly: `jlcpcb`
- firmware: `forbidden`
- foreign mating: `false`
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

This is a scaffold, not a passed commission. Read [`01_docs/COMMISSIONING-HOLD.md`](01_docs/COMMISSIONING-HOLD.md), preserve the original brief, close its fact locks, and replace or explicitly adopt every seeded example. Do not run either rebuild conductor while the hold exists; both fail closed.

Current source state is a reviewed 569-component / 65-reference ADC proposal,
including the planned `C_ADC_3V3X_OK_VDD` supervisor bypass and a project-only
P-MOD ordering repair. It has no new producer, schematic checkpoint, native
board, P2 acceptance, or release status. Earlier 568-component generated
artifacts remain historical evidence and must not be rebound; see
[`01_docs/STATUS.md`](01_docs/STATUS.md) before any conductor admission.

After the separately typed commission, architecture, and sourcing admission evidence is reviewed and its hold is removed, start the full conductor with `bash 03_src/rebuild_all.sh`. A fresh run deliberately stops at evidence and operator checkpoints. After accepting the exact schematic review checkpoint, continue without rebuilding TSX using `bash 03_src/rebuild_all.sh --resume-after-schematic-review`. A sealed release is immutable and does not by itself mean this board was ordered.
