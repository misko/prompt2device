#!/usr/bin/env bash
# Shared mechanics for a project whose accepted ADR already authorizes an
# unqualified prototype. This script creates no authorization or physical PASS.
# Usage: bash connector_prototype_admission.sh PY CS STAGE ADR [--compile-base]
set -euo pipefail
PY="${1:?Python interpreter required}"
CS="${2:?PCB design scripts directory required}"
stage="${3:?Stage label required}"
decision="${4:?Existing project prototype decision required}"
case "$decision" in
    *../*|*/./*|*//*) echo "Prototype decision path must be canonical" >&2; exit 1 ;;
    01_docs/decisions/*.md) ;;
    *) echo "Prototype decision must be a project decision record" >&2; exit 1 ;;
esac
if [ ! -f "$decision" ] || [ ! -s "$decision" ] || [ -L "$decision" ]; then
    echo "Missing or nonregular prototype decision: $decision" >&2; exit 1
fi
case "${5:-}" in
    "") [ "$#" -eq 4 ] ;;
    --compile-base)
        [ "$#" -eq 5 ]
        base_rc=0
        "$PY" "$CS/connector_assembly_contract.py" --project . \
            --contract 03_src/rules/connector_assemblies.yaml \
            --output 06_build/verification/connector_assembly_contract.json || base_rc=$?
        case "$base_rc" in
            0|2) ;;
            *) echo "$stage invalid connector base authority" >&2; exit "$base_rc" ;;
        esac
        ;;
    *) echo "Unknown prototype admission option" >&2; exit 1 ;;
esac
# SOURCE reopens exact base/compiler/contract/evidence/policy bytes, rejects
# unclassified source unknowns, and requires actual connector identities.
"$PY" "$CS/connector_assembly_phase_gate.py" --project . --phase source \
    --contract 03_src/rules/connector_assemblies.yaml \
    --policy 03_src/rules/connector_assembly_phases.yaml \
    --base-receipt 06_build/verification/connector_assembly_contract.json \
    --output 06_build/verification/connector_assembly_source_gate.json
full_rc=0
"$PY" "$CS/connector_assembly_phase_gate.py" --project . --phase full \
    --contract 03_src/rules/connector_assemblies.yaml \
    --policy 03_src/rules/connector_assembly_phases.yaml \
    --base-receipt 06_build/verification/connector_assembly_contract.json \
    --output 06_build/verification/connector_assembly_full_gate.json || full_rc=$?
case "$full_rc" in
    0) echo "$stage CONNECTOR-FULL closed; independent geometry/review gates still required" ;;
    2) echo "$stage CONNECTOR-FULL INCOMPLETE: $decision admits prototype design only. Physical fit/service remains owed. FIRST-ARTICLE-ONLY / DO-NOT-ORDER." ;;
    *) echo "$stage CONNECTOR-FULL invalid authority; prototype admission rejected" >&2; exit "$full_rc" ;;
esac
