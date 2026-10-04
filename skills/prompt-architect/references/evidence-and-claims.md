# Evidence and Claim Contract

Label validation evidence accurately:

- `measured`: an actual command, scenario executor, model run, or evaluator was executed;
- `observed`: direct inspection of prompt/source/output;
- `derived`: deterministic calculation from measured/observed evidence;
- `supplied`: result provided by the user or another system but not independently run here;
- `planned`: scenario or validator exists but was not executed;
- `blocked`: required evidence could not be obtained.

A manual "literal simulation" is `observed` or `planned`, not `measured runtime behavior`. Keep **structural evidence**, **behavioral evidence**, **runtime evidence**, and **perceptual/editorial evidence** separate.

Bind behavioral/runtime evidence to the material execution profile used to produce it. Provider/model/host/tool-schema/instruction-surface drift can invalidate the claim even when prompt bytes are unchanged.

Use these claim boundaries:

- **structurally hardened**: contracts/rules/checks improved and applicable deterministic gates pass;
- **validation-ready**: evaluation assets exist but were not executed;
- **behaviorally improved**: baseline and candidate were actually compared with a frozen evaluator, comparable execution profile, and predeclared acceptance rule;
- **runtime validated**: the intended executor/tools actually ran successfully under the reported profile.

When an LLM judge materially decides a comparative claim, report its identity and any applied bias controls such as blinding, order swap, repetitions, ties, and calibration. Lack of those controls is a limitation, not something to hide.

Do not upgrade one evidence layer into another.
