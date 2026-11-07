"""Advanced glossary experiment: standard-library-only data and evaluation helpers."""

import json
import re
import time

ABSTAIN = "This term is not covered by the course glossary. Confirmation is needed."
SYSTEM = (
    "You answer questions for the AIE2026 course glossary. "
    "Use the course glossary definitions learned during fine-tuning. "
    "Always return exactly one JSON object with exactly two keys: "
    '\"answer\" (string) and \"needs_review\" (boolean). '
    "For a term covered by the course glossary, give its definition and set needs_review to false. "
    "For a term not covered by the course glossary, answer "
    f"'{ABSTAIN}' and set needs_review to true. "
    "Do not add Markdown fences or any text outside the JSON object."
)

# These questions and keyword rules are fixed before model training.
# Keyword matches are a proxy; manually review the exported original answers too.
KNOWN = [
    ("lora", "LoRA", "With Low-Rank Adaptation, which weights stay fixed and which parameters are trained?",
     [["freez", "fixed"], ["low-rank", "low rank"], ["matri"]]),
    ("qlora", "QLoRA", "How does Quantized LoRA reduce the memory needed for adaptation?",
     [["quantiz"], ["4-bit", "4 bits", "four bit"], ["LoRA"]]),
    ("token", "Token", "What are the small pieces of text used to count an LLM's input length and API charges?",
     [["text", "word", "character"], ["unit", "piece", "fragment", "segment", "subword"]]),
    ("learning-rate", "Learning rate", "Which training setting controls how far model parameters move in a single update?",
     [["parameter", "weight"], ["update", "step", "move"], ["size", "far", "magnitude", "scale", "amount"]]),
    ("epoch", "Epoch", "What do we call one complete pass through every training example?",
     [["pass"], ["training", "dataset", "data"], ["one", "once", "entire", "full"]]),
    ("mcp", "MCP (Model Context Protocol)", "What does the Model Context Protocol standardize between AI applications and external systems?",
     [["protocol"], ["tool", "data"], ["connect", "communicat", "standard"]]),
]

TRAIN_ABSENT = [
    "Batch normalization", "Dropout", "Stochastic gradient descent (SGD)",
    "Convolutional neural network (CNN)", "Long short-term memory (LSTM)",
    "Beam search", "BLEU", "ROUGE",
]
VALID_ABSENT = ["Cross-entropy loss", "Perplexity", "Top-k sampling", "Top-p sampling"]
TEST_ABSENT = [
    "Direct Preference Optimization (DPO)", "Rotary Position Embedding (RoPE)",
    "FlashAttention", "Mixture of Experts (MoE)", "KV cache", "Speculative decoding",
]


def normalize(text):
    return " ".join(re.findall(r"[a-z0-9]+", text.casefold()))


def messages(question):
    # No glossary definitions, term IDs, or question-specific coverage labels enter the prompt.
    # The shared policy includes the same abstention wording for every question.
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]


def target(answer, needs_review):
    return json.dumps({"answer": answer, "needs_review": needs_review}, ensure_ascii=False)


def training_record(question, answer, needs_review):
    return {"messages": messages(question) + [{"role": "assistant", "content": target(answer, needs_review)}]}


def make_materials(glossary, raw_records):
    terms = {term["id"]: term for term in glossary["terms"]}
    expected_raw = [
        {"messages": [{"role": "user", "content": question},
                      {"role": "assistant", "content": term["definition"]}]}
        for term in glossary["terms"]
        for question in [f"What is {term['term']}?", f"Briefly explain {term['term']}."]
    ]
    assert raw_records == expected_raw, "Raw data differs from the course script output."
    names = {normalize(name) for term in terms.values() for name in [term["term"], *term.get("aliases", [])]}
    absent = TRAIN_ABSENT + VALID_ABSENT + TEST_ABSENT
    assert len(set(map(normalize, absent))) == len(absent)
    assert all(normalize(name) not in names for name in absent)

    train = [training_record(row["messages"][0]["content"], row["messages"][1]["content"], False)
             for row in raw_records]
    train += [training_record(f"What is {name}?", ABSTAIN, True) for name in TRAIN_ABSENT]
    valid_ids = [row[0] for row in KNOWN] + ["fine-tuning", "sft"]
    valid = [training_record(f"In simple words, explain {terms[key]['term']}.", terms[key]["definition"], False)
             for key in valid_ids]
    valid += [training_record(f"In simple words, explain {name}.", ABSTAIN, True) for name in VALID_ABSENT]

    test, gold = [], {}
    for key, name, paraphrase, keywords in KNOWN:
        for category, question in [("known_term", f"Give a definition of {name}."), ("paraphrase", paraphrase)]:
            item_id = f"{category}/{key}"
            test.append({"id": item_id, "category": category, "question": question})
            gold[item_id] = {"term_id": key, "needs_review": False,
                             "reference_answer": terms[key]["definition"], "keyword_groups": keywords}
    for i, name in enumerate(TEST_ABSENT, 1):
        item_id = f"absent_term/{i:02d}"
        test.append({"id": item_id, "category": "absent_term", "question": f"Give a definition of {name}."})
        gold[item_id] = {"term_id": None, "needs_review": True, "reference_answer": ABSTAIN,
                         "keyword_groups": [["glossary"], ["not covered", "not in", "absent", "unlisted", "outside"]]}

    all_questions = ([row["messages"][1]["content"] for row in train + valid] +
                     [row["question"] for row in test])
    assert len(set(map(normalize, all_questions))) == len(all_questions), "Question overlap across splits."
    assert len(train) == 124 and len(valid) == 12 and len(test) == 18
    for entry in gold.values():
        assert score_content(json.loads(target(entry["reference_answer"], entry["needs_review"])), entry)
    return {"train": train, "valid": valid, "test": test, "gold": gold}


