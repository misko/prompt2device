# Crow P1 relative-path terminal-failure evidence

This tracked archive preserves verbatim copies of the terminal one-attempt
campaign receipt, allocated envelope, runtime log, reviewed external envelope,
tool manifest, and formal admission review. It is historical evidence only;
neither the copies nor this README reclassify, retry, or alter the originals.

The original local receipt is
`06_build/task_runs/p1_floorplan_569_after_launch_abort_r1-4d8a216d0d254c4db60305b0528ba3c9/attempt.json`.
It records terminal `FAIL`, return code `1`, no outputs, no completion, missing
candidate/evidence/measurements/result handback, and a passing read-only writer
scope with equal before/after hashes and `changed_paths: []`.

The worker received `projects/crow-usb-carrier-v1` while its CWD already was
the project directory, so it resolved a nonexistent nested
`projects/crow-usb-carrier-v1/02_parts` path. This is a launch path-resolution
defect; the receipt proves no board, routing, source change, or project write.

Three envelope identifiers are preserved without conflation:

* `attempt.json` binds conductor canonical digest
  `b91f803e87ce5c4f15710a5056555071b421ec2c884abda431574bd2042f8308`.
* `allocated-envelope.json` is the received task-run envelope, SHA-256
  `a736d05a6471fb76c367be60484242a205c736c85f8c74535caaa150ff1f01fb`.
* `reviewed-envelope.schema2.json` is the separately reviewed external envelope,
  SHA-256 `43901bc23340bae467b460eb54df13372598a43cd05683c7069fa0693475f25d`.

Their differing output-path allocation/canonicalization records are retained
as facts. `SHA256SUMS` authenticates every tracked copy.
