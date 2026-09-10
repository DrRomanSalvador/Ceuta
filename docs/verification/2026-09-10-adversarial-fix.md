# Verification — adversarial validation severity repair

## Traceability

- **Task:** correct severity semantics in `backend/app/core/adversarial_validation.py`.
- **Root cause:** temporal/prospective validation findings used unconditional severity values that contradicted the existing test contract.
- **Change:** `NO_TEMPORAL_VALIDATION` is `CRITICAL` only for temporally/external validated maturity claims; otherwise `MAJOR`. Missing prospective dataset is `MAJOR`; a present dataset without prospective evaluation remains `CRITICAL`.
- **Verification:** GitHub Actions repair run `34470431324` completed successfully.
- **Test result:** `82 passed, 2 warnings`.
- **Additional checks:** Python compilation and `docker compose config -q` completed successfully in the same verification run.
- **Temporary automation:** the repair workflow removed itself after persisting the verified source change.
