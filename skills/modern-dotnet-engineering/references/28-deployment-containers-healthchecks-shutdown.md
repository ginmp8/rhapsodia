# Deployment, Containers, Aspire, Health Checks, and Graceful Shutdown

## Runtime requirements

- Liveness and readiness must have different meanings.
- Startup should fail fast for invalid required configuration.
- Graceful shutdown should stop admitting new work and finish/cancel in-flight HTTP/worker work predictably.
- Containers should run as non-root when feasible.
- Secrets/configuration should arrive through platform mechanisms rather than image contents.
- Database migrations should be deployment-controlled for important systems.
- Release artifacts must preserve provenance that maps deployment bytes to source, SDK/runtime, and dependency evidence.

## Immutable runtime patch ownership

Container and self-contained artifacts embed runtime/base-image bytes that do not update themselves. The delivery pipeline owns rebuild/redeploy after relevant runtime/base-image servicing. Verify the runtime/base image in the final artifact, not only the build host.

## Container image trade-offs

Minimal/chiseled/distroless-style images can reduce surface area and size, but they remove shells/package managers/diagnostic conveniences. Adopt them only with an operational debugging path such as external diagnostics, ephemeral debug containers, platform tooling, or a documented alternate image strategy.

## Health checks

- Liveness: process/runtime is alive enough that restart may help only when truly stuck/broken.
- Readiness: instance is able to accept the workload now.
- Do not make readiness depend on every downstream system if doing so would unnecessarily remove otherwise useful instances.
- Avoid exposing sensitive dependency details publicly.

## Aspire boundary

Aspire is an optional developer/cloud-native orchestration and observability layer for modeling, running, and deploying distributed applications. It is not an application framework, cloud provider, or production runtime.

Use Aspire when service topology, local orchestration, service discovery, telemetry defaults, and developer workflow materially benefit. Do not introduce it merely because a service is .NET.

Keep Aspire ServiceDefaults limited to cross-cutting operational setup such as telemetry, health, resilience/service-discovery configuration. Do not turn ServiceDefaults into a shared domain/application/kernel project.

## Validation gates

- Scan the final image and verify effective non-root user/runtime/base-image identity.
- Run container/published-artifact smoke tests.
- Exercise SIGTERM/graceful shutdown with in-flight HTTP and worker work.
- Verify readiness/liveness behavior during dependency failure.
- For Aspire adoption, prove a concrete reduction in orchestration/observability setup burden and preserve deployability independent of a local developer dashboard.

Fresh source: https://aspire.dev/get-started/what-is-aspire/
