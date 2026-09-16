# contract: system-integration project root

**Purpose** — retain whole-appliance requirements, decisions, shared interface
authority, and acceptance planning for a system implemented by multiple
self-contained PCB child projects. This parent deliberately owns no fabricable
board and no PCB release.

The exact publication scope is `01_docs/project-scope.json`. Its
`pcb_children` are not documentation links: the PCB publication gate replaces
this parent with those projects and requires every child to own exactly one
tracked live board and pass the ordinary sealed-release boundary.

## Ownership

| Folder | Authority |
|---|---|
| `01_docs/` | system requirements, accepted architecture decisions, system status, evidence, and whole-appliance test planning |
| `02_parts/` | source records used only by system-level analysis; a child PCB must carry its own complete part authority |
| `03_src/` | shared interface and integration rules; never a generator authority for a parent PCB |
| `03_tscircuit/` | retained scaffold contract only; no parent circuit source is permitted |
| `04_kicad/` | retained scaffold contract only; no `*.kicad_pcb` is permitted |
| `05_firmware/` | system integration records only when expressly commissioned |
| `06_build/` | disposable integration results, gitignored |
| `07_releases/` | retained scaffold contract only; this parent mints no PCB release |
| `07_enclosure_releases/` | independently governed system/enclosure releases when commissioned |
| `08_reviews/` | system review archive; never a substitute for each child's PCB reviews |

Each PCB child is standalone and transferable under its own board-project
contract. Parent records may constrain a child through a copied and checked
interface contract, but a child build or reorder must not depend on sibling or
parent files at runtime.

## Allowed at root

| Pattern | What |
|---|---|
| `README.md` | system scope, child links, status, and verification entry point |
| `contracts.md` | this file |
| `.gitignore` | ignores disposable `06_build/` data without hiding decisions or part evidence |
| `.gitattributes` | repository handling for review-critical binary evidence |
| contracted project folders | the folders listed above, each with its own `contracts.md` |

## Forbidden at root

- Any parent `*.kicad_pcb`, Gerber/drill archive, PCB assembly package, or PCB
  release. These belong to one declared child.
- Any runtime build dependency from a child into this parent or another child.
- A missing, malformed, self-referential, duplicated, or untracked
  `01_docs/project-scope.json` declaration.
- Reclassifying a project that owned a live board at either side of a
  publication diff. The publication gate checks both Git trees.
- Loose design docs or scripts at root, generated outputs outside `06_build/`,
  and filename-based revision copies such as `*_old` or `*_v2`.

## Fresh-agent verification

1. Read `01_docs/project-scope.json`, `README.md`, `01_docs/BRIEF.md`, and ADR
   0009. Confirm the declaration names the carrier and pod children exactly.
2. Confirm this parent owns no tracked `04_kicad/*.kicad_pcb` and no release
   payload below `07_releases/`.
3. Confirm each declared child owns exactly one tracked live PCB and remains
   independently understandable, rebuildable, reviewed, and releasable.
4. Run `python3 skills/pcb-design/scripts/pcb_publication_gate.py --project
   projects/crow-roof-array-v1`. It must report the `SYSTEM` expansion and then
   grade both children; an unfinished or unsealed child remains a failure.
5. Before publication, run the same gate with `--base <publication-base>` and
   `--head <candidate-head>` and require `P-PUBLISH PASS`.

## Validate and repair

- Treat a parent board or release payload as a scope defect; move its source
  into a newly commissioned PCB child and add that child to the sorted scope
  declaration.
- Treat a missing child, a child with zero/multiple boards, or an unsealed child
  as a publication failure; correct the child rather than weakening the parent
  declaration.
- Update integration decisions and child contracts together when an interface
  changes. Reseal only the child PCB whose material design authority changed,
  while the publication gate still regrades every declared child.
