# Supply Chain, Dependencies, CI/CD, and Script Security

## Dependency governance

- Use central package management.
- Prefer pinned explicit versions.
- Review direct install-from-url patterns.
- Check vulnerability scanner output before claiming CVEs.
- Remove unused packages.
- Treat pre-release packages as explicit risk decisions.

## CI/CD security

- Do not print secrets.
- Use least-privilege tokens.
- Pin actions/tools where policy requires it.
- Separate build, test, scan, package, deploy.
- Require approval for production deployment.

## Script security

Review scripts for shell injection, path traversal, unsafe archive extraction, broad deletes, unsafe file writes, untrusted deserialization, and execution of untrusted inputs.
