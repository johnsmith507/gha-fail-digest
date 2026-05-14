# Supported Failure Patterns

`gha-fail-digest` looks for the earliest high-signal failure in GitHub Actions
logs and turns it into a compact JSON, text, or Markdown summary.

The first release intentionally covers common, easy-to-sanitize CI failures
rather than every possible log format.

## TypeScript Build Errors

Input shape:

```text
##[group]Run npm run build
npm run build
src/index.ts(14,7): error TS2322: Type 'string' is not assignable to type 'number'.
##[error]Process completed with exit code 2.
```

Detected output:

```json
{
  "category": "build_error",
  "failing_step_name": "npm run build",
  "suggested_fix_category": "fix compile/type errors"
}
```

## Jest Test Failures

Input shape:

```text
##[group]Run npm test
FAIL src/cart.test.ts
  cart totals
    x applies discounts

    expect(received).toEqual(expected)
      at Object.<anonymous> (src/cart.test.ts:17:21)
```

Detected output:

```text
Failing step: npm test
Category: test_failure
Suggested fix category: fix failing tests
```

## Pytest Failures

Input shape:

```text
##[group]Run pytest
============================= FAILURES =============================
>       assert total(10) == 11
E       AssertionError: assert 10 == 11
tests/test_billing.py:8: AssertionError
```

Detected output:

```text
Failing step: pytest
Category: test_failure
Suggested fix category: fix failing tests
```

## Lint Errors

Input shape:

```text
##[group]Run ruff check .
src/app.py:12:5: F401 `json` imported but unused
Found 1 error.
```

Detected output:

```text
Category: lint_error
Suggested fix category: fix lint errors
```

## GitHub Error Annotations

Input shape:

```text
::error file=src/payment.py,line=42,col=9::AssertionError: expected captured amount to equal invoice total
Error: Process completed with exit code 1.
```

Detected output:

```json
{
  "category": "test_failure",
  "error_message": "AssertionError: expected captured amount to equal invoice total"
}
```

## Unsupported Or Weak Signals

When the parser cannot identify a specific failure, it returns
`unknown_failure` or `no_failure_detected`. That is deliberate: uncertain
summaries should stay small and honest instead of inventing a root cause.

The best way to improve coverage is to add a small sanitized fixture under
`tests/fixtures` plus an expected assertion in the parser tests.
