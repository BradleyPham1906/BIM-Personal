# Cline outcome record

Use this record to calibrate Cline's current model, not to rank tools by task or PR volume. Add one
row per audited Cline task. Keep Aider, Claude, and other model results separate.

“First gate” is the first `tools/gate.py check` for the task's initial complete implementation.
“Retries” counts subsequent gate-and-fix attempts before shipping. “Audit changes” counts behavior
or code changes made after shipping, not documentation-only annotations. If the history is unknown,
write `unknown`; do not infer it from the final green gate.

| Date | Model | Task | Route tier | First gate | Retries | Audit changes | Reopened or reverted |
|---|---|---|---|---|---:|---:|---|
