## Summary

Describe the parser, output, fixture, or documentation change.

## Validation

```bash
PYTHONPATH=src python -m unittest discover -s tests
python -m compileall src tests
python scripts/verify_public_repo.py
```

## Privacy Check

- [ ] I did not include private CI logs.
- [ ] Any fixture or example is synthetic or sanitized.
- [ ] I did not include credentials, customer data, private hostnames, or internal repository names.
