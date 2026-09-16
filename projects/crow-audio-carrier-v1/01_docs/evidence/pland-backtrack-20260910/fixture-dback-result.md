# P-LAND fixture-admission D-BACK — INCOMPLETE, diagnostic cap exhausted

Actual administrative completion: 2026-09-10T21:42:07.980188+00:00. The requested 21:39Z closure target was missed. The original envelope deadline remains 2026-09-10T21:56:28Z with its final 120-second reserve; neither that deadline nor any attempt cap was extended. Root requested administrative closure only after stopping diagnostics. No native, public CLI, fixture or implementation work resumed after the third failure.

Decision: this handback does not admit a maintained regression, production repair, placement progress, or a passing witness. Three native census commands failed before serializing their buffered census. All substantive native/public validation rows below remain unresolved. No API exception, zero denominator or missing output string is behavioral RED.

## Identity and mutation accounting

MEASURED: independently verified envelope SHA256 1a78e1b8712872d4c402e354d38621aa76ca73a1a64c9f6eda1731a51f23100e and all 640 members before diagnostic work. Both recomputed pipeline subject identities matched: semantic 31fe2f7a5c483980ce6cc5877ff73baf6f2b752bd6a660a8a92bf6e1c6e226b3; raw 3aa300bc3cbffba51794dd3e1e8bd6f71f94ca9d0be4a09b79a288df7f3a4265. Source commit is 95e51ad67f42c39c3f00e04c43975fdafa246368; actual final HEAD is 54097a19f83f9448da7c8019a5712f876fa83772, reflecting root's separate dispatch bookkeeping.

MEASURED: final packet audit rehashed 640 members, 640 unchanged and 0 differences. Complete member rows and any mutation inventory are in input-audit-before.json and input-audit-after.json. All writes were private under this output directory; root retained sole live ownership.

MEASURED: before extracting, verified archive 94bde46519fbe62185e729a769f5e2ee8e9fc2410bdade7c0bc54633c1cd7f03, exact 164903 bytes, and all 56 distinct regular members against witness-attempt-manifest.json, rejecting links/traversal. Only private extraction was used. Final extracted-member rehash found 0 differences; full rows are in archive-audit-after.json. Original private directories were not modified.

## Exact failed commands

All three commands used /usr/bin/python3, had 60-second timeouts, completed without timeout and were reaped. Full actual argv, start/end, PID, return code, duration, checker SHA before/after, separate complete stdout/stderr are retained under the numbered stems. Every run retained checker cb0d0cf6cb593b5f231fa372920e7dc6adf10bce95c0d734fac0900d3fd3ddf3 before and after.

1. 001_archived_native_census: PID 2041888; start 21:34:29.451595Z; end 21:34:29.667790Z; rc 1; 0.214694160 seconds. PAD.GetNetClass does not exist. Exact script retained as census-attempt-001.py.
2. 002_archived_native_census: PID 2043783; start 21:35:08.177468Z; end 21:35:08.393758Z; rc 1; 0.214747764 seconds. PAD.GetEffectiveNetClass returned SwigPyObject without GetName. Exact script retained as census-attempt-002.py.
3. 003_archived_native_census: PID 2045624; start 21:35:46.490293Z; end 21:35:46.706261Z; rc 1; 0.214480403 seconds. NETINFO_ITEM.GetNetClassSlow advanced farther, but NETCLASS.GetConstituentNetclasses returned a noniterable SwigPyObject. Exact script retained as census-attempt-003.py and census.py.

These are three consecutive nonimproving diagnostic attempts and exhaust this commission. Their total captured runtime is 0.643922327 seconds. No replacement, fourth correction, extension, public checker invocation, new fixture, native DRC, board sweep or old-suite rerun occurred. Bootstrap read commands were not instrumented with child PID/full timing; bootstrap-reads.md discloses that gap rather than fabricating metadata. One bootstrap rg lookup used the nonexistent generate_rules.py basename and was corrected by a filename search to generate_rules_generic.py; it was a read lookup error, not behavioral evidence.

## Exact inherited fixture failure and what remains unmeasured

MEASURED by reading verified saved files: all three archived PRO files define Low clearance 0.1 mm and High clearance 0.25 mm with board minimum 0.1 mm, but netclass_patterns is empty and no persisted assignments are present. The builder's temporary SetNetClass calls cannot substitute for saved project assignment evidence. The rejected unexecuted WIP adds patterns but supplies only top-level meta.version; the maintained generator separately writes net_settings.meta.version = 4. Whether that WIP would reload as intended was not tested here.

MEASURED by reading original checker source: read_dru_rules marks A.Type == 'Track' unparsed; resolve_min only accepts supported class or area conditions, with exact string equality for the class form. buor9qaj and mvyf2gld use that A.Type condition. c6rfmpgs uses A.NetClass == 'Low'. Saved geometry is the author's central U1.1 ADC rectangle 0.2 by 0.8 mm at (10,10), SIB J1.1/J2.1 at x=9.6/10.4, and REMOTE J3.1 at x=12, all y=10. These are source/artifact facts, not a completed independent native census.

INHERITED exact captured execution: 004 was the full old suite rc 1 / 52.357778 seconds and produced zero graded / four floorless on its added fixtures; 005 was targeted rc 1 / 0.414639 seconds with zero graded / four floorless. Both report zero failing graded pads and fail admission for the zero denominator. 004's unsupported condition prevents declared-floor application regardless of geometry; 005's expected Low match is not established by its saved project assignments. Full reloaded class/floor proof remains absent. The unexecuted 73-line WIP's RED-VERIFIED claim remains rejected.

