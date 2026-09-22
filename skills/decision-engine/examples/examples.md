# Examples

## Noul

Question: Should this candidate pass the gate?

Use `noul` when the proposition is binary under declared criteria. Return `undetermined` rather than forcing `true/false` if required evidence is missing.

## Choice

Question: Which route should run: `answer`, `search`, or `escalate`?

Use `choice`. The selected value must be one of the explicit options.

## Score

Question: Rate regression risk from 1 to 4, where 1 is low and 4 is critical.

Use `score` with the explicit scale and keep the result within bounds.

## Calibration

Do not emit a self-invented `0.93`. Numeric probability is allowed only when an identified calibrated source and calibration reference are available.
