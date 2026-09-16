#!/usr/bin/env bash
# Deterministic route-authority rebuild driver for crow-mic-pod-v3 (it is
# config-driven and needs NO per-board edits: the board name comes from
# 03_src/floorplan.yaml `project.name`, exactly like the generic backend).
#
# WHEN TO USE WHICH DRIVER
#   rebuild_all.sh    — the FULL pipeline from tscircuit source: tsci build ->
#                       converter .kicad_sch -> ERC/parity -> board -> route ->
#                       gates. Run it when the SCHEMATIC changed, or for the
#                       from-scratch reproducibility proof (canon M3).
#   rebuild_reuse.sh  — THIS driver: the per-iteration / verification rebuild.
#                       Skips the tsci stage entirely and regenerates the board
#                       from committed 03_src config + the PINNED, committed
#                       03_tscircuit/kicad/<board>.kicad_sch, importing the
#                       PROMOTED KRT chain. Every step is deterministic, so it
#                       reproduces the board's routing gate exactly.
#
# WHY THE SPLIT (2026-07-23, measured on crow-rv2 + usb-hub): `tsci build` is
# NON-DETERMINISTIC — rerunning it churns the generated .kicad_sch by ~2900
# lines of UUID/ordering noise (connectivity stays stable per count_parity,
# but kicad-cli's --schematic-parity then reports phantom field diffs against
# the sealed board). The COMMITTED .kicad_sch is therefore the PINNED canonical
# schematic: this driver never regenerates it, it consumes it. This pattern was
# independently rewritten by THREE boards (usb-hub-3s-v2/-v3 rebuild_fast.sh,
# crow-rv2 rebuild_reuse.sh) — an M8 two-strike violation this template retires.
#
# VALID ONLY while KRT-routed pins do NOT move. If a signal-carrying pad's
# placement changes, re-route KRT on a track-free board, re-promote the chain
# into 03_src/route/, and commit it (there is deliberately no autorouter here).
#
# Order is BINDING (03_src/contracts.md): rules BEFORE import (canon R1),
# generate_rules LAST again after stitch (pcbnew saves clobber netclasses),
# then the full gate: kicad-cli pcb drc --severity-all --refill-zones
# --schematic-parity --exit-code-violations 04_kicad/<board>.kicad_pcb = 0/0/0.
# The pinned .kicad_sch is copied beside the board
# first — without it --schematic-parity SILENTLY SKIPS (crow-rv2 finding).
set -euo pipefail
cd "$(dirname "$0")/.."                       # -> project root (03_src/..)

# Share the full conductor's project-inode lock.  This is acquired before any
# generated receipt/directory/netlist write and creates no repository file.
exec 9<.
/usr/bin/flock -n 9 \
    || { echo "GATE INCOMPLETE [PCB-REBUILD-LOCK]: another crow PCB conductor is already running for this project" >&2; exit 2; }

if [ -e 01_docs/COMMISSIONING-HOLD.md ] || [ -L 01_docs/COMMISSIONING-HOLD.md ]; then
    echo "GATE INCOMPLETE [PCB-COMMISSION]: 01_docs/COMMISSIONING-HOLD.md still exists; close the brief/fact locks and adopt every schema example before rebuilding" >&2
    exit 2
fi

PY=/usr/bin/python3
# Resolve the shared skill scripts from an explicit circuits checkout or this
# project's repository. An explicit CIRCUITS_ROOT is authority: never replace
# a bad value with an ambient installed skill.
if [ -n "${CIRCUITS_ROOT:-}" ]; then
    REPO_ROOT="$(cd "$CIRCUITS_ROOT" 2>/dev/null && pwd)" \
        || { echo "GATE FAILED [PCB-TOOLCHAIN]: CIRCUITS_ROOT is not a readable directory: $CIRCUITS_ROOT" >&2; exit 2; }
else
    REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" \
        || { echo "GATE FAILED [PCB-TOOLCHAIN]: project is outside the circuits checkout; export CIRCUITS_ROOT=/absolute/path/to/circuits" >&2; exit 2; }
fi
S="$REPO_ROOT/skills/kicad-pcb/scripts"
CS="$REPO_ROOT/skills/pcb-design/scripts"
[ -f "$S/generate_board_generic.py" ] \
    || { echo "GATE FAILED [PCB-TOOLCHAIN]: resolved circuits checkout '$REPO_ROOT' does not contain skills/kicad-pcb; export CIRCUITS_ROOT=/absolute/path/to/circuits" >&2; exit 2; }
[ -f "$CS/connector_assembly_contract.py" ] \
    || { echo "GATE FAILED [PCB-TOOLCHAIN]: resolved circuits checkout '$REPO_ROOT' does not contain the pcb-design connector compiler" >&2; exit 2; }
