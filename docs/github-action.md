# GitHub Action

Use `gha-fail-digest` inside a workflow when you want a compact failure summary
from a captured log file.

The action installs this package from the checked-out action directory, runs the
CLI, prints the digest, and exposes it as the `digest` output.

## Summarize a Failed Test Log

```yaml
name: CI

on:
  pull_request:
  push:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        id: test
        continue-on-error: true
        run: |
          set -o pipefail
          npm test 2>&1 | tee test.log

      - name: Summarize failed tests
        if: steps.test.outcome == 'failure'
        id: digest
        uses: johnsmith507/gha-fail-digest@main
        with:
          path: test.log
          format: markdown
          output-file: gha-fail-digest.md
          step-summary: true

      - name: Upload failure digest
        if: steps.test.outcome == 'failure'
        uses: actions/upload-artifact@v4
        with:
          name: gha-fail-digest
          path: gha-fail-digest.md

      - name: Preserve test failure
        if: steps.test.outcome == 'failure'
        run: exit 1
```

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `path` | Yes | | Log file, directory of logs, GitHub logs ZIP, run URL, or `-` for stdin. |
| `format` | No | `markdown` | `markdown`, `text`, or `json`. |
| `compact` | No | `false` | Emits compact JSON when `format` is `json`. |
| `output-file` | No | | Writes the digest to a file for artifact upload or later steps. |
| `step-summary` | No | `false` | Appends the digest to the GitHub Actions step summary. |

## Outputs

| Output | Description |
| --- | --- |
| `digest` | The rendered failure digest. |

## Notes

- The action does not call any AI API or collect telemetry.
- Local log files remain inside the workflow runner.
- If you pass a GitHub Actions run URL, provide `GITHUB_TOKEN` when GitHub
  requires authentication to download the logs.
