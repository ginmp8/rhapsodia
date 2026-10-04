# Example Context Map

## Context Map for: add a new onboarding status

### Evidence identity
- Contract: context-map/2.1
- Repository: `/repo/onboarding`
- Revision/worktree: `abc1234`, clean
- Change anchor: supplied feature request; no base/head diff
- Evidence freshness: observed

### Scope classification
- Change type: feature
- Evidence tier: standard
- Scope confidence: medium - owner, direct writer, response DTO, build/runtime wiring, and nearest tests were inspected; downstream reporting consumers remain unresolved
- Repository evidence inspected: semantic references for `OnboardingStatus`; exact searches for serialized value; project references; `src/domain/onboarding_status.cs`, `src/api/onboarding_response.cs`, `src/workflows/open_account_handler.cs`, `tests/onboarding_status_tests.cs`

### Primary files / owners
| File | Evidence | Source class | Why primary | Expected action |
|---|---|---|---|---|
| `src/domain/onboarding_status.cs` | observed | semantic index | defines allowed status values | edit |
| `src/api/onboarding_response.cs` | observed | semantic index | exposes status in public response contract | inspect/update |

### Secondary files and dependencies
| File | Relation type | Direction / hop | Evidence | Source class | Selection role | Action |
|---|---|---|---|---|---|---|
| `src/workflows/open_account_handler.cs` | writes-data | status -> writer / 1 | observed | semantic index | direct writer | update transition |
| `tests/onboarding_status_tests.cs` | tested-by | status -> test / 1 | observed | lexical + test discovery | validation | update/add cases |

### Test coverage and validation
| Test or command | Evidence | Purpose | Confidence |
|---|---|---|---|
| `dotnet test --filter OnboardingStatus` | planned | validates status transitions and serialization | medium |

### Patterns to follow
- `src/domain/account_status.cs` - observed enum naming and serialization pattern

### Conflicts / unresolved consumers
- inferred: downstream reporting may consume the serialized status; no reporting repository/path was available in the current evidence set.

### Ripple effects and risks
| Severity | Risk | Evidence | Mitigation |
|---|---|---|---|
| high | external clients may reject an unknown status | observed public response field; external consumers blocked | verify contract/versioning tolerance before release |
| medium | status writer may omit the new transition | observed workflow writer | add transition-focused test |

### Coverage and closure
- Closure: provisional
- Owners/definitions: covered
- Direct consumers: covered
- Runtime/build/config: covered for inspected service
- Tests/validation: covered, not yet executed
- External/dynamic consumers: unresolved
- Traversal: hop 1 covered; expansion stopped at unavailable external reporting boundary
- Context selection quality: no gold/reference set; metrics not claimed

### Suggested sequence
1. Confirm compatibility strategy for external consumers.
2. Update domain status and transition logic.
3. Update serialization/contract tests.
4. Run targeted tests and inspect downstream clients if access becomes available.

### Open questions or blockers
- Do external clients tolerate unknown status values, or is contract versioning required?
