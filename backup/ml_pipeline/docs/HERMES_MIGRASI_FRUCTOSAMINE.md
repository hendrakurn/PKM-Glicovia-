# Hermes Guide: Migrating the Viscosity Feature to Fructosamine

## Task Summary

You are working in this repository:

```text
/home/hendra/projects/pkmGlico/ml_pipeline
```

The main goal is to migrate the third feature in the GlicoSaliva ML Pipeline from:

```text
viscosity_cP
```

to:

```text
fructosamine_umol_l
```

The current pipeline features are:

```text
glucose_saliva
ph_value
viscosity_cP
```

The target pipeline features are:

```text
glucose_saliva
ph_value
fructosamine_umol_l
```

This must be treated as a feature schema migration, not a simple string rename. The pipeline must remain consistent across data generation, data loading, preprocessing, training, inference, API validation, metadata, documentation, and tests.

## Objectives

1. Replace saliva viscosity with fructosamine as an exploratory candidate biomarker feature.
2. Keep the feature contract consistent across all modules.
3. Prevent old model, scaler, and processed-data artifacts based on `viscosity_cP` from being treated as valid.
4. Make the pipeline able to regenerate dummy data, preprocess, retrain, evaluate, and run inference with the new feature.
5. Keep scientific language careful: fructosamine is an exploratory prototype feature, not a final clinical diagnostic claim.

## Relevant Hermes Skills

Use the relevant Hermes skills for:

- repository/codebase analysis;
- Python ML pipeline editing;
- test updates and test execution;
- code review/self-check;
- artifact regeneration if the project has official pipeline commands and they are safe to run.

If Hermes provides specific skills for coding agents, Python, ML pipelines, testing, or review, activate those skills before implementation.

## New Feature Assumptions

Canonical column name in source code, CSV, JSON, API schemas, scaler metadata, and tests:

```text
fructosamine_umol_l
```

Human-facing label for documentation or UI:

```text
Fructosamine (umol/L)
```

Use ASCII in code and data. Do not use the `µ` character in column names, because `fructosamine_umol_l` is safer for CSV, JSON, CLI, and API usage.

Unit:

```text
umol/L
```

Global dummy/prototype bounds:

```text
150 to 500
```

Class-wise dummy distribution:

| Class | Mean | Std |
| --- | ---: | ---: |
| Normal | 220 | 18 |
| Pre-Diabetes | 285 | 25 |
| Diabetes | 375 | 40 |

Methodology notes:

- Fructosamine is more commonly known as a serum/plasma biomarker. In this pipeline, treat it as an exploratory surrogate feature for a prototype.
- Do not make fructosamine a near-deterministic proxy for the target.
- A positive, moderate relationship with glycemic status is acceptable, but the generated data should still include noise and overlap between classes.
- The model target remains `bg_mgdl_reference`.
- The class label remains `bg_class`.

## Files to Inspect and Change

### 1. `src/generate_dummy.py`

Update the dummy data generator so it produces `fructosamine_umol_l` instead of `viscosity_cP`.

Required updates:

- Update `DEFAULT_CLASS_MEANS`.
- Update `DEFAULT_CLASS_STDS`.
- Update `FEATURE_BOUNDS`.
- Update the random outlier feature selection.
- Update the feature generation logic from `viscosity` to `fructosamine`.
- Update CSV row output.
- Update `feature_ranges` metadata.
- Update docstrings and examples if present.

The new generated CSV must have these columns:

```text
id,glucose_saliva,ph_value,fructosamine_umol_l,bg_class,bg_mgdl_reference
```

### 2. `src/data_loader.py`

Update the input data schema:

- `REQUIRED_COLUMNS`
- `FEATURE_COLUMNS`
- error messages or validation logic that mention the old feature

Target feature columns:

```python
FEATURE_COLUMNS = ["glucose_saliva", "ph_value", "fructosamine_umol_l"]
```

### 3. `src/preprocessing.py`

Update the preprocessing schema:

