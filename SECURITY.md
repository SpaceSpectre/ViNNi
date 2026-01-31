# Security Policy

## Supported Versions

Only the latest `main` branch of ViNNi is currently supported for security updates.

| Version | Supported          |
| ------- | ------------------ |
| v0.2.x  | :white_check_mark: |
| v0.1.x  | :x:                |

## Reporting a Vulnerability

We take the security of ViNNi seriously. If you discover a vulnerability, please follow these steps:

1.  **Do NOT open a public issue.** This prevents potential exploitation while we work on a fix.
2.  **Contact the Creator Privately**: Please reach out to Abhishek Arora directly with details of the vulnerability.
3.  **Includes**:
    - Description of the issue.
    - Steps to reproduce.
    - Potential impact.
    - Any relevant logs or screenshots (redact sensitive info).

## Scope

This policy covers:
- Core ViNNi logic (`vinni/`).
- Local logging and data handling.
- Integration with Ollama (though Ollama bugs should be reported to them).

We are **not** responsible for:
- Vulnerabilities in the underlying LLM models (Llama, Qwen).
- Security of the user's local operating system or network.

## Remediation

We aim to address critical security issues within 48 hours of acknowledgment. Fixes will be pushed to the `main` branch.