FS="$(dirname "$(dirname "$S")")/jlcpcb-fab/scripts"
export PATH="$HOME/.bun/bin:$PATH"

run_stage() {
    local stage="$1"; shift
    "$PY" "$S/pcb_flow.py" run . --stage "$stage" -- "$@"
}

# Fail closed before the first generated receipt/directory/netlist write. The
# shared project-local gate reopens both stage checkpoints, the complete input
# census, exact request, live receipt and manufacturing readiness.
BOARD=$($PY - <<'PYEOF'
import re
txt = open("03_src/floorplan.yaml").read()
m = re.search(r'^\s*name:\s*["\']?([A-Za-z0-9_.-]+)', txt.split("project:", 1)[1], re.M)
print(m.group(1))
PYEOF
)
[ -n "$BOARD" ] || { echo "rebuild_reuse: no project.name in 03_src/floorplan.yaml"; exit 2; }
SCH="03_tscircuit/kicad/$BOARD.kicad_sch"
PRELAYOUT_RESUME_GATE="$REPO_ROOT/projects/crow-roof-array-v1/03_src/prelayout_resume_gate.py"
[ -f "$PRELAYOUT_RESUME_GATE" ] \
    || { echo "GATE FAILED [PCB-TOOLCHAIN]: missing crow prelayout resume gate: $PRELAYOUT_RESUME_GATE" >&2; exit 2; }
PRELAYOUT_AUTH_ARGS=()
if [ ! -e 06_build/sourcing/prelayout_receipt.json ] && \
   [ -f 06_build/sourcing/public_catalog_stock.json ] && \
   [ -f 01_docs/decisions/0006-public-catalog-prelayout-only.md ]; then
    PRELAYOUT_AUTH_ARGS=(--allow-public-catalog)
fi
$PY "$PRELAYOUT_RESUME_GATE" . --repo-root "$REPO_ROOT" \
    --context reuse-preflight --require-schematic \
    --pinned-schematic "$SCH" \
    --generated-schematic "04_kicad/$BOARD.kicad_sch" \
    --continuation "$0" \
    "${PRELAYOUT_AUTH_ARGS[@]}" \
    || exit $?

PIPELINE_EVIDENCE=06_build/verification/pipeline
mkdir -p "$PIPELINE_EVIDENCE/bundles"

# Connector assembly facts remain load-bearing on deterministic replay. This
# compiles the canonical evidence contract and stops on represented unknowns;
# it does not manufacture a realized-board service-geometry PASS.
# ADR0005 permits a nonorderable candidate with planned physical unknowns.
# Shared SOURCE/FULL admission preserves every unknown and rejects invalid or
# unclassified authority before TSX, placement or route work.
bash "$CS/connector_prototype_admission.sh" "$PY" "$CS" "[connector]" \
    01_docs/decisions/0005-first-article-only-release.md --compile-base

# P-MOD is source-only and cheap; the deterministic path must not bypass the
# architecture decision merely because it reuses a pinned schematic.
$PY "$S/module_first_check.py" . \
    || { echo "GATE FAILED P-MOD: module-first architecture contract"; exit 1; }
$PY "$S/rf_contract_check.py" . --require-applicability \
    || { echo "GATE FAILED RF-CONTRACT: explicit RF applicability/requirements"; exit 1; }
run_stage rf_context "$PY" "$S/rf_context.py" . \
    || { echo "GATE FAILED RF-CONTEXT: local RF source-card selection is incomplete"; exit 1; }
run_stage rf_solver "$PY" "$S/rf_solver.py" . \
    || { echo "GATE FAILED RF-SOLVER: a declared local solver job failed or exceeded its deadline"; exit 1; }
run_stage rf_source "$PY" "$S/rf_check.py" source . \
    || { echo "GATE FAILED RF-SOURCE: authored RF geometry/authority is inconsistent"; exit 1; }
$PY "$S/early_design_check.py" . \
    || { echo "GATE FAILED D-SPEC/E-PATH/E-SWDRV/E-SURGE: upstream design contract is red; deterministic replay may not bypass architecture"; exit 1; }
$PY "$S/rules_audit.py" . --phase source \
    || { echo "GATE FAILED A-SOURCE: net-class current/width/pour intent is malformed before deterministic replay"; exit 1; }

SCH="03_tscircuit/kicad/$BOARD.kicad_sch"      # the PINNED canonical schematic
[ -f "$SCH" ] || { echo "rebuild_reuse: pinned $SCH missing — run rebuild_all.sh once and COMMIT it"; exit 2; }

# Preserve an authenticated build/FINAL marker when route.import_source is
# explicitly `build`; deleting it here makes the deterministic driver destroy
# the very route lineage it is configured to import.  An explicit `promoted`
# source does not consult build/FINAL, so no filesystem-precedence cleanup is
# needed there either.  The importer owns source selection fail-closed.

