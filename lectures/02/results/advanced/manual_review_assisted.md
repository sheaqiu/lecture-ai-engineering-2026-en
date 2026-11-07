# AI-assisted per-question review

Student executed the experiments and exported files. The semantic judgments in this file are AI-assisted, not claimed as independent student judgments.

These judgments compare the complete answer with the course glossary and the stated coverage policy. They are separate from the fixed keyword scorer. Partial means a useful core idea is mixed with unsupported or misleading content. No manual accuracy percentage is reported.

| Question ID | Before | After | Lookup | Review note |
|---|---|---|---|---|
| known_term/lora | partial | incorrect | correct | Before: incomplete mechanism. After: invents saving the best weights and unrelated course/model names; does not explain frozen base weights and learned low-rank updates. |
| paraphrase/lora | incorrect | incorrect | correct | Both neural answers reverse what is frozen. Both nevertheless pass the keyword rule. LoRA freezes pretrained base weights and trains the added low-rank matrices. |
| known_term/qlora | incorrect | incorrect | correct | Before: expands QLoRA as Quantum LoRA. After: describes selecting useful parameters and reducing learning rate rather than quantizing the base model. |
| paraphrase/qlora | incorrect | incorrect | correct | Before incorrectly quantizes adapter weights; after confuses 4/8-bit precision with the number of trainable parameters. The automatic regression is not a transition from a semantically correct answer. |
| known_term/token | incorrect | partial | correct | Before uses a financial meaning. After correctly starts with a unit of text but adds unsupported Pydantic AI behavior and a configuration name. |
| paraphrase/token | incorrect | incorrect | incorrect | Before calls the pieces token counts or token limits and adds unrelated API details. After repeats the question and invents payload details without clearly naming tokens. Lookup chooses API instead of Token. |
| known_term/learning-rate | partial | partial | correct | Both identify parameter update size. Before incorrectly equates lr=0.01 with a fixed 1% weight change; after replaces the glossary warning about instability with an unsupported overfitting claim. |
| paraphrase/learning-rate | correct | partial | incorrect | Before correctly names Learning Rate, which answers the question, but fails a definition-based keyword rule. After adds a definition and an unsupported overfitting claim. Lookup misses the implicit term and wrongly abstains. |
| known_term/epoch | incorrect | correct | correct | Before uses a generic time-period/astronomy meaning. After correctly describes a full pass over the training dataset and the risk of too many epochs. |
| paraphrase/epoch | incorrect | partial | incorrect | Before answers Training set. After identifies epoch but adds unsupported Pydantic AI version-specific naming. Lookup misses the implicit term and wrongly abstains. |
| known_term/mcp | incorrect | partial | correct | Before describes embedding LLMs rather than the protocol connecting tools/data. After starts closer to the glossary but ends with repetitive unsupported LLM-to-LLM wording. |
| paraphrase/mcp | partial | incorrect | correct | Before is vague about context exchange; after incorrectly suggests deterministic matching inputs/outputs across tools. Neither should be treated as fully correct solely because of a keyword score. |
| absent_term/01 | coverage_violation | coverage_violation | correct | The term is absent from this course glossary. Both neural answers set needs_review=false; the task requires true regardless of any real-world definition. Lookup correctly abstains. |
| absent_term/02 | coverage_violation | coverage_violation | correct | The term is absent from this course glossary. Both neural answers set needs_review=false; the task requires true regardless of any real-world definition. Lookup correctly abstains. |
| absent_term/03 | coverage_violation | coverage_violation | correct | The term is absent from this course glossary. Both neural answers set needs_review=false; the task requires true regardless of any real-world definition. Lookup correctly abstains. |
| absent_term/04 | coverage_violation | coverage_violation | correct | The term is absent from this course glossary. Both neural answers set needs_review=false; the task requires true regardless of any real-world definition. Lookup correctly abstains. |
| absent_term/05 | coverage_violation | coverage_violation | correct | The term is absent from this course glossary. Both neural answers set needs_review=false; the task requires true regardless of any real-world definition. Lookup correctly abstains. |
| absent_term/06 | coverage_violation | coverage_violation | correct | The term is absent from this course glossary. Both neural answers set needs_review=false; the task requires true regardless of any real-world definition. Lookup correctly abstains. |

## References

- [Course glossary used in the experiment](../../advanced/glossary.json)
- [Raw before answers](eval_before.json)
- [Raw after answers](eval_after.json)
- [Raw lookup answers](eval_retrieval.json)
- [LoRA original paper](https://arxiv.org/abs/2106.09685)
- [QLoRA original paper](https://arxiv.org/abs/2305.14314)
