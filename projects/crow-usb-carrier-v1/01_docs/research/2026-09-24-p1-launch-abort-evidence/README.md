# Crow P1 launch-abort historical receipt

`attempt.json` and `envelope.json` are verbatim, tracked historical copies of
the terminal run records. They preserve the original byte content and make the
consumed-attempt evidence available from a fresh checkout; they do not
reclassify, replace, or alter either original runtime record.

Original local provenance:

* `06_build/task_runs/crow-45-569-p1-one-attempt-terra-a7b5e6b970ce440e862f123b2a2d214f/attempt.json` — SHA-256 `382f8798074233eef808f79fc868f155fa31972fde956c23cd6f645b6af99314`
* `06_build/task_runs/crow-45-569-p1-one-attempt-terra-a7b5e6b970ce440e862f123b2a2d214f/envelope.json` — SHA-256 `01f5d608494cfd4c596c3fecbb422bc2bfa5199d225e994293d8edacc9c6b6d2`

The attempt binds envelope digest
`f004b21dce254ef29e7550b5e4f5805b9e95f50a33967e876971e78a00e42cd9`.
Its recorded terminal facts are `FAIL`, return code `-15` (`SIGTERM`), no
completion or outputs, and unchanged read-only writer scope. `SHA256SUMS`
authenticates these tracked copies.
