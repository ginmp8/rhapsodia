# Prompt Architect Scenarios

## Create Mode

User asks: "Create a prompt for a data-quality assistant that reviews CSV uploads."

Expected behavior: define the assistant task, required inputs, validation workflow, output format, examples, and stop conditions. Include a concise validation note unless the user asks for prompt-only output.

## Improve Mode

User provides a prompt and asks: "Make this less ambiguous and add examples."

Expected behavior: audit the prompt, preserve the user's requirements, rewrite only defective sections, add representative examples, and validate with a Prompt Tester scenario.

## Review-Only Mode

User asks: "Score this prompt and do not rewrite it."

Expected behavior: produce a verdict, scorecard, critical issues, and prioritized rewrite strategy without outputting a new prompt.

## Negative Boundary

User asks: "Run this prompt and produce the report."

Expected behavior: treat the request as task execution, not prompt engineering, unless the user also asks to improve, validate, or package the prompt.
