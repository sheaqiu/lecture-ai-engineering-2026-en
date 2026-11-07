# Lecture 02 Answers

## Exercises

### Original FAQ experiment

I ran the original course notebook and exported its results. This section reports the original FAQ task, in which the FAQ was included in the model input. The glossary homework below is a separate closed-book experiment with different questions.

- Model: `Qwen/Qwen3.5-0.8B`, revision `2fc06364715b967f1860aea9cf38778875588b17`.
- Method: LoRA without quantization; `r=16`, `lora_alpha=32`, learning rate `2e-4`, 20 epochs, seed 42.
- Generation: greedy (`do_sample=false`), maximum 96 new tokens.
- Training executed personally: **Yes** (`executed_training_myself=true`).

| Metric | Before training | After training |
|---|---:|---:|
| JSON format compliance | 20/21 (95.24%) | 21/21 (100%) |
| Content pass under the course keyword rules | 8/21 (38.10%) | 20/21 (95.24%) |
| Both format and content pass | 8/21 (38.10%) | 20/21 (95.24%) |

There were no automatic regressions. The remaining failed question was **“Do office hours require an appointment?”** The model returned the Tuesday office-hours schedule with `needs_review=false`. The FAQ supplies a schedule but does not specify appointment requirements, so this response does not establish the requested fact. Before training, some other responses contained useful answer text but used an incorrect review flag; one response omitted `needs_review` entirely.

### Knowledge questions from original section 6

| Question | Before classification | After classification | Observation |
|---|---|---|---|
| Final assignment deadline | asserted | asserted | Reuses the ordinary assignment deadline, although the exercise labels the final-assignment question as unsupported. |
| Instructor's name | needs_review | needs_review | Changes from `None` to a clear confirmation-needed response. |
| Topic of the next lecture | needs_review | needs_review | Continues requesting confirmation, with wording closer to the training target. |
| Ordinary assignment deadline, as a control | asserted | asserted | Correctly answers from the FAQ. |

The fictional FAQ's ordinary assignment deadline does not establish an explicit deadline for a final assignment. This is an evidence-boundary distinction within the exercise, not a claim about the real course deadline.

Training improved the task's format, answer wording, and many review-flag decisions, but it did not eliminate unsupported assertions. Format compliance and reliable evidence assessment are different capabilities.

Evidence: [original result](results/faq_baseline/result.json), [before answers](results/faq_baseline/eval_before.json), [after answers](results/faq_baseline/eval_after.json).

## Homework

**Level attempted: Advanced.**

### Data and implementation

The source was the repository's [course glossary](../../data/glossary.json), at course-source commit `2a89014410768f2307a72d0727d1c6bdb29cd726`. It contains 58 entries and is explicitly marked as a draft glossary.

Codex ran the supplied `scripts/make_sft_dataset.py` to generate 116 `messages` records: “What is {term}?” and “Briefly explain {term}.” for each entry, using its definition as the answer. The [original script output](advanced/glossary_sft.jsonl) was preserved. To retain the course's structured-answer task, the definitions were wrapped as JSON with `answer` and `needs_review=false`, and the same system instruction was added to training and evaluation. Eight negative training examples about unlisted terms were added, with a confirmation-needed answer and `needs_review=true`.

| Split | Records | Purpose |
|---|---:|---|
| Training | 124 | 116 glossary question/definition pairs plus 8 unlisted-term questions. |
| Validation | 12 | 8 known-term questions in another wording and 4 different unlisted terms. |
| Test | 18 | 6 named-term questions, 6 paraphrases, and 6 further unlisted terms. |

Exact and normalized question texts are disjoint across the splits. Known concepts occur in both training and testing: this evaluates wording generalization and coverage handling, not the acquisition of entirely unseen concepts. The unlisted terms are disjoint across training, validation, and testing.

The six known test concepts are LoRA, QLoRA, Token, Learning rate, Epoch, and MCP. Unlisted test terms are DPO, RoPE, FlashAttention, MoE, KV cache, and speculative decoding. Here **unlisted** means absent as an entry in this course glossary. A model may know a real-world definition and still violate the task's coverage rule by answering without requesting review.

