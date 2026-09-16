#!/usr/bin/env bash
# Compatibility entry point under existing user-accepted carrier ADR0007.
# The common SOURCE/FULL mechanics live once in the shared PCB design backend.
set -euo pipefail
PY="${1:?Python interpreter required}"
CS="${2:?PCB design scripts directory required}"
stage="${3:?Stage label required}"
exec bash "$CS/connector_prototype_admission.sh" "$PY" "$CS" "$stage" \
    01_docs/decisions/0007-prototype-before-physical-qualification.md
