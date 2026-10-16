# Required-session reference notes

Checked 2026-10-16. Primary sources govern the following bounded guidance; repository source
and executed tests govern the implementation. No external source authorizes a local action.

| Source | Supported guidance |
|---|---|
| Microsoft PowerShell, about_Pipeline_Chain_Operators | Conditional `&&`/`||` start in PowerShell 7; semicolon alone is not equivalent |
| Microsoft PowerShell, about_Language_Modes | Method invocation restrictions can follow ConstrainedLanguage; do not weaken policy |
| AWS CLI, IAM Identity Center configuration | SSO login uses the configured profile/session and human authorization; credentials are private |
| VS Code, Custom agents | Profile tools and visibility depend on host/harness; inspect actual tool execution rather than treating instructions as enforcement |

```text
https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pipeline_chain_operators?view=powershell-7.6
https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_language_modes?view=powershell-7.6
https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html
https://code.visualstudio.com/docs/agent-customization/custom-agents
```

The default runtime registry does not probe PowerShell language mode, run Git, authenticate or
install software. Shell/tool/profile applicability is an explicit producer/user observation.
Documentation examples are not local measured fixes. No host/model token or latency benchmark
was performed merely by checking these references.