# [1] Reproduce the netlist from the PINNED schematic without overwriting the
# checkpointed JLC/review subject.  KiCad rewrites the export clock, source
# path, generated sheet properties, instance UUIDs, and project-derived class
# labels even when electrical connectivity is unchanged.  Compare with the
# same narrowly normalized electrical digest used by PR-REVIEW, then keep
# downstream consumers on the frozen canonical bytes.
NETLIST="06_build/netlists/$BOARD.net"
if [ -L "$NETLIST" ] || [ ! -f "$NETLIST" ]; then
    echo "GATE FAILED [1] M-PIN: frozen canonical netlist is missing or not regular: $NETLIST" >&2
    exit 2
fi
NETLIST_CANDIDATE=$(mktemp "/tmp/crow-${BOARD}-reuse-netlist.XXXXXX")
trap 'rm -f -- "$NETLIST_CANDIDATE"' EXIT
kicad-cli sch export netlist --format kicadsexpr \
    -o "$NETLIST_CANDIDATE" "$SCH"
if ! "$PY" - "$S" "$NETLIST_CANDIDATE" "$NETLIST" <<'PYEOF'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from pre_route_review_check import netlist_digest

candidate = Path(sys.argv[2])
frozen = Path(sys.argv[3])
if netlist_digest(candidate) != netlist_digest(frozen):
    raise SystemExit(1)
PYEOF
then
    echo "GATE FAILED [1] M-PIN: reproduced electrical netlist differs from the frozen canonical netlist; no frozen artifact was replaced" >&2
    exit 1
fi
rm -f -- "$NETLIST_CANDIDATE"
trap - EXIT

$PY "$S/pre_route_review_check.py" . --phase schematic \
    --netlist "$NETLIST" \
    || { echo "GATE FAILED [1a] PR-REVIEW: topology witness missing, stale, or defective"; exit 1; }

$PY "$S/electrical_closure.py" . \
    --json "$PIPELINE_EVIDENCE/electrical_closure.json" \
    --stage-bundle "$PIPELINE_EVIDENCE/bundles/electrical_closure" \
    --stage-result "$PIPELINE_EVIDENCE/E-CLOSURE.stage.json" \
    || { echo "GATE FAILED [1a] E-CLOSURE: composed electrical battery is incomplete or stale"; exit 1; }

# Exact JLC authority was reverified by reuse-preflight before any generated
# write; later stages may not substitute a catalog or prior-circuit receipt.

# [2] board (placement + zones) from committed floorplan.yaml  [SHARED]
$PY "$S/generate_board_generic.py" 03_src/floorplan.yaml -o "04_kicad/$BOARD.kicad_pcb"
# KiCad parity discovers the comparison schematic only beside the board.  The
# reuse preflight already required that frozen copy to exist byte-identically;
# never rewrite it here.

# [2a] Physical/schematic/footprint pin identity, before any placement review
# or promoted-route import.
$PY "$S/pin_map_check.py" . --board "04_kicad/$BOARD.kicad_pcb" \
    --circuit-json 03_tscircuit/build/circuit.json \
    || { echo "GATE FAILED [2a] P-PINMAP: reconcile pin identities before placement/routing work"; exit 1; }

# [3] placement/pad invariants, if the board defines them  [per-board gate]
if [ -f 03_src/audit_board.py ]; then $PY 03_src/audit_board.py; fi
$PY "$S/placement_routability_preflight.py" grade . \
    --board "04_kicad/$BOARD.kicad_pcb" \
    --placement-config 03_src/placement_gates.json \
    --json 06_build/verification/placement_routability_receipt.json \
    --stage-bundle "$PIPELINE_EVIDENCE/bundles/placement_feasibility" \
    --stage-result "$PIPELINE_EVIDENCE/P-FEASIBILITY.stage.json" \
    || { echo "GATE FAILED [3] KICAD-PLACEMENT: physical placement and declared routability do not jointly pass"; exit 1; }
$PY "$S/model_coverage_check.py" "04_kicad/$BOARD.kicad_pcb" \
    -o 06_build/verification/model_coverage.json \
    || { echo "GATE FAILED [3m] P-MODEL: every fitted footprint needs a renderer-resolvable 3D body before placement review"; exit 1; }
$PY "$S/pad_separation.py" "04_kicad/$BOARD.kicad_pcb" --project . \
    || { echo "GATE FAILED [3] P-PADSEP: separate-footprint copper clearance"; exit 1; }

# [3a] Datasheet placement policy, before promoted-route import.  This is the
# same P-ADJ evaluator used by the final release audit, not a parallel metric.
$PY "$S/policy_audit.py" . --board "$BOARD" --skip-drc --phase placement \
    || { echo "GATE FAILED [3a] P-ADJ: datasheet placement budget violated before routing"; exit 1; }

