#!/usr/bin/env python3
from pathlib import Path
import re
import sys

REQUIRED_REFERENCES = [f"{i:02d}-" for i in range(1, 38)]
REFERENCE_FILES = [
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
    '36-review-evidence-and-reproducibility.md',
    '37-dotnet-ai-agents-mcp.md',
]

# These markers make the research integration mechanically regression-testable.
# Each tuple is: relative path -> material knowledge that must remain present.
REQUIRED_KNOWLEDGE_MARKERS = {
    'SKILL.md': [
        'current servicing patch',
        'modular single deployable',
        'references/37-dotnet-ai-agents-mcp.md',
    ],
    'references/02-solution-architecture.md': [
        'Distributed-systems cost checklist',
        'well-modularized single deployable',
    ],
    'references/03-dotnet-10-baseline.md': [
        '2026-11-10',
        'self-contained and container deployments own rebuild/redeploy cadence',
        'Prerelease policy',
    ],
    'references/04-csharp-14-type-modeling.md': [
        'C# 14 adoption table',
        'Do not imply that Span usage or source generation is automatically superior',
    ],
    'references/09-ef-core-10-persistence.md': [
        'not authorization',
        'deployment-controlled',
        'concurrency',
    ],
    'references/11-aspnet-core-10-api-design.md': [
        'OpenAPI 3.1',
        'resource-based authorization',
        'unbounded resource consumption',
    ],
    'references/12-minimal-apis-net10.md': [
        'AddValidation',
        'assembly where',
    ],
    'references/14-logging-observability-pii.md': [
        'authentication, authorization, and Identity metrics',
        'Cardinality and privacy gate',
    ],
    'references/15-security-auth-secrets-sensitive-data.md': [
        'BOLA/IDOR',
        'Resource-consumption',
    ],
    'references/18-supply-chain-dependencies-cicd-scripts.md': [
        'NuGetAuditMode',
        'NU1901-NU1904',
        'CentralPackageTransitivePinningEnabled',
    ],
    'references/21-resilience-timeout-retry-circuitbreaker-ratelimit.md': [
        'PooledConnectionLifetime',
        'Microsoft.Extensions.Http.Resilience',
        'Retry-safety gate',
    ],
    'references/25-messaging-workers-background-services.md': [
        'bounded `Channel<T>`',
        'backpressure',
    ],
    'references/26-testing-modern-tooling.md': [
        'Microsoft.Testing.Platform',
        'Zero/expected-test-count gate',
        'FakeTimeProvider',
    ],
    'references/28-deployment-containers-healthchecks-shutdown.md': [
        'Aspire is an optional',
        'ServiceDefaults',
        'rebuild/redeploy',
    ],
    'references/29-aot-trimming-reflection-source-generators.md': [
        'MVC is not supported',
        'OData is not supported',
        'AOT/trimming validation gate',
    ],
    'references/37-dotnet-ai-agents-mcp.md': [
        'IChatClient',
        'IEmbeddingGenerator',
        'Prompt instructions are guidance to the model, not an authorization boundary',
    ],
}


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    root = root.resolve()
    errors: list[str] = []
    skill = root / 'SKILL.md'
    if not skill.exists():
        errors.append('missing SKILL.md')
    else:
        text = skill.read_text(encoding='utf-8')
        unfinished_marker = 'TO' + 'DO'
        if unfinished_marker in text or 'placeholder' in text.lower():
            errors.append('SKILL.md contains unfinished or placeholder text')
        if not re.search(r'^---\nname: modern-dotnet-engineering\ndescription: [a-z0-9]', text):
            errors.append('SKILL.md frontmatter is missing expected lowercase name/description')
        for ref in REFERENCE_FILES:
            if f'references/{ref}' not in text:
                errors.append(f'SKILL.md does not reference {ref}')

    for index, ref in enumerate(REFERENCE_FILES, start=1):
        if not ref.startswith(f'{index:02d}-'):
            errors.append(f'reference sequence mismatch at {index}: {ref}')
        path = root / 'references' / ref
        if not path.exists():
            errors.append(f'missing reference {ref}')
        elif len(path.read_text(encoding='utf-8').strip()) < 120:
            errors.append(f'reference too small: {ref}')

    for rel, markers in REQUIRED_KNOWLEDGE_MARKERS.items():
        path = root / rel
        if not path.exists():
            errors.append(f'missing knowledge-owner file: {rel}')
            continue
        text = path.read_text(encoding='utf-8')
        for marker in markers:
            if marker not in text:
                errors.append(f'missing research knowledge marker in {rel}: {marker}')

    generated_examples = [
        Path('scripts') / ('example' + '.py'),
        Path('references') / ('api_' + 'reference.md'),
        Path('assets') / ('example_' + 'asset.txt'),
    ]
    for rel in generated_examples:
        if (root / rel).exists():
            errors.append(f'generated scaffold file still exists: {rel.as_posix()}')

    if not (root / 'agents' / 'openai.yaml').exists():
        errors.append('missing agents/openai.yaml')

    if errors:
        for error in errors:
            print(f'[FAIL] {error}')
        return 1
    print('[OK] modern-dotnet-engineering content validation passed')
    print(f'[OK] references: {len(REFERENCE_FILES)}')
    print(f'[OK] research knowledge owners: {len(REQUIRED_KNOWLEDGE_MARKERS)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
