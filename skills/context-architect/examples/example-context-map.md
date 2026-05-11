# Example Context Map

## Context Map for: add a new onboarding status

### Scope classification
- Change type: feature
- Scope confidence: medium - primary status enum and tests were found, but downstream reporting consumers still need inspection
- Repository evidence inspected: `rg "OnboardingStatus|status" src tests`, `src/domain/onboarding_status.cs`, `tests/onboarding_status_tests.cs`

### Primary files
| File | Why it is primary | Expected change |
|---|---|---|
| `src/domain/onboarding_status.cs` | owns status values | update |
| `src/api/onboarding_response.cs` | serializes status externally | inspect/update |

### Secondary files and dependencies
| File | Relationship | Action |
|---|---|---|
| `src/workflows/open_account_handler.cs` | writes status | update |
| `tests/onboarding_status_tests.cs` | nearest status coverage | update |

### Test coverage and validation
| Test or command | Purpose | Confidence |
|---|---|---|
| `dotnet test --filter OnboardingStatus` | validates status transitions | medium |

### Patterns to follow
- `src/domain/account_status.cs` - enum naming and serialization pattern

### Ripple effects and risks
| Risk | Evidence | Mitigation |
|---|---|---|
| external clients may not handle new status | response DTO exposes status | check client contract tests or add compatibility note |

### Suggested sequence
1. Update domain status and transition logic.
2. Update serialization and API response tests.
3. Run targeted status tests and inspect downstream clients.

### Open questions or blockers
- Are external clients required to tolerate unknown statuses?