Original hostile geometry also has a potential confound: 0.2-wide pads at 0.4 pitch have 0.2 mm pad-to-pad gap, below High's 0.25 mm clearance. This arithmetic is an inference from the saved dimensions, not a native DRC result. A future native control must preserve and classify any such static violations rather than call them track-only failure.

Unresolved required rows:

- Complete native reloaded census of all three fixtures: pad/net identity, effective classes and relevant compound semantics, floors, layers and effective polygons. The attempted records were buffered and never serialized; no measured census is claimed.
- One private clean/hostile diagnostic pair, predeclared geometry/classes/floors, verified after save/reload before public CLI. No pair was built.
- Causal unchanged public CLI failure of a named central pad with a nonzero denominator. No new public CLI was run, so no behavioral RED exists.
- Independent explicit 0.2 mm connected native track positive and nearest-High hostile control, all DRC categories, baseline pad-pair findings and connectivity. No native DRC ran. Schematic parity cannot be inferred from a specimen without schematic.
- Maintained regression admission, final witness admission, production GREEN and full suites. None is established.

## Upstream interface decision and ownership

SOURCE-LEVEL DECISION: the census was overimplemented by this agent. The task asks for compound-class detail where relevant; it did not require unconditional enumeration of an unbound C++ container. Each attempted script already called the maintained escape_check.read_board(path), which uses installed PAD.GetNetClassName and effective polygons, before failing on optional additional introspection. The required basic records were available in memory but not serialized before the optional work. This is a diagnostic dependency and observability failure, not proof those buffered values were correct. A future design should persist basic pad/name/layer/polygon records first, then isolate optional effective-class introspection behind an explicitly supported binding contract. It must distinguish a native display class string from native constituent-membership semantics when composition is actually relevant. No fourth execution is authorized by this simplification.

PROPOSED admission contract, not executed: first assert exact saved/reloaded fixture identity and a nonzero graded denominator with named U1.1 floor, layer and native land; next prove the old CLI fails U1.1 specifically because its blanket clearance incorporates a remote High obstacle; separately require a genuine native specified-track positive and nearest-High negative with all categories/connectivity disclosed. A positive native specified track is a geometric oracle, not itself a whole-public-search RED. Final implementation tests must then assert VALIDATED_CONSTANT_WIDTH_WITNESS / NO_VALIDATED_WITNESS behavior with actual start/end/width/layer/floor and limiting pair/rule/gap/margin, independent of any missing-string failure against old output. The current maximum-width claim must be migrated truthfully.

OWNERSHIP/COST DECISION: reject another identical full author commission or any reset of either exhausted implementation cap. Preserve the fixed-point author's initial focused failure plus two terminated attempts, and the latest author's sampling edit plus two floorless fixture attempts. This additional failed diagnosis also retains its own exhausted cap. These binding failures alone do not justify a higher model-cost ceiling: the narrower upstream interface contract and staged output durability are the immediate owner. The original production repair still requires reviewed decomposition into (1) native persistence/admission fixture contract, (2) compiled rule semantics and native candidate validation, and (3) public verdict/denominator and maintained hostile-corpus migration. Each requires its own concrete acceptance boundary and explicit coordinator authorization; no work is commissioned by this report. An above-standard role, if later chosen, needs a specific semantic/native-integration reason rather than a promise that repetition will succeed.

Accepted upstream direction remains finite declared-width witnesses; a complete compiled AST; both A/B orderings with per-constraint last-match semantics; native candidate shape validation; truthful failure when no validated witness exists. Preserve MAX_LAUNCH_PTS = 25 (37 actual points on the sufficiently large rectangular case), 48 directions, 1 mm reach and 2 mm cap. No design width-floor or source-copper relaxation is authorized.

All seven production guard groups remain owed: native support/unreadable geometry; all effective/local clearance bounds; B-dependent width AST prevalidation; complete supported attributes/constraints; native class/string/wildcard semantics; absolute board minima/local-custom precedence; and full public verdict/denominator migration with retained hostile corpus. INHERITED from root's independent source inspection: native pad/footprint local-clearance precedence and custom-rule/board-minimum early-return behavior require careful native validation or fail-closed handling. This agent did not independently probe that behavior.

INHERITED project baseline remains 0 physical findings / 514 complete connection gaps / 0 parity, not remeasured here. Existing schematic, source copper, models, routes, checkpoints, reviews and releases remain unchanged; stale checkpoints and all physical/order holds stay open. No electrical progress credit.

## Closure

MEASURED process audit: all three captured child PIDs absent = True; matching remaining diagnostic processes = 0. Exact /proc observations and excluded administrative ancestors are in process-audit.json. The administrative audit process exits after writing this report and manifests; no diagnostic process remains to terminate.

output-manifest.json lists SHA256 and byte size of every retained output, including this actual result.md, complete failed-command records, all script versions, audit files and all extracted evidence. It excludes only itself and its detached hash receipt to avoid self-reference; output-manifest.sha256 authenticates the manifest. No files are promoted to the live repository. All writes cease after this closure command returns. This is a complete administrative INCOMPLETE handback, not a passing technical witness.