$PY "$S/generate_rules_generic.py" .
kicad-cli pcb drc --severity-all --refill-zones --schematic-parity \
    --format json -o 06_build/drc/pre_route.json "04_kicad/$BOARD.kicad_pcb"
$PY "$S/placement_drc_check.py" 06_build/drc/pre_route.json \
    || { echo "GATE FAILED [3b] P-DRC: exact placement has a short, clearance, library, hole, or parity defect before human review"; exit 1; }

# [4] netclasses + .kicad_dru BEFORE import (canon R1: rules ride into the route)  [SHARED]
#     (generate_rules_generic itself purges kicad-cli's stray
#     <board>.kicad_pcb.kicad_pro/.prl droppings — do NOT re-add a bespoke rmstray)
$PY "$S/generate_rules_generic.py" .

# [4a] P-LAND before promoted-route import: fail on a package/placement launch
# wall while the board is still track-free, not after replaying/stitching it.
$PY "$S/escape_check.py" --board "04_kicad/$BOARD.kicad_pcb" \
    || { echo "GATE FAILED [4a] P-LAND: a placed pad cannot launch its declared width"; exit 1; }

$PY "$S/tier_preflight.py" . \
    || { echo "GATE FAILED [4b] R-PREFLIGHT: route geometry disagrees with the fab tier"; exit 1; }
$PY "$S/route_and_stitch_generic.py" prep 03_src/route.yaml

$PY "$FS/model_registration_gate.py" . --board "04_kicad/$BOARD.kicad_pcb" \
    || { echo "GATE FAILED [4c] P-MODEL-REG: native body, footprint, courtyard, or attachment datums disagree"; exit 1; }
timeout --signal=TERM --kill-after=10s 180s \
    $PY "$FS/connector_orientation_gate.py" . --board "04_kicad/$BOARD.kicad_pcb" \
    || { echo "GATE FAILED [4d] P-ORIENT: connector mouth/edge geometry, render evidence, or explicit approval is missing, stale, or defective"; exit 1; }
$PY "$S/pre_route_review_check.py" . --phase placement \
    --board "04_kicad/$BOARD.kicad_pcb" \
    || { echo "GATE FAILED [4c] P-ROUTEBASE/PR-REVIEW: prepared-route compatibility or placement evidence missing, stale, or defective"; exit 1; }

# [5] import the PROMOTED KRT chain once into the track-free board  [SHARED]
$PY "$S/route_and_stitch_generic.py" import 03_src/route.yaml
# [5b] taps — no-op unless route.yaml configures `taps:`  [SHARED]
$PY "$S/route_and_stitch_generic.py" taps   03_src/route.yaml

# [6] stitch: pours + stitch/thermal vias + island heal + gate  [SHARED]
$PY "$S/route_and_stitch_generic.py" stitch 03_src/route.yaml
$PY "$S/critical_route_check.py" . --board "04_kicad/$BOARD.kicad_pcb" --require-connected \
    || { echo "GATE FAILED [6a] R-CRITESC: critical-pair copper is incomplete"; exit 1; }
$PY 03_src/check_realized_routes.py "04_kicad/$BOARD.kicad_pcb" \
    --json 06_build/verification/realized_route_receipt.json \
    || { echo "GATE FAILED [6b] R-POD-PATH: regulator, surge, or audio-clamp realized copper violates its exact route contract"; exit 1; }

# [7] generate_rules LAST — pcbnew saves in the chain clobber netclasses  [SHARED]
$PY "$S/generate_rules_generic.py" .
$PY "$S/rules_audit.py" . --board "04_kicad/$BOARD.kicad_pcb" \
    || { echo "GATE FAILED [7a] A-CLASS/A-AGREE/A-AMP/A-FIRE/A-ORDER: generated rules do not enforce authored copper intent"; exit 1; }
run_stage rf_realized "$PY" "$S/rf_check.py" realized . --board "04_kicad/$BOARD.kicad_pcb" \
    || { echo "GATE FAILED [7c] RF-REALIZED: saved RF copper/fence evidence is incomplete"; exit 1; }

# [8] Atomic route acceptance over the exact reused board.
run_stage route_acceptance "$PY" "$S/route_acceptance_gate.py" grade . \
    --board "04_kicad/$BOARD.kicad_pcb" --mode full \
    --drc-json 06_build/route/gate.json \
    --json 06_build/verification/route_acceptance_receipt.json \
    || { echo "GATE FAILED [8] KICAD-ROUTING: final reused copper was not atomically accepted"; exit 1; }
echo "rebuild_reuse: route acceptance GREEN from committed source"
