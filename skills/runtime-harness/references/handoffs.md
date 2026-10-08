# Content-pinned handoffs

## Producer

Pass `task_id`, `next_action`, 1..32 exact refs and optional bounded one-line summary.
Supported pins include tools, skills, agents, repository files, shared `resource://`
files and workspace identity. Every selected resource must currently resolve.

Files/resources receive current SHA-256 pins; local tools/workspace receive identities.
The immutable receipt contains no permission grants, arbitrary command fields, secrets,
transcripts or claimed test verdicts. Summary/action strings remain untrusted data.

If a missing exact tool is required, an execution-authorized producer may `ensure` it
before handoff. If native work found a stable reusable file, `observe-resource` can make
that location addressable for the receiver. Do not publish domain conclusions merely to
avoid writing a proper domain handoff/artifact.

## Consumer

`handoff-resume --id <ID>` resolves every pin against the current store. Changed pinned
file/resource bytes fail closed. Unrelated new observations do not invalidate the receipt.

For another machine/workspace, transport only the receipt and authorized portable source
artifacts, then use `--input <FILE> --rebind`. Local tool identities are rebound; content
pins must still match. Runtime rebind proves identity consistency only, not minimum
version compatibility, authority or task completion.

A receiver should reuse the pinned observations rather than repeat search. If a required
unpinned tool/resource is missing, normal lazy discovery rules apply within that agent's
existing authority.

Contract: [runtime-handoff-v1](../contracts/runtime-handoff-v1.schema.json).
