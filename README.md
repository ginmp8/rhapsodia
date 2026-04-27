# Rhapsody of Skills

A curated collection of agent skills, evaluation harnesses, benchmarks, and
delivery workflows.

---

## Repository layout

```
rhapsody-of-skills/
├── skills/          # Reusable agent skill implementations
├── evals/           # Evaluation harnesses and metrics
├── benchmarks/      # Benchmark suites and a runner
│   └── tasks/       # Pre-built benchmark task definitions
├── workflows/       # Delivery workflows (skill pipelines)
└── tests/           # Unit tests
```

---

## Skills

Skills are the atomic building blocks.  Every skill extends `skills.base.Skill`
and exposes a single `run(input) -> SkillResult` method.

| Skill | Class | Description |
|---|---|---|
| echo | `EchoSkill` | Returns its input unchanged – useful as a baseline |
| search | `SearchSkill` | Web search (mock by default, subclass to wire a real API) |
| summarize | `SummarizeSkill` | Extracts the first *N* sentences from a text block |

### Writing a new skill

```python
from skills.base import Skill, SkillResult

class MySkill(Skill):
    name = "my-skill"
    description = "Does something useful."

    def run(self, input, **kwargs):
        result = do_something(input)
        return SkillResult(output=result, metadata={"skill": self.name})
```

---

## Evaluation harnesses

`evals.harness.EvalHarness` evaluates any skill against a list of
`EvalCase` objects and returns an `EvalReport`.

```python
from skills.echo import EchoSkill
from evals.harness import EvalCase, EvalHarness
from evals.metrics import accuracy

cases = [
    EvalCase(id="c1", input="hello", expected="hello"),
    EvalCase(id="c2", input="world", expected="world"),
]

harness = EvalHarness(skill=EchoSkill(), cases=cases, metric=accuracy)
report = harness.run()
print(report)  # EvalReport(skill='echo', score=1.0000, cases=2)
```

### Available metrics

| Function | Description |
|---|---|
| `accuracy` | Exact-match accuracy (1.0 or 0.0) |
| `f1_score` | Token-level F1 between two strings |
| `rouge_l` | ROUGE-L based on longest common subsequence |

---

## Benchmarks

A `BenchmarkSuite` groups evaluation cases under a named benchmark.
`BenchmarkRunner` runs one or more skills across a suite collection.

```python
from benchmarks.runner import BenchmarkSuite, BenchmarkRunner
from benchmarks.tasks.qa import QA_TASKS
from evals.metrics import accuracy
from skills.echo import EchoSkill

suite = BenchmarkSuite(name="qa-smoke", cases=QA_TASKS, metric=accuracy)
runner = BenchmarkRunner(suites=[suite])
for result in runner.run(EchoSkill()):
    print(result)
```

---

## Delivery workflows

`workflows.pipeline.SkillPipeline` chains skills so the output of each step
becomes the input of the next.

```python
from skills.search import SearchSkill
from skills.summarize import SummarizeSkill
from workflows.pipeline import SkillPipeline

pipeline = SkillPipeline(skills=[SearchSkill(), SummarizeSkill(max_sentences=2)])
result = pipeline.run("latest advances in quantum computing")
print(result.output)
```

---

## Getting started

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run the full test suite
pytest
```