- `REQUIRED_COLUMNS`
- `FEATURE_COLUMNS`
- scaler metadata if feature names are persisted
- preprocessing reports if they mention feature names

Make sure the processed arrays still contain exactly 3 features.

### 4. `src/inference.py`

Update the inference contract:

- `FEATURE_ORDER`
- single-input examples
- batch-input examples
- input validation if present
- exports or reports that mention the old feature

Target feature order:

```python
FEATURE_ORDER = ["glucose_saliva", "ph_value", "fructosamine_umol_l"]
```

### 5. `src/api_connector.py`

Update API schema and validation:

- Remove the `viscosity_cP` field.
- Add the `fructosamine_umol_l` field.
- Validation range: `150` to `500`.
- Description: `Fructosamine concentration (umol/L)`.
- Update the single-payload example.
- Update the batch-payload example.
- Update `validate_prediction_input`.
- Update `required_fields`.
- Update the `features` tuple/list used for validation.
- Update `ranges`.
- Update the `/model-info` feature list.

New example payload:

```json
{
  "glucose_saliva": 1.5,
  "ph_value": 6.5,
  "fructosamine_umol_l": 285
}
```

### 6. `src/pipeline.py`

Inspect and update if any of these are hardcoded:

- feature lists;
- pipeline metadata;
- schema summaries;
- reports that mention `viscosity_cP`.

### 7. `src/train_svm.py`

Inspect and update if any of these are hardcoded:

- feature lists;
- logs;
- model metadata;
- docstrings that mention the old feature.

### 8. `src/evaluate.py`

Inspect and update if any of these are present:

- report text;
- feature metadata;
- internal documentation that mentions `viscosity_cP`.

### 9. `run_inference.py`

Check whether CLI examples or default payloads still use `viscosity_cP`. Update them to `fructosamine_umol_l`.

### 10. `tests/`

Search every test for:

```text
viscosity_cP
viscosity
FEATURE_COLUMNS
FEATURE_ORDER
```

Update all expectations to the new schema.

Add or update tests to verify:

- the dummy CSV has a `fructosamine_umol_l` column;
- the dummy CSV no longer has a `viscosity_cP` column;
- `FEATURE_COLUMNS` is correct;
- `FEATURE_ORDER` is correct;
- the API accepts `fructosamine_umol_l`;
- the API no longer requires `viscosity_cP`;
- the API rejects requests missing `fructosamine_umol_l`;
- scaler metadata stores the new feature.

### 11. Documentation

Inspect documentation files such as:

- `docs/MODULE_DOCS.md`
- `flow.md`
- `flow_mermaid.md`
- `flow_pkm_formal.md`
- `ml_pipeline_cheat_sheet.md`
- README files if present

Update active references from `viscosity_cP` to `fructosamine_umol_l`.

If a section intentionally discusses migration history, it may mention `viscosity_cP` as the old feature. However, it must not look like the active feature contract for the new pipeline.

## Old Artifacts

Old artifacts based on `viscosity_cP` must not be treated as valid for the new schema.

Artifacts to consider:

```text
src/data/dummy/generated_data.csv
src/data/dummy/metadata.json
src/data/processed/*.npy
src/data/processed/scaler_params.json
src/data/processed/preprocessing_report.json
src/models/best_model.pkl
src/models/experiment_log.json
src/models/fold_results/*.json
src/evaluation/*
src/pipeline_results/*.json
```

Consequences:

- The old `best_model.pkl` may still technically accept 3 features, but it is scientifically invalid because the semantic meaning of the third feature has changed.
- The old `scaler_params.json` still contains mean/std values for `viscosity_cP`, so it must be treated as obsolete and regenerated.
- `X_train.npy`, `X_test.npy`, and other processed artifacts must be regenerated.
- Old evaluation reports cannot be used as results for the new feature schema.

Instructions:

- If the project has official commands for regeneration/retraining, use those commands.
- Do not delete important artifacts without a clear reason.
- If old artifacts need to be cleaned up, prefer archiving or regenerating through the official pipeline.
- If you are not sure whether an artifact may be deleted, do not delete it. Explain the uncertainty in the final response.

