# Content type contracts

Use this reference when a document's purpose materially changes what "good" means. Content kind is independent from review mode: a README review can contain a quickstart, a reference section, or mixed content.

## Selection rules

Choose the narrowest useful `content_kind`:

| Kind | Reader need | Primary obligation | Common failure |
|---|---|---|---|
| `tutorial` | learn by doing | provide a successful learning path with concrete steps and expected checkpoints | overloading the path with explanation or assuming expertise |
| `how-to` | accomplish a goal | guide a competent reader to a specific result safely and directly | teaching generic background instead of solving the task |
| `reference` | look up facts/contracts | be accurate, complete for scope, structured, and low-interpretation | mixing opinion/procedure into lookup material or omitting contract detail |
| `explanation` | understand why/how | build context, relationships, trade-offs, and mental models | turning explanation into a step-by-step procedure |
| `quickstart` | get a focused result fast | state audience/prerequisites/outcome and keep only essential steps | becoming a full tutorial or reference dump |
| `troubleshooting` | diagnose/recover | connect symptom -> likely cause -> recovery -> verification, or state no known workaround | listing errors without a recovery path or inventing a fix |
| `mixed` | several explicit needs | keep transitions and section purposes clear | blending purposes inside the same section until none is clear |
| `unspecified` | purpose not material/clear | apply the normal rubric without inventing a classification | forcing a taxonomy choice without evidence |

Use these as review obligations, not rigid publishing templates. Do not restructure merely to make a document look taxonomically pure.

## Procedural content

For `tutorial`, `how-to`, `quickstart`, and procedural sections inside mixed documents, check:

- prerequisites appear before the action that depends on them;
- steps are ordered and actionable;
- expected checkpoints are present where failure is plausible;
- common failures are near the relevant procedure when that improves recovery;
- next steps are included only when they help continue the reader's task.

Tutorials may be more explicit about basic actions; how-to guides may assume domain competence. Quickstarts should omit nonessential explanation and link to deeper material instead of reproducing it.

## Reference content

Check that reference structure mirrors the described contract or system when that helps lookup. Separate factual contract description from recommendations, rationale, or tutorials. Completeness is scoped to the declared surface; do not claim universal completeness without evidence.

## Explanation content

Check that explanation answers why/how, connects concepts, and preserves relevant alternatives or trade-offs. It may contain perspective, but factual claims still require source fidelity.

## Troubleshooting content

Prefer this shape when evidence supports it:

```text
symptom
likely cause or diagnostic condition
recovery/workaround
verification after recovery
known limitation or no-known-workaround state
```

Do not invent a root cause or workaround merely to complete the shape.

## Mixed-content rule

A mixed document is acceptable when distinct reader needs are intentionally grouped. Review each section against its local purpose and verify that navigation makes the transitions obvious. Do not split content solely for taxonomy purity when doing so would worsen discoverability or maintenance.
