#!/usr/bin/env python3
from pathlib import Path
import re
import sys

REQUIRED_REFERENCES = [
    '01-engineering-principles.md',
    '02-solution-architecture.md',
    '03-dotnet-10-baseline.md',
    '04-csharp-14-type-modeling.md',
    '05-async-tasks-cancellation.md',
    '06-error-handling-result-exceptions.md',
    '07-dependency-injection-lifetimes.md',
    '08-configuration-options-secrets-flags.md',
    '09-ef-core-10-persistence.md',
    '10-transactions-concurrency-consistency.md',
    '11-aspnet-core-10-api-design.md',
    '12-minimal-apis-net10.md',
    '13-serialization-contract-versioning.md',
    '14-logging-observability-pii.md',
    '15-security-auth-secrets-sensitive-data.md',
    '16-audit-compliance-traceability.md',
    '17-threat-modeling-security-review.md',
    '18-supply-chain-dependencies-cicd-scripts.md',
    '19-dotnet-10-performance.md',
    '20-caching.md',
    '21-resilience-timeout-retry-circuitbreaker-ratelimit.md',
    '22-abstractions-design-overengineering.md',
    '23-cqrs-mediator-ddd.md',
    '24-events-outbox-idempotency.md',
    '25-messaging-workers-background-services.md',
    '26-testing-modern-tooling.md',
    '27-build-analyzers-cicd-quality.md',
    '28-deployment-containers-healthchecks-shutdown.md',
    '29-aot-trimming-reflection-source-generators.md',
    '30-time-dates-clock-timezone.md',
    '31-technical-docs-adrs-runbooks.md',
    '32-agent-skill-governance.md',
    '33-modern-antipatterns.md',
    '34-production-readiness-checklist.md',
    '35-decision-matrix.md',
]

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    errors = []
    skill = root / 'SKILL.md'
    if not skill.exists():
        errors.append('missing SKILL.md')
    else:
        text = skill.read_text(encoding='utf-8')
        if 'TODO' in text or 'placeholder' in text.lower():
            errors.append('SKILL.md contains TODO or placeholder text')
        if not re.search(r'^---\nname: modern-dotnet-engineering\ndescription: [a-z0-9]', text):
            errors.append('SKILL.md frontmatter is missing expected lowercase name/description')
        for ref in REQUIRED_REFERENCES:
            if f'references/{ref}' not in text:
                errors.append(f'SKILL.md does not reference {ref}')
    for ref in REQUIRED_REFERENCES:
        path = root / 'references' / ref
        if not path.exists():
            errors.append(f'missing reference {ref}')
        elif len(path.read_text(encoding='utf-8').strip()) < 120:
            errors.append(f'reference too small: {ref}')
    for rel in ['scripts/example.py', 'references/api_reference.md', 'assets/example_asset.txt']:
        if (root / rel).exists():
            errors.append(f'generated placeholder still exists: {rel}')
    if not (root / 'agents' / 'openai.yaml').exists():
        errors.append('missing agents/openai.yaml')
    if errors:
        for e in errors:
            print(f'[FAIL] {e}')
        return 1
    print('[OK] modern-dotnet-engineering content validation passed')
    print(f'[OK] references: {len(REQUIRED_REFERENCES)}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
