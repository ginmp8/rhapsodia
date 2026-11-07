# Trace signals

Treat signals as diagnostic hypotheses, never automatic verdicts. Verify against original JSON, source facts and actual rendered output.

| Signal | Evidence to seek |
| --- | --- |
| Deleted/replaced nodes after failure | Lost semantic content or a source-backed correction; check conditions and ownership. |
| Automatic route crosses unrelated node | Test whether initial placement made a legal route impossible before blaming router. |
| Repeated explicit pin conflicts | Placement, route contract, or inaccurate repair recommendation; test repair against original input. |
| Repeated gap/width oscillations | Conflicting constraints or unclear guidance. |
| Renderer source read before first diagram | Instruction discoverability concern only if the detour was necessary, not automatically misuse. |
| First-draft success | Automated acceptance; still audit source accuracy and readability. |
| Pass requires removal of labels | Possible validator overreach; check semantic significance before accepting. |
| One route improves while graph worsens | Local optimization fails whole-diagram outcome; compare all paths and labels. |
| Screenshot fails to capture | Missing visual evidence, not a visual pass. |

Keep unsuitable or rejected rule changes as negative evidence. Maintain one bounded hypothesis, keep failed runs, and stop when additional attempts supply no new causal evidence.

Original source: [trace-signals.md](https://github.com/ginmp8/archify/blob/a4065941f12be7967436261d9934784e381d423c/.agents/skills/archify-tuning/references/trace-signals.md).
