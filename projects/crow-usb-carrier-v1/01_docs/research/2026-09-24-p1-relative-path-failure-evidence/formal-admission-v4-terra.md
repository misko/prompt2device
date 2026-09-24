# Crow 569/45 P1 formal admission review v4 — Terra

**Disposition: SOUND — admitted for exactly one isolated P1 run.**

* Exact envelope SHA-256: `43901bc23340bae467b460eb54df13372598a43cd05683c7069fa0693475f25d` — verified.
* Exact tool-manifest SHA-256: `482027fe1368c1fccc1e76921626c90f047f52092655ad122348604c3def67d4` — verified.
* Source HEAD and `origin/main`: both
  `6d18f40930e8b9e343623a17f4c7e59b4bd95472`; the scoped project is clean.

## Closed execution identity

All 187 manifest entries exist and match their SHA-256 values.  The previous
script, ambient-runtime, and PATH-resolution defects are closed:

* the direct wrapper has `#!/usr/bin/bash`, and `/usr/bin/bash` is manifest-bound;
* the verifier has `#!/usr/bin/python3` and invokes manifest-bound
  `/usr/bin/git` by absolute path for both HEAD and clean-tree checks;
* `/usr/bin/python3`, `/usr/bin/timeout`, and `/usr/bin/kicad-cli` are
  manifest-bound; the worker uses the latter two native executables by
  absolute path;
* the wrapper, `pcb_flow.py`, `process_runner.py`, `pipeline_execution.py`,
  related pipeline modules, worker, verifier, geometry helper, and invoked
  generation/measurement scripts are manifest-bound.

The exact direct `verify_envelope.py` preflight returned `PASS`, verifying the
envelope digest, source identity, clean scoped project, manifest, task/run
identity, full 408-item input packet, and deadline.  The envelope permits one
non-improving attempt, zero replacements, and has a read-only source writer
scope.  The wrapper requires a new `/tmp` candidate workspace and applies a
1200-second timeout with TERM then a 30-second KILL grace period; preflight
requires more than 21 minutes remaining before dispatch.

## Scope and gate integrity

The graph has exactly one active `p1_floorplan_569_after_launch_abort` root
with `max_attempts: 1`, no retired-root references, and seven P2 nodes that
both depend on and backtrack to it.  The historical launch-abort remains
terminal and does not grant an automatic retry.

The worker contains exactly one native board-generator invocation and no
resume, import, router, or repair path.  It requires the final board,
candidate output, and evidence-board SHA-256 values to agree, emits the
evidence archive and archive digest, and marks a failed delivery terminal.
P-ADJ and P-ADJ-PAIR remain explicit P2-owned measured debt rather than P1
passes.  Connector FULL remains `INCOMPLETE_19_PHYSICAL_TARGETS`; routing and
promotion are explicitly prohibited.  The independent 45-page schematic
pre-route review check also passed 2/2 against the current exact subject.

This review authorizes no P2, P3, routing, promotion, release, or ordering
work.  No task-run, wrapper, generator, project write, or git mutation was
performed during this review.
