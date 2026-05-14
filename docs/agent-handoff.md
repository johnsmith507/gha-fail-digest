# Agent Handoff Template

Use this when a coding agent needs to fix a failed GitHub Actions run.

```text
We need to fix a GitHub Actions failure.

Constraints:
- Use the existing project style and test commands.
- Start by inspecting the files named in the failure summary.
- Reproduce with the narrowest relevant command before broad test runs.
- Do not change unrelated files.
- Do not paste private logs or credentials into public comments.

Failure summary:

<paste gha-fail-digest JSON, text, or Markdown output here>

Expected result:
- code or docs fix
- relevant tests passing
- short explanation of the root cause
```

For public issues or PR comments, remove anything that could identify private
infrastructure, customers, credentials, internal paths, or private repository
names.
