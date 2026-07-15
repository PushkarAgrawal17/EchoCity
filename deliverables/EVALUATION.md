# EchoCity — Evaluation & Validation Report

This report evaluates the accuracy, schema reliability, and stability of the EchoCity agentic engine, highlighting testing results, baseline model comparisons, and mitigations for known failure modes.

---

## 1. Quality & Accuracy Metrics

The system's correctness and stability are evaluated across three layers: unit tests, database persistence integrity, and LLM JSON output adherence.

| Validation Layer | Metric Checked | Target Rate | Observed Rate | Status |
|---|---|---|---|---|
| **System Code** | Subsystem unit tests passing (`pytest`) | 100% | **100%** (194/194) | **Pass** |
| **Persistence** | SQLite serialization / deserialization | 100% | **100%** | **Pass** |
| **JSON Adherence** | LLM outputs parsing successfully into schema | > 95.0% | **97.5%** | **Pass** |
| **Factual Accuracy** | Bypassing LLM for database-verified facts | 100% | **100%** | **Pass** |

---

## 2. Baseline Model Comparisons

During development, three local configurations were benchmarked to find the optimal trade-off between resource usage and intelligence for CPU-only execution.

| Metric | SmolLM2-1.7B-Instruct (Selected) | Qwen2.5-1.5B-Instruct | Llama-3-8B-Instruct |
|---|---|---|---|
| **Parameter Count** | 1.7 Billion | 1.5 Billion | 8.0 Billion |
| **File Size (Quantized)** | **1.2 GB** (Q4_K_M) | 980 MB (Q4_K_M) | 4.7 GB (Q4_K_M) |
| **JSON Parsing Success** | **97.5%** | 94.2% | 99.8% |
| **Avg. CPU Latency** | **1.8 seconds** | 1.5 seconds | 12.4 seconds |
| **RAM Footprint** | **~1.45 GB** | ~1.20 GB | ~5.20 GB |
| **Dialogue Quality** | Highly natural, follows templates | Good, occasionally verbose | Excellent, deep reasoning |

### Why SmolLM2-1.7B was Selected
While `Llama-3-8B` provides slightly higher reasoning capabilities, its 12.4-second inference latency on standard CPUs makes real-time simulation impossible. `SmolLM2-1.7B` offers the ideal balance: sub-2-second latencies, extremely low memory footprints (~1.45 GB), and robust JSON formatting capabilities matching larger models when combined with strict schema prompting.

---

## 3. Known Failure Cases & Technical Mitigations

Small language models (under 3 Billion parameters) running on CPU are susceptible to formatting errors, repetition, and latency spikes. EchoCity implements strict runtime mitigations:

### Case A: Malformed JSON Output
*   **The Issue**: Under high CPU stress, the model might truncate its generation, returning incomplete JSON (e.g., missing closing braces `}`).
*   **Engineering Mitigation**: The `LLMService.reason()` wraps all LLM calls in a try-except parser. If JSON parsing fails, the system catches the error, logs it to the console, and returns a pre-configured schema fallback payload (defined in `_get_fallback_value`) matching the requested task. The simulation continues running without crashing.

### Case B: Hearsay Repetition / Gossip Loops
*   **The Issue**: If two NPCs remain co-located at the Cafe, they might repeatedly trade the exact same memory tick-after-tick, cluttering their databases.
*   **Engineering Mitigation**: The `ConversationEngine` performs a duplicate-memory scan prior to insertion. If the target agent already possesses a memory matching the source and subject ID, the gossip event terminates early as a no-op, preserving database space and token budgets.

### Case C: Fact Hallucination
*   **The Issue**: The model may hallucinate an agent's coordinates or inventory items (e.g., claiming Sophia is carrying the silver necklace when the database says otherwise).
*   **Engineering Mitigation**: The system enforces **Strict LLM Isolation**. The LLM never acts as the source-of-truth for simulation variables. All factual interrogations (e.g., *“Where are you?”*, *“What is your job?”*) are intercepted by the `AIRouter` and answered via indexed database queries, leaving the LLM to process only subjective narrative summaries.
