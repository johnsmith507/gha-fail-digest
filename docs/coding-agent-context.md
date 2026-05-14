# Turn Failed GitHub Actions Logs Into Clean Coding-Agent Context

Failed CI logs are usually too long for the job they need to do.

When a GitHub Actions run fails, the useful information is often a small set of
facts:

- which step failed
- what kind of failure it was
- the primary error line
- whether there is a stack trace
- enough nearby context to start fixing it

That is also the information a coding agent needs. Pasting a whole log file into
an agent usually adds noise, wastes context, and risks sharing information that
did not need to leave your machine.

`gha-fail-digest` is a small local CLI for this narrow workflow. It reads GitHub
Actions logs and emits a compact JSON, text, or Markdown summary.

Install the release wheel:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install \
  https://github.com/johnsmith507/gha-fail-digest/releases/download/v0.1.0/gha_fail_digest-0.1.0-py3-none-any.whl
```

## Before

A CI run might contain thousands of lines across install, build, lint, and test
steps. The actual failure can be buried near the end:

```text
##[group]Run npm run build
> app@1.0.0 build
> tsc --noEmit

src/index.ts(14,7): error TS2322: Type 'string' is not assignable to type 'number'.
Error: Process completed with exit code 2.
```

That is enough to fix the problem, but it is not a clean handoff yet.

## After

Run:

```bash
gha-fail-digest --format text tests/fixtures/typescript.log
```

Output:

```text
Failing step: npm run build
Category: build_error
Suggested fix category: fix compile/type errors
Error: src/index.ts(14,7): error TS2322: Type 'string' is not assignable to type 'number'.
```

Or emit JSON for automation:

```bash
gha-fail-digest --compact tests/fixtures/typescript.log
```

```json
{"category":"build_error","error_message":"src/index.ts(14,7): error TS2322: Type 'string' is not assignable to type 'number'.","failing_step_name":"npm run build","source_count":1,"suggested_fix_category":"fix compile/type errors"}
```

## Agent Handoff

The summary is meant to become a small, specific prompt:

```text
Fix the GitHub Actions failure below. Start by reading the files referenced in
the error and run the narrowest test/build command that reproduces it.

Failing step: npm run build
Category: build_error
Suggested fix category: fix compile/type errors
Error: src/index.ts(14,7): error TS2322: Type 'string' is not assignable to type 'number'.
```

That is more useful than asking an agent to infer the failure from an entire log
archive.

## Inputs

`gha-fail-digest` supports:

- local `.log` and `.txt` files
- directories of logs
- downloaded GitHub Actions log ZIPs
- stdin
- GitHub Actions run URLs

Local files, ZIPs, directories, and stdin require no credentials.

GitHub Actions run URL mode uses GitHub's logs endpoint from your machine. If
the run is private or GitHub requires authentication, set `GITHUB_TOKEN` in the
environment.

## Privacy Boundary

The tool is intentionally local-first:

- no telemetry
- no third-party AI API
- no hosted log ingestion
- no account required for local parsing

You should still sanitize output before posting it publicly. CI logs can include
private package names, internal paths, repository names, hostnames, or accidental
secrets.

## Current Categories

The first version is deliberately simple:

- `test_failure`
- `build_error`
- `lint_error`
- `dependency_error`
- `unknown_failure`
- `no_failure_detected`

It is a heuristic parser, not a full observability product. That is the point:
the output should be small, explainable, and easy to improve with sanitized
fixtures.

## Try It

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install \
  https://github.com/johnsmith507/gha-fail-digest/releases/download/v0.1.0/gha_fail_digest-0.1.0-py3-none-any.whl
gha-fail-digest --format text path/to/action.log
```

The repository also includes synthetic fixtures for pytest, Jest, TypeScript,
and lint failures so you can test the parser without using private CI logs.

## What Comes Next

Useful next improvements:

- more fixture coverage for common CI failures
- confidence scores when multiple failures are detected
- issue/PR comment template output
- SARIF-style output
- team-specific classification rules

If you try it on a real failure and the parser misses the important line, the
most helpful issue is a small sanitized fixture that reproduces the pattern.
