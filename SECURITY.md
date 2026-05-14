# Security

`gha-fail-digest` is a local-first log parser. It should not transmit local logs
to third-party services.

## Reporting

If you find a security issue, open a minimal public issue only when it can be
described without secrets, private logs, tokens, customer data, or exploit-ready
payloads.

For normal bugs, include a sanitized fixture that reproduces the parser behavior.

## Token Handling

GitHub Actions run URL mode may use `GITHUB_TOKEN` to download logs from GitHub.
The token is read from the environment and is not printed, stored, or included in
output.

Prefer fine-grained tokens with the narrowest required repository access.
