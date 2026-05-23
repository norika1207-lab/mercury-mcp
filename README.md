# Mercury MCP — Cross-Architecture LLM Internal Observation, as Agent Tools

> "Most AI coding agents don't know what's inside the model they're talking to. Mercury does."

Mercury MCP exposes a **18-LLM cross-architecture observation database** to any agent that speaks the [Model Context Protocol](https://modelcontextprotocol.io/) — Claude Code, Cursor, Cline, Goose, etc.

Built entirely on consumer hardware (one Mac mini + one NVIDIA DGX Spark) at near-zero compute cost.

---

## What it answers

Try these prompts with any MCP-aware agent after installing:

- *"What hidden dimensions are universally hot across LLM families?"*
- *"In qwen-7B, which layer has the same functional fingerprint as falcon-7B layer 16?"*
- *"Compose a layer recipe for a Chinese-writing + reasoning hybrid model."*
- *"Show me OLMo2's anchor dimensions and how they overlap with the qwen anchor set."*

The agent calls Mercury MCP tools; Mercury answers from precomputed observation data.

---

## Why this matters

### For mech interp researchers
First public 18-LLM cross-architecture survey with reproducible per-cell, per-layer observations. Anchor universality hypothesis (Olah et al.) gets large-scale empirical evidence: **dim 11 appears in top-50 hot dims of 11/18 models across 5 architecture families** including the fully-independent OLMo2.

### For LLM application developers
Stop guessing which model to fine-tune. Mercury tells you *structurally* which model carries which capability — and which models' layers are functionally interchangeable.

### For Frankenstein / model-merge people
Cross-architecture layer alignment matrix included. Strongest single match: **qwen-7B L15 ↔ falcon-7B L16 = 0.868 similarity** (different vendors, completely different lineages).

---

## Install (3 lines)

```bash
git clone https://github.com/norikaoda/mercury-mcp
cd mercury-mcp
pip install -e .
```

Then add to your MCP client config:

```jsonc
// ~/.claude/mcp_settings.json  (Claude Code)
{
  "mcpServers": {
    "mercury": {
      "command": "python",
      "args": ["-m", "mercury_mcp.server"]
    }
  }
}
```

Restart your agent. You now have 7 new tools: `mercury_list_models`, `mercury_anchor_dims`, `mercury_universal_anchors`, `mercury_layer_fingerprint`, `mercury_cross_arch_equivalent`, `mercury_compose_recipe`, `mercury_about`.

---

## The 18 models in v0.1

| Family | Models | Tier-B available |
|---|---|---|
| qwen2 | 3B, 7B, 14B, 32B, coder-32B | 3B, 7B, 14B ✓ |
| qwen2-distill (DeepSeek-R1) | 7B, 32B, **70B** | 7B ✓ |
| llama | 3.1-8B, 3.3-70B | (pending) |
| phi3 | medium-14B | ✓ |
| falcon3 | 7B | ✓ |
| internlm2 | 7B | (pending) |
| mistral | 7B-v0.3, small-3.2-24B | 7B ✓ |
| **olmo2** | **7B (AllenAI fully-open)** | (pending) |
| gemma2 | 9B | (pending) |
| granite | 3.1-dense-8B (IBM) | (pending) |
| yi | 1.5-9B | (pending) |

Tier-A = output-layer logit observation (cheap, all 18 done).
Tier-B = per-layer HF `output_hidden_states` observation (rich, 7 done, 5 in progress).

---

## Headline findings (paper-grade)

1. **Universal anchors are real.** dim 11 (top-50) in 11/18 models including AllenAI's OLMo2 — completely independent lineage. Probability of random co-occurrence ≈ 0.
2. **Distillation transplants anchor structure.** DeepSeek-R1:70b uses a llama base but shows qwen-anchor presence at 44.7× random — anchors survive distillation, suggesting they're a fingerprint for model lineage detection.
3. **Cross-architecture layer alignment exists.** qwen-7B L15 ≈ falcon-7B L16 (sim 0.868) by per-layer functional fingerprint. Middle layers (~50% depth) are most universally aligned across families.
4. **Three families show alternative geometry.** mistral-7B, mistral-small, yi-1.5 all show 0/11 qwen-anchor presence — they occupy a different residual subspace. This opens the door to *non-interfering cross-architecture composition* (Frankenstein).

Full data + analysis: see [`anchor-survival-MASTER.txt`](./data/anchor-survival-MASTER.txt) and the [`paper-handoffs/`](https://github.com/norikaoda/mercury-paper-handoff) repo.

---

## Tool reference

| Tool | Purpose |
|---|---|
| `mercury_list_models` | List all 18 observed models |
| `mercury_anchor_dims(model, top_k=50)` | This model's hot dims + qwen-anchor overlap analysis |
| `mercury_universal_anchors(min_models=3)` | Cross-model universal anchor presence ranking |
| `mercury_layer_fingerprint(model, layer)` | Per-layer functional fingerprint (Tier-B only) |
| `mercury_cross_arch_equivalent(model, layer, top_k=5)` | Find functionally-similar layers in OTHER models |
| `mercury_compose_recipe(capabilities)` | Generate composable layer recipe for given capabilities |
| `mercury_about` | Paper status, citations, contribution info |

---

## How the data was collected

- **Observation protocol**: 10 multilingual prompts per model, ~60 tokens each, greedy decoding
- **Tier-A**: hooked into `llama_cpp.Llama.logits_processor` to capture output-layer hot dims per token
- **Tier-B**: `transformers.AutoModelForCausalLM.from_pretrained` with `output_hidden_states=True`, per-layer residual stream activation magnitudes binned into 10 quantiles
- **Cell grid scheme**: addressable `(layer, dim, quantile_idx)` mmap-able binary, ~24MB-840MB depending on model size
- **Source code**: [paper-handoff `paper-G-composable-llm/tools/`](https://github.com/norikaoda/mercury-paper-handoff)

Reproducibility: ~4 hours wall-clock per model on a Mac mini M4 Pro. No GPU required.

---

## Cite

```bibtex
@dataset{oda_mercury_2026,
  author = {Chen, Ho Yiing (norika)},
  title  = {Mercury: Cross-Architecture Hot-Dim Geometry Database for 18 LLMs},
  year   = {2026},
  doi    = {10.5281/zenodo.XXXXXXX},
  url    = {https://github.com/norikaoda/mercury-mcp}
}
```

---

## License

MIT for code. Data CC-BY-4.0.

---

## Author

norika (Chen Ho Yiing), Taiwan independent researcher.
ORCID: [0009-0006-6816-9891](https://orcid.org/0009-0006-6816-9891)
Built solo, no institutional affiliation, no grant, no GPU. Just curiosity and stubborn nights.
