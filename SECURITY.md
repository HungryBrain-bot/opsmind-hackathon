# Security Policy

## Supported version

The current hackathon release is `1.6.x`. Earlier MVP versions are not maintained.

## Reporting a vulnerability

Please do not publish security vulnerabilities in a public issue.

Use GitHub's private vulnerability reporting feature when available. Include:

- Affected component and version
- Reproduction steps
- Expected and observed behavior
- Potential impact
- Any suggested mitigation

## Current security boundaries

OpsMind v1.6 is a hackathon MVP and is not hardened for production use. In particular:

- Authentication and authorization are not implemented.
- CORS is permissive for local demonstration.
- File-based investigation storage is intended for a single local user.
- Enterprise connectors and evidence are demo-oriented.
- Automated remediation is intentionally not implemented.
- Secrets should be supplied through environment variables and must never be committed.

Do not expose this build directly to the public internet or connect it to production systems without adding appropriate identity, authorization, tenant isolation, secrets management, audit controls, transport security, and deployment hardening.