The neural model answers **closed book**: its input contains only the shared system instruction and the question. It does not receive glossary definitions, reference answers, term IDs, or per-question coverage labels. The reference answers and expected review flags remain in a separate [gold file](advanced/gold.json).

Implementation: [Colab notebook](../../notebooks/lora_glossary_advanced.ipynb), [data/scoring/lookup helper](advanced/advanced_glossary.py), [test questions](advanced/test.jsonl), [data manifest](advanced/manifest.json).

### Fixed training settings

The model and revision, unquantized float32 base weights, rank, alpha, learning rate, and seed were retained from the course. The first experiment used **3 epochs** instead of the FAQ experiment's 20 because its training set is larger (124 versus 14 records). With batch size 4 and gradient accumulation 2, this produced 48 updates. Maximum generation length was increased from 96 to 192 tokens to accommodate glossary definitions.

| Setting or measurement | Value |
|---|---:|
| LoRA rank / alpha | 16 / 32 |
| Learning rate / seed | 0.0002 / 42 |
| Epochs / optimizer updates | 3 / 48 |
| Trainable parameter fraction, from the console | 0.8421% |
| Maximum measured train/validation record length | 237 tokens, below the 512-token limit |
| Training time | 205.98 seconds |
| Average training loss over the run | 0.763707 |
| Last logged training loss | 0.358351 |
| Validation loss after training | 0.382231 |

The logged training loss decreased from 2.396908 at step 4 to 0.358351 at step 48. The last logged loss describes a logging window; it is not the same quantity as the average loss over the whole run. Validation was performed after training, with no checkpoint selection or hyperparameter search against the test set.

A bookkeeping bug in the token-length check initially counted the fields of a tokenizer return dictionary. Before training, it was corrected by setting `return_dict=false` in `apply_chat_template`; the measured maximum was then 237. The correction did not change the evaluation prompts or model outputs. The GitHub notebook contains the corrected check.

Evidence: [training metrics](results/advanced/training.json), [training log](results/advanced/training_log.json), [console summary](results/advanced/training_console_summary.json).

### Evaluation and results

The same 18 questions, system instruction, greedy generation parameters, and precision were used before and after training. A strict format check requires exactly `answer` as a string and `needs_review` as a boolean. Content scoring checks the review flag and case-insensitive groups of keywords. These are **keyword-based task scores**, not a complete assessment of factual correctness.

The comparison system is a simple lexical glossary lookup: it matches whole normalized term names or aliases, returns the longest matching entry's definition, and requests review if no entry matches. It has direct access to the glossary. This is a different information-access strategy from the neural model's closed-book answering, and is not a full semantic retrieval or RAG system.

| Metric | Before LoRA | After LoRA | Lexical lookup |
|---|---:|---:|---:|
| Format pass | 18/18 (100%) | 18/18 (100%) | 18/18 (100%) |
| Keyword content pass | 5/18 (27.78%) | 7/18 (38.89%) | 15/18 (83.33%) |
| Named-term questions | 1/6 | 3/6 | 6/6 |
| Paraphrased questions | 4/6 | 4/6 | 3/6 |
| Unlisted-term questions | 0/6 | 0/6 | 6/6 |
| Evaluation time for 18 questions | 69.35 s | 69.41 s | 0.06 s |

Four questions improved under the fixed automatic scorer and two regressed, for a net gain of two questions (11.11 percentage points). Format compliance was already 100%, so this run provides no measured format gain. All six unlisted terms still received `needs_review=false` after training.

The automatic regressions were:

- “How does Quantized LoRA reduce the memory needed for adaptation?”
- “What does the Model Context Protocol standardize between AI applications and external systems?”

These are regressions under the automatic scoring rule. They should not be described as transitions from factually correct answers to incorrect answers without inspecting the original text.

Evidence: [full result](results/advanced/result.json), [before outputs](results/advanced/eval_before.json), [after outputs](results/advanced/eval_after.json), [lookup outputs](results/advanced/eval_retrieval.json).

### AI-assisted inspection of actual answers

