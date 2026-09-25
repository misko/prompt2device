#!/usr/bin/env bash
# Build a private, schematic-only evidence bundle for an explicitly admitted
# prototype-only critical-part selection.  This is deliberately not a reduced
# form of rebuild_all.sh: it cannot create a board, a route receipt, a release
# artifact, or an order input.
set -euo pipefail
cd "$(dirname "$0")/.."

BOARD=crow_carrier
TSX=crow_carrier
PY=/usr/bin/python3

if [ -n "${CIRCUITS_ROOT:-}" ]; then
    REPO_ROOT="$(cd "$CIRCUITS_ROOT" 2>/dev/null && pwd)" \
        || { echo "GATE FAILED [PCB-TOOLCHAIN]: CIRCUITS_ROOT is not readable" >&2; exit 2; }
else
    REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" \
        || { echo "GATE FAILED [PCB-TOOLCHAIN]: project is outside circuits" >&2; exit 2; }
fi
S="$REPO_ROOT/skills/kicad-pcb/scripts"
CS="$REPO_ROOT/skills/pcb-design/scripts"
for required in "$S/tsx_preflight.py" "$S/circuit_json_diagnostics.py" \
                "$S/circuit_json_to_kicad_sch.py" "$S/render_schematic_pdf.mjs" \
                "$CS/critical_part_selection_admission.py"; do
    [ -f "$required" ] || { echo "GATE FAILED [PCB-TOOLCHAIN]: missing $required" >&2; exit 2; }
done
[ -x 03_tscircuit/node_modules/.bin/tsci ] \
    || { echo "GATE FAILED [TSCI]: frozen local toolchain is missing; do not install from this prototype producer" >&2; exit 2; }

# This is the sole admission exception.  The generic checker validates the
# typed prototype_only suitability status, independent review/evidence, and
# open deferred DESIGN_CLEAN finding(s).  --require-prototype rejects PASS and
# NOT_APPLICABLE as well as incomplete selections, so this path cannot become
# a second ordinary producer.
"$PY" "$CS/critical_part_selection_admission.py" . --require-prototype \
    || { rc=$?; echo "GATE INCOMPLETE [PROTOTYPE-SELECTION]: this producer requires an admitted typed prototype_only selection" >&2; exit "$rc"; }

# Cheap source checks remain useful.  No generated board, route, layout, fab,
# release, or order gate is reachable from this script.
"$PY" "$S/tsx_preflight.py" . \
    || { echo "GATE FAILED [TSX-PRE]: source/pad declarations are malformed" >&2; exit 1; }

STAMP="$(date -u +%Y%m%dT%H%M%SZ)-$$"
OUT="06_build/prototype_only/$STAMP"
mkdir -p "$OUT"
WORK="$(mktemp -d "$OUT/.tsci-work.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# tsci writes beneath its working directory.  Build a minimal private copy and
# share the already-frozen dependency tree read-only by convention, so this
# path neither reads nor overwrites 03_tscircuit/dist, build, kicad, or 04_kicad.
mkdir -p "$WORK/03_tscircuit"
cp -a 03_tscircuit/src "$WORK/03_tscircuit/"
cp -a 03_tscircuit/package.json 03_tscircuit/bun.lock "$WORK/03_tscircuit/"
ln -s "$(pwd)/03_tscircuit/node_modules" "$WORK/03_tscircuit/node_modules"
( cd "$WORK/03_tscircuit" && ./node_modules/.bin/tsci build --disable-pcb "src/$TSX.tsx" )
cp "$WORK/03_tscircuit/dist/src/$TSX/circuit.json" "$OUT/circuit.json"

"$PY" "$S/circuit_json_diagnostics.py" "$OUT/circuit.json" \
    || { echo "GATE FAILED [TSX-DIAG]: private circuit contains hard producer diagnostics" >&2; exit 1; }
"$PY" "$S/circuit_json_to_kicad_sch.py" "$OUT/circuit.json" \
    -o "$OUT/$BOARD.kicad_sch" --parts 02_parts \
    --net-aliases 03_tscircuit/net_aliases.txt
kicad-cli sch export netlist --output "$OUT/$BOARD.net" "$OUT/$BOARD.kicad_sch"

NET_ALIAS_ARGS=()
[ -f 03_tscircuit/net_aliases.txt ] && NET_ALIAS_ARGS=(--net-aliases 03_tscircuit/net_aliases.txt)
node "$S/render_schematic_pdf.mjs" "$OUT/circuit.json" "$OUT/schematic.pdf" \
    --title "Crow USB Carrier v1 — PROTOTYPE ONLY" "${NET_ALIAS_ARGS[@]}" \
    --toolchain-package 03_tscircuit/package.json \
    --sheet-text-scale xmos_core:2.6:pins \
    --pin-index "U_XU:$OUT/$BOARD.net"

OUT="$OUT" "$PY" - <<'PY'
import hashlib, json, os, subprocess
from pathlib import Path

out = Path(os.environ["OUT"])
root = Path.cwd()
files = ["circuit.json", "crow_carrier.kicad_sch", "crow_carrier.net", "schematic.pdf"]
source_files = sorted((root / "03_tscircuit/src").rglob("*.tsx"))
source_files += [root / name for name in (
    "03_tscircuit/package.json", "03_tscircuit/bun.lock",
    "03_tscircuit/net_aliases.txt", "03_src/rules/critical_part_selection.yaml",
    "03_src/rules/assembly.yaml", "01_docs/findings.yaml",
    "02_parts/TPD2EUSB30ADRTR/part.yaml",
    "01_docs/research/2026-09-24-public-stock-569/public-stock.json",
    "01_docs/research/2026-09-25-ti-usb-esd-prototype-test-plan.md",
    "08_reviews/2026-09-25_ti-usb-esd-prototype-only_terra.md",
)]
receipt = {
    "schema": 1,
    "status": "PROTOTYPE_ONLY",
    "scope": "private source/schematic evidence only; no layout, release, fabrication, order, or electrical qualification claim",
    "git_head_at_build": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    "selection_gate": "skills/pcb-design/scripts/critical_part_selection_admission.py --require-prototype",
    "inputs": {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
               for path in source_files},
    "artifacts": {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in files},
}
(out / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
PY
echo "PROTOTYPE-ONLY PASS: private source/schematic bundle at $OUT"
