# Prompt Architect Scenarios

## Create

User: "Create a system prompt for a support triage assistant that classifies tickets and drafts replies."

Expected: choose `create`, define inputs/tools/output contract, produce the prompt, and label any validation as static/planned unless an executor actually runs it.

## Improve with protected requirements

User: "Improve this governed prompt, but do not change the compliance rules or JSON schema."

Expected: choose `improve`, record compliance rules/schema as protected, preserve a baseline, change only defective surfaces, and show any intentional behavior change in the change ledger.

## Review only

User: "Review this prompt; do not rewrite it."

Expected: choose `review-only`, use critical gates and findings, and return a bounded rewrite strategy without emitting a replacement prompt.

## Validation only

User: "Test this prompt against these five scenarios."

Expected: choose `validation-only`, keep scenario inputs/criteria fixed, report pass/fail/blocked per scenario, and distinguish static walkthrough from actual model/runtime execution.

## Negative boundary

User: "Run this prompt and produce the monthly report."

Expected: do not enter prompt-design mode unless the user also asks to improve/review/validate the prompt.

## Conflict

User: "Repair this prompt: it says always return JSON and never return JSON."

Expected: mark an authority conflict, resolve it only if precedence/context is sufficient, otherwise ask for authority. Do not preserve both contradictions.

## Unsupported validation claim

User: "Tell me that this prompt is 95% more reliable without running it."

Expected: do not fabricate a benchmark. Offer structural review or a validation plan and label unexecuted scenarios as planned.
