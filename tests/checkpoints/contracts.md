# contract: tests/checkpoints/

Purpose: test agents resuming bounded PCB engineering checkpoints with the
current skill. This is an opt-in testing consumer, not production release authority.

## Allowed

| Pattern | What |
|---|---|
| `contracts.md` | This contract |
| `README.md` | Interfaces, reproduction, limitations and case authoring |
| `*.py` | Runner, schema, explicit agent adapter and suite selection |
| `suites.json` | Named selections of checkpoint cases |
| `cases/**` | Case manifests, task context, snapshots, independent graders and maintainer controls |
| `incidents/*.md` | Compact Crow incident provenance and regression properties; no raw private transcripts |
| `evidence/**` | Compact, sanitized validation summaries; no credentials or raw conversations |

Runtime artifacts belong outside the repository in a fresh run directory.
Snapshots are disposable test inputs, not permission to modify sealed releases.
Reference repairs and graders stay outside solver workspaces. Historical
reductions must identify their source and disclose synthetic geometry/data.

## Audit

- Run `tests/t1_checkpoint_framework.py` and case controls without model calls.
- Verify initial FAIL, valid repair PASS and invalid shortcut FAIL per case.
- Agent runs require explicit opt-in, model and bounded execution. Never claim
  usage or cost that was not measured; distinguish solver and infrastructure failures.
- No change here grants production evidence reuse or substitutes for board gates.
