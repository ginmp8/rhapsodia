# Evidence and Claim Contract

Label validation evidence accurately:

- `measured`: an actual command, scenario executor, model run, or evaluator was executed;
- `observed`: direct inspection of prompt/source/output;
- `derived`: deterministic calculation from measured/observed evidence;
- `supplied`: result provided by the user or another system but not independently run here;
- `planned`: scenario or validator exists but was not executed;
- `blocked`: required evidence could not be obtained.

A manual "literal simulation" is `observed` or `planned`, not `measured runtime behavior`. Keep **structural evidence**, **behavioral evidence**, and **runtime evidence** separate; perceptual/editorial evidence is a fourth layer when subjective review is material.

Use these claim boundaries:

- **structurally hardened**: contracts/rules/checks improved and applicable deterministic gates pass;
- **validation-ready**: evaluation assets exist but were not executed;
- **behaviorally improved**: baseline and candidate were actually compared with a frozen evaluator and predeclared acceptance rule;
- **runtime validated**: the intended executor/tools actually ran successfully.

Do not upgrade one evidence layer into another.
