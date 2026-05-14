# Contributing

Small, focused improvements are welcome.

Good contributions:

- add a sanitized fixture for a CI failure pattern
- improve classification for a common test/build/lint failure
- improve output formatting without adding hosted dependencies
- add docs that help people run the tool safely on private logs

Please avoid posting private CI logs. Reproduce issues with synthetic or
sanitized examples.

## Local Checks

```bash
PYTHONPATH=src python -m unittest discover -s tests
python -m compileall src tests
python scripts/verify_public_repo.py
```
