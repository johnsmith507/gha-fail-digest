# Demo Transcript

This transcript uses only synthetic fixture logs included in the product.

## TypeScript Build Failure

Command:

```bash
PYTHONPATH=src python3 -m gha_fail_digest.cli tests/fixtures/typescript.log
```

Output excerpt:

```json
{
  "category": "build_error",
  "error_message": "src/index.ts(14,7): error TS2322: Type 'string' is not assignable to type 'number'.",
  "failing_step_name": "npm run build",
  "suggested_fix_category": "fix compile/type errors"
}
```

## Jest Test Failure

Command:

```bash
PYTHONPATH=src python3 -m gha_fail_digest.cli --format text tests/fixtures/jest.log
```

Output:

```text
Failing step: npm test
Category: test_failure
Suggested fix category: fix failing tests
Error: expect(received).toEqual(expected)

Stack trace:
  at Object.<anonymous> (src/cart.test.ts:17:21)
```

## How A Buyer Uses This

1. Download failed GitHub Actions logs.
2. Run `gha-fail-digest logs.zip`.
3. Paste the JSON, text, or Markdown result into an issue, PR comment, incident note, or coding-agent prompt.
