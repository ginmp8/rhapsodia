# API and Business Abuse Review

Use this reference for APIs, webhooks, service-to-service integrations, partner APIs, expensive operations, sensitive business workflows, or flows that consume third-party API responses.

## Authorization lenses

Check independently:

- **object-level authorization**: actor/tenant is allowed to act on this concrete resource id;
- **property-level authorization**: actor can read/write each sensitive field accepted or returned;
- **function-level authorization**: actor can invoke the operation at all;
- **state-transition authorization**: actor can perform this transition from the current resource state.

Authentication or a caller-supplied tenant/resource id is never sufficient proof of authorization.

## Business-flow abuse

Look beyond technical injection bugs. Identify operations whose legitimate automation can be abused at scale: sign-up, purchase, transfer, redeem, reserve, invite, submit, approve, search, export, password/reset, OTP, document generation, AI/tool invocation, or other scarce/costly actions.

Check:

- per-actor/resource/tenant limits;
- velocity and concurrency limits;
- idempotency and duplicate intent;
- economic or quota amplification;
- sequencing/precondition bypass;
- automation/bot resistance where the business invariant requires it;
- auditability and recovery after abuse.

## Resource and cost exhaustion

Inspect unbounded arrays, page sizes, recursion, fan-out, expensive filters, regex/parsing, uploads, archive expansion, external calls, model/tool calls, concurrency, and retry amplification. Limits must exist at the component that incurs the cost; an upstream UI limit is not a security boundary.

## Third-party API consumption

Treat responses from upstream/partner APIs as untrusted data crossing a trust boundary. Validate schema, length, type, enum/range, ownership/resource identifiers, redirect/URL values, content type, signatures when part of the contract, and any field that can influence authorization, persistence, rendering, file paths, commands, or downstream requests.

A trusted vendor identity does not make every returned field safe for every sink.

## SSRF and inventory/version exposure

When APIs fetch user- or upstream-controlled URLs, inspect destination validation, redirect behavior, DNS/IP changes, metadata/internal-network reachability, protocol restrictions, response-size/time limits, and credential forwarding.

When the surface is versioned or externally deployed, inspect obsolete/debug endpoints, shadow hosts, undocumented versions, and mismatches between deployed inventory and reviewed contracts when evidence is available.

## Required output

For each material abuse case state actor, resource/business asset, precondition, abuse path, control expected, evidence, impact, smallest mitigation, and validation. Keep speculative API Top 10 categories as hypotheses until the target path is evidenced.

## Research basis

Review lenses are informed by the OWASP API Security Top 10 2023, especially object/property authorization, unrestricted resource consumption, sensitive business flows, SSRF, inventory management, and unsafe consumption of APIs.
