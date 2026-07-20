# Validation and Packaging

## Board Validation

Use `scripts/validate_repo_board.py` as the canonical board entrypoint. It validates cycle path/metadata consistency, identity/ULID rules, registry consistency, duplicate active features, dependencies/DAG, package identity, technical design, prohibited aggregate placement, and sibling-cycle conflicts.

Use `scripts/validate_concurrent_board.py` for a single resolved cycle root. Old layouts are read-only `adapt` inputs and are never accepted as active board roots.

## Generated Views

Run `scripts/render_registry_views.py <board_root> --output <external-dir>`. Re-running unchanged input must produce byte-identical output and the same registry digest. Run `scripts/validate_generated_view_contract.py <skill-root>` whenever renderer or projection templates change.

## Package-Level Gates

Before packaging MAGO, run all of these:

1. `python scripts/validate_skill_package.py <skill-root>`;
2. `python scripts/validate_planning_execution_handoff.py <skill-root>`;
3. `python scripts/validate_generated_view_contract.py <skill-root>`;
4. `python scripts/validate_boundary.py <skill-root>`;
5. `python scripts/validate_activation_scenarios.py <skill-root>`;
6. `python -B -m unittest discover -s tests -p 'test_*.py'`;
7. compile every script without creating caches;
8. run a canonical create/register/render/validate fixture;
9. package as `skill.zip` with one top-level `mago/` directory;
10. extract the ZIP and repeat skill, handoff, generated-view, boundary, activation, and test gates.

The packager must exclude caches, reports, generated views, old ZIPs, secrets, credentials, and temporary fixtures. Do not claim readiness when any required gate fails.