- **Clear improvement: Epoch.** Before training, the model used a generic time-period/astronomy meaning. Afterward, it correctly described one pass through the entire training dataset and the risk of too many epochs.
- **Keyword false positive: LoRA.** Both before and after answers to the frozen-weights question claimed that the low-rank matrices are fixed. The correct mechanism freezes pretrained base weights and trains the added low-rank matrices. Both incorrect answers still matched the scorer's keywords. See the [LoRA paper](https://arxiv.org/abs/2106.09685).
- **Another false positive: QLoRA.** The before answer to the memory question said the adapter weights are quantized; QLoRA's central mechanism uses a frozen, quantized base model and trains LoRA adapters. Thus the automatic regression on this question is not evidence that its before answer was semantically correct. See the [QLoRA paper](https://arxiv.org/abs/2305.14314).
- **Keyword false negative: Learning rate.** Before training, the question asking which setting controls update size received “Learning Rate.” That directly answers the question, but the scorer required keywords from a full definition and marked it wrong.
- **Unsupported additions remain.** Several after-training answers add Pydantic AI-specific claims absent from the glossary, or repetitive statements such as the MCP answer's repeated “LLM to the LLM.” A useful first sentence does not make the entire answer reliable.
- **Coverage failure: DPO and the other unlisted terms.** The model continues providing definitions with `needs_review=false`; the task requires a review request because the source glossary has no entry. This conclusion does not depend on evaluating the real-world correctness of each definition.

The [complete AI-assisted review](results/advanced/manual_review_assisted.md) records qualitative judgments for every test question separately from the automatic scores. No additional manual accuracy percentage is claimed. The original exported files are preserved unchanged.

### Fine-tuning compared with searching the glossary

For this particular source-based definition task, direct lookup produced the stronger overall keyword score, returned stored definitions, and enforced the coverage rule for all six unlisted test terms. Its content can be updated by editing the glossary rather than retraining a model. Its JSON format is constructed by code, so its 100% format score is not a learned model capability.

Lookup also has a clear weakness: it needs recognizable names or aliases. For the implicit Token question, it matched the incidental word “API” and returned the wrong entry. It missed the Learning rate and Epoch paraphrases and incorrectly requested review. More aliases or semantic retrieval might help, but they were not evaluated here.

Fine-tuning can be useful for output conventions, tone, and recurring task behavior, and can sometimes handle language variation without supplying a source document at inference. In this run, the Epoch definition improved, but many answers still mixed correct ideas with unsupported claims, and the coverage behavior did not improve. It would therefore be inappropriate to use this adapter as a reliable store of the course glossary without further evaluation. For definitions that require traceability, frequent updates, or clear source coverage, a lookup/retrieval design is a better fit for the observed needs.

The observed times show the cost difference in this small run, not a general serving benchmark: the neural systems and the lexical program have different computational workloads, and model-loading time is not included in those evaluation times.

### Limitations and conclusion

This is one fixed, short training run on a small dataset and 18 test questions. Known concepts are shared across training and testing, the glossary itself is a draft, and keyword matching has both false positives and false negatives. The lookup system has direct source access while the neural model is closed book. These choices must be considered when comparing the results.

The run does not isolate whether the limited benefit comes primarily from the model, training duration, data composition, or task design. More controlled experiments would be needed to identify the cause. Lower training and validation loss alone does not establish factual accuracy, coverage awareness, or the presence of overfitting.

Under these conditions, LoRA improved the automatic content score modestly, while format compliance stayed unchanged and all unlisted-term review decisions remained wrong. The main practical lesson is to inspect actual answers and evidence boundaries alongside aggregate metrics, and to choose fine-tuning or retrieval according to the behavior and source requirements of the task.

### Personal execution and AI assistance

I personally ran the original FAQ notebook and the Advanced Colab experiment, including training, before/after evaluation, and result export. I supplied the outputs and the exported result files for checking.

Codex assisted with data generation, evaluation-question and scoring design, notebook implementation, a token-length-check correction, file consistency checks, semantic comparison of the answers, and report drafting. The answer-level judgments above are explicitly AI-assisted; they are not presented as an independent unaided student assessment.
