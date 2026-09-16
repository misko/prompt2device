# Native-interface admission result (corrected administrative report)

Status: FAILED at producer launch; execution stopped as required. The frozen producer was launched exactly once; no retry, repair, alternative API, fixture, source, or live project write occurred. The initial report is preserved as `result.initial.md`.

Bootstrap record: the administrative setup created `/tmp/pland-native-interface-20260910T215034Z/run` with `mkdir(parents=True)` before launch. The exact command then launched at `2026-09-10T21:51:44.418538+00:00` was `/usr/bin/python3 /tmp/pland-native-interface-20260910T215034Z/producer/execute.py /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901 /tmp/pland-native-interface-20260910T215034Z/run`.

## Verification

- Task envelope SHA-256: `6bbd771f65c528c0cbe081eaaa47eec7f715cabd0aba03540d71189651570fb3`, verified.
- Input packet: 647/647 members verified for exact path, size, and SHA-256; audit: `packet-audit.json`.
- Producer archive SHA-256: `06cf4fbec59d3357a39319af0d62b7a0635e8915e5dde27184b0601660b2aaa2`; size 4909 bytes, verified against manifest.
- Extracted regular members: `census.py` 2252 bytes SHA `3a470c0418e76bc7741865e45f51bba603d62eb234b69ac61b24e5b46aa2e6d4`; `execute.py` 5559 bytes SHA `ffa5736c0bd08ed783274f9dc23f539a9f3c3034ac15145207575d7b43650bbc`; `fixture.py` 4858 bytes SHA `de165a7c7035e48e69ba43f4f0a4ccfc6115af5e5c054124011599c8b283f162`.

## Single command outcome

```text
argv: /usr/bin/python3 /tmp/pland-native-interface-20260910T215034Z/producer/execute.py /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901 /tmp/pland-native-interface-20260910T215034Z/run
start: 2026-09-10T21:51:44.418538+00:00
pid: 2087572
duration_seconds: 0.0568261609878391
timeout_seconds: 420
timed_out: false
rc: 1
end: 2026-09-10T21:51:44.475375+00:00
```

Full stdout is empty (`command.stdout`, SHA `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`). Full stderr is in `command.stderr` (352 bytes, SHA `9b128933e717f3b7649b55cbd4c76f1398bb5b16618e5055dd73ecffd7400a7f`) and reports `FileExistsError` because the producer requires its output directory to be absent and `/tmp/.../run` existed at launch. No producer stages ran; no census, checker, or DRC result exists.

## Closure

The failed launch process exited and no matching producer process remains; final process audit is `process-cessation.json`. Final 647-member input and 3-member producer audits are retained in `packet-audit.json` and the extracted-member rows therein. The complete output SHA/size manifest is `output-manifest.json` (including `command.json`, full stdout/stderr, packet audit, preserved initial report, and all extracted producer members).
