# Native parity bridge schema-contract follow-up review

Reviewed commit: `0a02e31417105726ea0e59f15b4057cfb06a00ba`

Verdict: **PASS — schema-contract documentation scope only.**

The commit changes exactly the six `pin_aliases` reader rows in both the
generic 02_parts contract template and Crow's mirrored contract. Each now
names `part_identity.py`, which directly reads `pin_aliases` and all five
declared child keys in `alias_map()`. This is the truthful reader after the
previous commit factored that logic out of `pin_map_check.py`; the latter now
imports the helper and no longer owns those reads.

Validation:

- Worktree is clean at the reviewed commit.
- `git diff --check 0a02e314^ 0a02e314`: passed.
- `schema_reader_audit.py --root /tmp/crow-native-parity-bridge-20260923
  --families`: exited successfully and lists all six alias rows with
  `part_identity.py` as reader.

No electrical source, generator code, PCB, schematic, or release artifact was
changed by this follow-up. Broader root-workspace schema and documentation
checks remain outside this narrow review.

## Ratchet follow-up assessment

The proposed `PROVEN_FLOOR` update from 827 to 874 is **accepted and
required** by the existing ratchet contract. The governing test measures the
repository on every run and requires exact equality between the measured
`PROVEN` count and `PROVEN_FLOOR`; it rejects both a lowered value and a value
that lags newly proven rows. The full-root result supplied for this source tree
is 23 governed families and 874 proven rows, while the governed-family floor
already remains 23. Therefore a monotone 827-to-874 update is the correct
source-only repair; it does not waive or relax coverage.

My isolated parity worktree cannot reproduce the fleet denominator because it
does not contain the full project set recognized by the auditor. The result is
therefore based on inspection of the audit/test logic and root's complete-tree
measurement, rather than treating that sparse-worktree `UNGRADED` result as a
failure of the proposed floor update.
