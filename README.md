# Mercury MCP: Cross-Architecture LLM Internal Observation, as Agent Tools

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20352085.svg)](https://doi.org/10.5281/zenodo.20352085)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


> "Most AI coding agents don't know what's inside the model they're talking to. Mercury does."

Mercury MCP exposes a 23-LLM cross-architecture observation database to any agent that speaks the [Model Context Protocol](https://modelcontextprotocol.io/) (Claude Code, Cursor, Cline, Goose, etc.).

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
23-LLM cross-architecture survey across 13 architecture families, two observation tiers per model.

Tier-A (output-layer logit hooks): cheap, fast, candidate-signal screening. May surface artifacts from shared tokenization (vocab-id mod hidden_size collisions). Useful as hypothesis-generating layer.

Tier-B (HF output_hidden_states across all layers): the actual finding layer. Per-layer residual stream fingerprints. Cross-architecture functional layer alignment qwen-7B L15 to falcon-7B L16 reaches 0.868 similarity. 54/84 model-pairs aligned at the middle layers (50-60% depth).

Earlier "dim 11 universal across families" claim from Tier-A is being re-framed as candidate signal, not validated residual stream feature. Working through this in Paper A draft.

### For LLM application developers
Stop guessing which model to fine-tune. Mercury tells you structurally which layers carry which capability and which models' middle layers are functionally interchangeable.

### For Frankenstein / model-merge people
Cross-architecture per-layer alignment matrix included (12 Tier-B models, 84 pairwise). Strongest single match: qwen-7B L15 to falcon-7B L16 at 0.868 similarity. mistral / yi / gemma occupy alternative residual subspace, possible non-interfering composition substrate.

---

## Install (3 lines)

```bash
git clone https://github.com/norika1207-lab/mercury-mcp
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

## The 23 models in v0.1 (13 architecture families)

| Family | Models | Tier-B done |
|---|---|---|
| qwen2 | 3B, 7B, 14B, 32B, coder-32B | 3B, 7B, 14B ✓ |
| qwen2-distill (DeepSeek-R1) | 7B, 32B, 70B | 7B ✓ |
| llama | 3.1-8B, 3.3-70B | pending |
| phi3 | medium-14B | ✓ |
| falcon3 | 7B | ✓ |
| internlm2 | 7B | running |
| mistral | 7B-v0.3, small-3.2-24B | 7B ✓ |
| olmo2 | 7B (AllenAI fully-open) | ✓ |
| gemma2 | 9B | ✓ |
| granite | 3.1-dense-8B (IBM) | ✓ |
| yi | 1.5-9B | ✓ |
| starcoder2 | 15B | pending |
| codestral | 22B (mistral coder variant) | pending |
| command-r | 35B (Cohere) | pending |

Tier-A all 23 done. Tier-B 12 of 23 done, rest in progress.

---

## Findings (still evolving, see Paper A draft for current framing)

1. Cross-architecture per-layer functional alignment. qwen-7B L15 to falcon-7B L16 reaches sim 0.868. 54 of 84 pairwise comparisons show sim above 0.7 at middle layers (50-60% depth). This is the strongest finding right now. Comes from Tier-B (residual stream level), so not vulnerable to tokenizer artifact critique.

2. Distillation appears to transplant anchor structure. DeepSeek-R1:70b uses a llama base but Tier-A anchor structure aligns with qwen at 44.7x random baseline. Note this is Tier-A so caveats apply (see point 4), but the magnitude is hard to dismiss as pure vocab artifact at 44.7x.

3. Three families show alternative residual stream geometry. mistral-7B, mistral-small, yi-1.5 all show 0/11 qwen-anchor presence in Tier-A and structurally different hot dims in Tier-B. They occupy a different subspace, possible substrate for non-interfering cross-architecture composition.

4. Methodology caveat being worked through openly. Tier-A "dim 11 universal across families" (originally framed as residual stream feature) may be a vocab-token-id mod hidden_size collision artifact from shared tokenizer training. Tier-B on OLMo2 contradicts the Tier-A reading. Paper A is being re-framed with Tier-A as screening layer (candidate signals) and Tier-B as finding layer (validated residual stream observations). Discussion welcome.

Full data + analysis: see [`anchor-survival-MASTER.txt`](https://github.com/norika1207-lab/mercury-paper-handoff/blob/main/anchor-survival-MASTER.txt) and the [`mercury-paper-handoff`](https://github.com/norika1207-lab/mercury-paper-handoff) repo.

---

## Tool reference

| Tool | Purpose |
|---|---|
| `mercury_list_models` | List all 23 observed models |
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
- **Source code**: [paper-handoff `paper-G-composable-llm/tools/`](https://github.com/norika1207-lab/mercury-paper-handoff)

Reproducibility: ~4 hours wall-clock per model on a Mac mini M4 Pro. No GPU required.

---

## Cite

```bibtex
@dataset{oda_mercury_2026,
  author = {Chen, Ho Yiing (norika)},
  title  = {Mercury: Cross-Architecture Hot-Dim Geometry Database for 23 LLMs},
  year   = {2026},
  doi    = {10.5281/zenodo.20352085},
  url    = {https://github.com/norika1207-lab/mercury-mcp}
}
```

---

## License

MIT for code. Data CC-BY-4.0.

---

## Author

norika (Chen Ho Yiing), Taiwan independent researcher.

- ORCID: [0009-0006-6816-9891](https://orcid.org/0009-0006-6816-9891)
- Google Scholar: [wrTR3VMAAAAJ](https://scholar.google.com/citations?user=wrTR3VMAAAAJ)
- GitHub: [@norika1207-lab](https://github.com/norika1207-lab)

Built solo, no institutional affiliation, no grant, no GPU. Just curiosity and stubborn nights.
