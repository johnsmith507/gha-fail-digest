# Examples

All examples use synthetic fixtures in `tests/fixtures`.

## TypeScript Build Failure

```bash
PYTHONPATH=src python -m gha_fail_digest.cli tests/fixtures/typescript.log
```

Primary fields:

```json
{
  "category": "build_error",
  "error_message": "src/index.ts(14,7): error TS2322: Type 'string' is not assignable to type 'number'.",
  "failing_step_name": "npm run build",
  "suggested_fix_category": "fix compile/type errors"
}
```

## Jest Failure

```bash
PYTHONPATH=src python -m gha_fail_digest.cli --format text tests/fixtures/jest.log
```

```text
Failing step: npm test
Category: test_failure
Suggested fix category: fix failing tests
Error: expect(received).toEqual(expected)
```

## Pytest Failure

```bash
PYTHONPATH=src python -m gha_fail_digest.cli --format text tests/fixtures/pytest.log
```

```text
Failing step: pytest
Category: test_failure
Suggested fix category: fix failing tests
```