## Expected Work Sequence

1. Inspect the repository with `rg`.
2. Search for all references to:

```text
viscosity_cP
viscosity
FEATURE_COLUMNS
FEATURE_ORDER
```

3. Update source code consistently.
4. Update tests.
5. Update relevant documentation.
6. Run formatting/linting if available.
7. Run unit tests.
8. Regenerate dummy data.
9. Run preprocessing again.
10. Retrain the model.
11. Evaluate the model.
12. Smoke test single and batch inference.
13. Smoke test the API schema if possible.
14. Confirm there are no active references to the old feature in source, tests, or documentation.

## Acceptance Criteria

The migration is complete when:

- Main source files use `fructosamine_umol_l`.
- `FEATURE_COLUMNS` and `FEATURE_ORDER` use:

```python
["glucose_saliva", "ph_value", "fructosamine_umol_l"]
```

- The new dummy CSV has these columns:

```text
id,glucose_saliva,ph_value,fructosamine_umol_l,bg_class,bg_mgdl_reference
```

- The `/predict` API accepts:

```json
{
  "glucose_saliva": 1.5,
  "ph_value": 6.5,
  "fructosamine_umol_l": 285
}
```

- The API no longer requires `viscosity_cP`.
- The new model and scaler are generated from the new feature schema.
- Tests pass, or every remaining failure is explained clearly.
- This search does not find active references to the old feature:

```bash
rg "viscosity_cP|viscosity" src tests docs *.md
```

Note: this search may still find references in this migration guide or in explicit historical notes, but there must be no active use of the old feature in the new pipeline.

## Constraints

- Do not change the model target `bg_mgdl_reference`.
- Do not change the class label `bg_class`.
- Do not perform broad refactors outside the feature migration.
- Do not add new dependencies unless truly necessary.
- Do not make final clinical diagnostic claims.
- Use language that describes fructosamine as a candidate feature for a prototype.
- If file conflicts occur or commands fail, continue with the best available approach and explain the result in the final response.

## One-Shot Prompt for Hermes

Use this prompt to run the task directly:

```text
You are working in /home/hendra/projects/pkmGlico/ml_pipeline.

Task: implement an end-to-end migration of the third GlicoSaliva ML Pipeline feature from viscosity_cP to fructosamine_umol_l.

Read the full guide at docs/HERMES_MIGRASI_FRUCTOSAMINE.md and follow it.

Target features:
- glucose_saliva
- ph_value
- fructosamine_umol_l

Fructosamine assumptions:
- unit: umol/L
- bounds: 150 to 500
- Normal: mean 220, std 18
- Pre-Diabetes: mean 285, std 25
- Diabetes: mean 375, std 40

Do not only rename strings. Update source code, tests, relevant documentation, dummy generator, API schema, inference feature order, preprocessing feature columns, and pipeline artifacts if they can be safely regenerated.

Old model/scaler/data artifacts based on viscosity_cP must be treated as obsolete. After changing the source code, regenerate dummy data, rerun preprocessing, retrain the model, evaluate it, and smoke test inference/API if commands are available.

Acceptance criteria:
- FEATURE_COLUMNS and FEATURE_ORDER use ["glucose_saliva", "ph_value", "fructosamine_umol_l"].
- The new dummy CSV uses columns id,glucose_saliva,ph_value,fructosamine_umol_l,bg_class,bg_mgdl_reference.
- The API accepts fructosamine_umol_l and no longer requires viscosity_cP.
- Tests pass, or remaining failures are explained.
- The final response includes changed files, regenerated artifacts, commands run, test results, and a short scientific-risk note.

Start implementation now in one run.
```

## Required Final Response Format for Hermes

At the end, Hermes must report:

```text
Summary:
- ...

Changed files:
- ...

Regenerated artifacts:
- ...

Commands run:
- ...

Test results:
- ...

Scientific-risk note:
- Fructosamine is used as an exploratory surrogate feature for a prototype, not as a final clinical diagnostic claim.

Remaining risks or follow-up:
- ...
```
