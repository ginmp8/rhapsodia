# JSON version inventory

| Class | Examples | Release-coupled? |
|---|---|---|
| package-release | marketplace/catalog.json plugin.version, marketplace.version; generated host plugin manifests; MANIFEST.json package_version | yes: 0.6.0 |
| internal-semantic | agent-system-contract/v4, dynamic-workflow-plan/v1, convergence-plan/v1, workflow-plan/v1, workflow-plan/v2, schema/manifest versions | no |

The release validator checks the known package-release surfaces. Internal semantic versions change only when their own contract changes.
