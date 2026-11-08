---
name: grilling
description: "Interview a user to stress-test a decision, design, project or plan through dependency-aware questions and explicit recommendations. Use for deliberate grilling and ambiguous decision discovery; not for routine factual answers, audits, or autonomous implementation."
---

# Grilling

## Purpose and boundary

Lead a bounded, interactive decision interview. Discover assumptions, contradictory requirements, dependencies and trade-offs without silently choosing on the user's behalf. This skill owns **elicitation**, not the canonical technical specification (Mago), delivery governance (Nomia), implementation (Magia), or final formal decision policy (Decision Engine).

## Modes

- **Focused** (default): one central decision, up to three rounds of two to five questions.
- **Deep**: a user-requested extended interrogation; agree a finite round budget before continuing.
- **Review**: revisit previously settled answers when new evidence materially changes prerequisites.

## Workflow

1. State the goal, known decisions, missing facts and scope boundary in one short paragraph. Read available evidence before asking questions.
2. Build a small decision tree. Put only questions with resolved prerequisites on the current **frontier**; defer dependent questions.
3. For each question give a specific **recommended answer**, a short reason and relevant trade-off. Phrase the choice so **"yes" means accept the recommendation**, never the opposite. Make alternatives explicit where useful.
4. Ask no more than five frontier questions in one round. Wait for the user to answer; do not answer on their behalf. The user may correct, reject or defer recommendations.
5. Recompute the frontier after each response. Investigate facts using available approved tools; request a user decision only for genuine preferences, constraints or authority.
6. At the agreed round limit, summarize confirmed decisions, unanswered questions, evidence gaps and downstream implications. Ask whether to conclude or extend only if material decisions remain.
7. Close when the frontier is empty or the user explicitly ends the interview. Do not implement or publish decisions unless separately authorized.

## Interview format

For each question use **Q1 — [decision title]**, the question, then **Recommended: [answer] — [reason]**. Keep question numbering stable within a round and link references to their source when available.

## Invariants

- Facts and assumptions are separate. Never invent environmental facts or claim tool/delegation execution that did not occur.
- Recommend, challenge and explain without coercion, false dilemmas or infinite questioning.
- Respect existing requirements and approved choices until the user revises them. State when a new answer conflicts with an earlier one.
- Use a fresh context for independent fact-finding only when the host supports real delegation; otherwise investigate sequentially and report that limitation.
- Use **domain-modeling** when terminology or aggregates are disputed; **grill-with-docs** when the user wants a documented result; **wayfinder** when work spans sessions; **premortem-analysis** for a concrete plan's prospective failures.
- A Grilling recommendation cannot approve risk, alter deadlines, create GitHub issues or grant write authority.

## Host portability

Interview questions require only a conversation. Network access, named-skill invocation, filesystem access and subagents are optional capabilities. When fact-finding tools are unavailable, use supplied evidence and mark unverified assumptions; when delegation is unavailable, investigate sequentially without claiming an independent agent ran.

## Output contract and stop conditions

During each round show numbered decision-ready questions and a recommended answer with rationale. Finish with approved choices, explicit unknowns and deferrals. Stop at the agreed round limit, an empty frontier or the user's explicit request; never turn interview recommendations into approvals.
