# Security Policy

## Scope
Agent Log Viewer reads local text/JSONL files and prints derived output. It performs no network requests, telemetry, credential discovery, or code execution from log content.

## Sensitive logs
Logs can contain prompts, tokens, credentials, personal data, or tool output. Review files before sharing them. The tool does not redact secrets automatically and does not modify source logs.

## Reporting
Please report security concerns privately through GitHub's security reporting features when available. Do not open a public issue containing secrets or sensitive log samples.

## Supported version
Security fixes target the latest release on `main`.