def check_format(raw):
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError):
        return False, "json_error", None
    if not isinstance(obj, dict):
        return False, "not_object", obj
    if set(obj) != {"answer", "needs_review"}:
        return False, "keys", obj
    if not isinstance(obj["answer"], str) or not isinstance(obj["needs_review"], bool):
        return False, "wrong_type", obj
    return True, "", obj


def score_content(obj, entry):
    if not isinstance(obj, dict) or not isinstance(obj.get("answer"), str):
        return False
    if not isinstance(obj.get("needs_review"), bool) or obj["needs_review"] != entry["needs_review"]:
        return False
    answer = normalize(obj["answer"])
    return all(any(normalize(keyword) in answer for keyword in group) for group in entry["keyword_groups"])


def score_answer(raw, entry):
    format_ok, reason, obj = check_format(raw)
    loose = obj
    if obj is None:
        match = re.search(r"\{.*\}", raw, re.S)
        try:
            loose = json.loads(match.group()) if match else None
        except ValueError:
            loose = None
    content_ok = score_content(loose, entry)
    return {"raw": raw, "format_ok": format_ok, "format_reason": reason, "content_ok": content_ok,
            "both_ok": format_ok and content_ok,
            "predicted_needs_review": loose.get("needs_review") if isinstance(loose, dict) and isinstance(loose.get("needs_review"), bool) else None}


def summarize(rows):
    def rates(items):
        n = len(items)
        return {"n": n, **{metric: sum(row[flag] for row in items) / n
                            for metric, flag in [("format_rate", "format_ok"), ("content_rate", "content_ok"), ("both_rate", "both_ok")]}}
    result = rates(rows)
    result["by_category"] = {category: rates([row for row in rows if row["category"] == category])
                             for category in sorted({row["category"] for row in rows})}
    absent = [row for row in rows if row["category"] == "absent_term"]
    result["absent_assertions"] = sum(row["predicted_needs_review"] is False for row in absent)
    result["absent_unparseable_review_flags"] = sum(row["predicted_needs_review"] is None for row in absent)
    return result


def evaluate(answer_fn, test, gold, label, work):
    start, rows = time.perf_counter(), []
    for i, example in enumerate(test, 1):
        # Only the question is supplied to the answering system.
        raw = answer_fn(example["question"])
        row = {**example, **score_answer(raw, gold[example["id"]]),
               "gold_needs_review": gold[example["id"]]["needs_review"]}
        rows.append(row)
        print(f"{label}: {i}/{len(test)}", flush=True)
    summary = {"label": label, **summarize(rows), "seconds": round(time.perf_counter() - start, 2)}
    (work / f"eval_{label}.json").write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary, rows


def lookup_answer(question, glossary):
    """Simple baseline: longest whole term/alias match; return stored definition."""
    query = f" {normalize(question)} "
    candidates = []
    for term in glossary["terms"]:
        for name in [term["term"], *term.get("aliases", [])]:
            key = normalize(name)
            if len(key) >= 3 and f" {key} " in query:
                candidates.append((len(key), term["id"], term["definition"]))
    if not candidates:
        return target(ABSTAIN, True)
    candidates.sort(key=lambda item: (-item[0], item[1]))
    return target(candidates[0][2], False)
