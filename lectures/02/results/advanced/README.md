# Advanced run evidence

These files were exported from the student's Colab run `20261107T045051Z_3b9000` and checked against the prepared materials.

- Original archive: `advanced_results_20261107T045051Z_3b9000.zip`
- Archive SHA-256: `42448660f57742793e009faf7984f41d60fa5404d370f570c90e973368602df2`
- Raw exports preserved unchanged: `result.json`, the three `eval_*.json` files, `training.json`, `training_log.json`, and `manual_review.csv`.
- Prepared runtime materials are byte-identical to the files in [the Advanced materials directory](../../advanced/); their hashes are also recorded in `result.json`.
- `verification.json` records the checks of material hashes, per-question scores, summaries, regression list, and training log consistency.
- `training_console_summary.json` preserves numbers supplied from the training console, including the trainable parameter fraction.
- `manual_review_assisted.md` and `.json` contain a subsequent, explicitly AI-assisted semantic comparison for all 18 questions.

The original `manual_review.csv` is blank because it was exported before the subsequent assisted review. Likewise, `result.json` retains its export-time review status. Follow-up analysis is kept separately rather than modifying raw evidence. The source manifest's preparation-status label describes the materials at preparation time; completed training is recorded in the top-level run metrics and training files.

The original ZIP and its full extracted snapshot, including all materials and the generated report draft, are also retained locally. Model weights and checkpoints were not included in the exported ZIP.
