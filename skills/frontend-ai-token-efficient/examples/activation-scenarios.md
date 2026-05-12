# Activation scenarios

Use these scenarios to calibrate when to apply the skill.

## Should activate

- "what React structure helps AI use fewer tokens?"
- "review this frontend so AI agents can maintain it more safely"
- "create an AI_CONTEXT.md for my React project"
- "Vite or Next.js for an onboarding backoffice?"
- "how do I prevent token leaks in the frontend?"
- "evaluate whether this feature should move to shared or stay duplicated"
- "generate a frontend PR checklist for AI-assisted coding"
- "review this account-opening form to reduce friction while keeping compliance"
- "create an AGENTS.md to separate frontend implementation, browser QA, and accessibility checks"
- "how should I validate this modal in Playwright?"

## Should not activate

- "fix this C# endpoint"
- "create a new skill"
- "make a visual layout in Figma"
- "configure CloudFront Terraform"
- "explain React from scratch without focus on architecture, AI, or maintenance"
- "create a complete brand identity and logo without code"

## Ambiguous

- "improve my project" -> ask or infer whether it is a React frontend and whether the focus is architecture, maintenance, security, UX implementation, or AI assistance.
- "create a screen" -> use only if there is frontend implementation scope; if it is pure visual design, do not activate.
- "review security" -> use if the target is frontend; if it is infrastructure, backend, or cloud, route to the appropriate review.
- "make this page prettier" -> if code/project context exists, apply existing visual system and implementation quality; if the task is visual-only design, do not activate.
