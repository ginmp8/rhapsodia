# Research Foundation and Transfer Limits

## At a Glance
- **Purpose:** Preserve the empirical and epistemological rationale without overstating what research on human cognition proves about code-analysis agents.
- **Load when:** Explaining design choices, revising the workflow, making empirical claims or evaluating whether mechanistic self-explanation is useful.
- **Decision impact:** Requires evidence/interpretation separation, counterevidence, explicit transfer assumptions and no invented efficacy metrics.

## What the research supports

1. **Explanatory-depth illusion.** Rozenblit & Keil (2002), *Cognitive Science*, DOI [10.1207/s15516709cog2605_1](https://doi.org/10.1207/s15516709cog2605_1), report overestimation of explanatory knowledge in a series of experiments. **Design translation (inference):** require mechanics and gap identification, not component-name familiarity.
2. **Self-explanation.** Chi et al. (1989), *Cognitive Science*, DOI [10.1207/s15516709cog1302_1](https://doi.org/10.1207/s15516709cog1302_1), analyze learners' self-generated explanations in physics worked examples; higher-quality explanations relate actions to principles and monitoring. **Transfer limit:** these are learners studying physics, not autonomous code-analysis agents. Do not promise improved correctness.
3. **Developer information seeking.** Ko et al. (2006), *IEEE TSE*, DOI [10.1109/TSE.2006.116](https://doi.org/10.1109/TSE.2006.116), studied developers seeking, relating and collecting information during maintenance. Sillito et al. (2008), DOI [10.1109/TSE.2008.26](https://doi.org/10.1109/TSE.2008.26), cataloged 44 types of questions in programming-change tasks. **Design translation:** question-driven, cross-file exploration rather than exhaustive file summaries.
4. **Reachability.** LaToza & Myers (2010), ICSE, DOI [10.1145/1806799.1806829](https://doi.org/10.1145/1806799.1806829), documented reachability questions across three empirical studies. **Design translation:** distinguish reachable versus observed paths and scope negative claims.
5. **Confirmation bias in testing.** An experiment involving 42 graduate students reported more confirmatory than disconfirmatory functional test cases; it did *not* establish time pressure as the cause. *Empirical Software Engineering* (2019), DOI [10.1007/s10664-018-9668-8](https://doi.org/10.1007/s10664-018-9668-8). **Design translation:** deliberately seek plausible disconfirming paths.
6. **Causal explanation and uncertainty, including contrary evidence.** Fernbach et al. (2013), DOI [10.1177/0956797612464058](https://doi.org/10.1177/0956797612464058), reported reduced political extremity after policy-mechanism explanations. Crawford & Ruscio (2021), DOI [10.1177/0956797620972367](https://doi.org/10.1177/0956797620972367), found no such moderation effect in three preregistered replications, though perceived policy understanding declined. **Do not claim** explanation reliably moderates opinions or increases technical correctness. This skill uses explanation to expose falsifiable gaps, not to promise attitude change.
7. **Provenance vocabulary.** [W3C PROV-O Recommendation (2013)](https://www.w3.org/TR/prov-o/) formalizes entity/activity/agent provenance. The skill's lightweight evidence IDs are *inspired* by provenance thinking; they are **not** PROV-O-compliant RDF.

## Evidence transfer rule

Label three layers separately: **published observation** (study population/task/outcome), **cross-domain design inference** (plausible use in code comprehension), and **actual target evaluation** (requires tests on real repository tasks). The first two never imply the third. Absence of relevant study replication or full-text access limits interpretation; use abstracts only for narrow abstract-supported claims.

The source-to-finding-to-requirement accounting used during this skill's creation is in `research/traceability.json`; this is *creation provenance*, not a dynamic output requirement. Research is corpus-bounded, not exhaustive or a systematic review.
