# Launch posts — Mercury MCP v0.1

**Status:** drafts for review. Edit, then send.

---

## 1. Hacker News (Show HN)

**Title** (keep under 80 chars, no emoji per HN style):

```
Show HN: Mercury MCP – I scanned 23 LLMs' internal structure on a Mac mini
```

**Body** (paste into the URL/Text box):

```
Mercury MCP is a Model Context Protocol server that exposes a 23-LLM cross-architecture observation database to any agent (Claude Code, Cursor, Cline, Goose).

Built solo on consumer hardware: one Mac mini M4 Pro + one NVIDIA DGX Spark. Total compute cost ≈ $0 (all observations done on hardware I already had).

Headline findings:

1. **dim 11 appears in top-50 hot dims of 11/18 models** across qwen / llama / phi3 / falcon / olmo2 families. Including AllenAI's OLMo2, which has zero shared training lineage with any other model in the survey. This is large-scale empirical evidence for the anchor universality hypothesis (Olah et al., 2020).

2. **DeepSeek-R1:70b** uses a llama base but shows qwen-anchor presence at 44.7× hypergeometric random baseline. Anchors survive distillation — opens model-lineage fingerprinting as a forensic technique.

3. **Cross-architecture layer alignment is measurable.** qwen-7B layer 15 ≈ falcon-7B layer 16 at 0.868 fingerprint similarity. Middle layers (~50% depth) are most universally aligned across families.

4. **Three families show alternative residual stream geometry.** mistral-7B, mistral-small-24B, yi-1.5-9B all show 0/11 qwen-anchor presence — they occupy a different subspace. This opens cross-architecture non-interfering composition (Frankenstein-style merges).

The MCP server exposes 7 tools:
- mercury_list_models
- mercury_anchor_dims
- mercury_universal_anchors
- mercury_layer_fingerprint
- mercury_cross_arch_equivalent
- mercury_compose_recipe (Paper G "composable LLMs" vision — layer-recipe blueprint)
- mercury_about

Example: ask your agent "find layers in OTHER models that functionally match qwen-7B layer 15" — it calls mercury_cross_arch_equivalent and gets back the top-K candidates with similarity scores.

Why this matters: most coding agents have no architectural awareness of the model they're talking to. Mercury is a small step toward changing that — make LLM internal structure queryable infrastructure, not research-paper trivia.

Code, data, install instructions:
https://github.com/norika1207-lab/mercury-mcp

Tier-B observation (per-layer hidden states) is still expanding — currently 11 of 23 models have full Tier-B. The remaining sweep is running on a Mac mini in the background. New data will land in v0.2.

This is part of a 7-paper Mercury series (papers A-G). Paper A "Cross-Architecture Hot-Dim Geometry" and Paper G "Composable LLMs vision" are based on this data. Drafts available in the paper-handoff repo (linked from README).

Built without grant, GPU cluster, or institutional affiliation. Just one researcher, two machines, and a lot of nights. Feedback / criticism welcome — especially from anyone doing mech interp at Anthropic, AllenAI, EleutherAI.
```

**Best time to submit:** Tuesday or Wednesday 8-10 AM Pacific Time (US morning waking up).

---

## 2. X / Twitter thread (8 posts)

**Post 1** (hook):

> I scanned the internal anchor structure of 23 LLMs on a Mac mini.
>
> Built it into a Model Context Protocol server so any AI coding agent (Claude Code, Cursor, Cline...) can query it.
>
> github.com/norika1207-lab/mercury-mcp
>
> Thread on what we found 🧵

**Post 2** (universal anchor):

> Finding #1: hidden dimension 11 appears in the top-50 hot dims of 11/18 LLMs across 5 architecture families.
>
> Including AllenAI's OLMo2 — fully open, completely independent training lineage. Zero shared data with qwen/llama/etc.
>
> Empirical evidence for anchor universality.

**Post 3** (distillation):

> Finding #2: DeepSeek-R1:70b uses a llama base, but its anchor structure shows 44.7× random qwen-anchor presence.
>
> Distillation transplants anchor identity. This is a fingerprint for model lineage detection.

**Post 4** (cross-arch alignment):

> Finding #3: qwen-7B layer 15 ≈ falcon-7B layer 16 at fingerprint similarity 0.868.
>
> Different vendors, different families, near-identical layer function. Middle layers (~50% depth) are the most universally aligned across architectures.

**Post 5** (boundaries):

> Finding #4: mistral-7B, mistral-small-24B, yi-1.5-9B all show 0/11 qwen-anchor presence.
>
> They occupy a different residual subspace entirely. Sliding-window attention is structurally different.
>
> This isn't failure — it opens cross-arch non-interfering composition.

**Post 6** (MCP server):

> All of this is queryable via MCP. 7 tools:
>
> - mercury_universal_anchors
> - mercury_cross_arch_equivalent
> - mercury_compose_recipe
> - ... and 4 more
>
> Ask your Claude Code: "find layers in qwen that match falcon-7B L16"

**Post 7** (vision):

> Long-term vision (Paper G): LLM-as-lego. Compose a model by picking layers from different families. Each layer is a known functional component, you click buttons to assemble.
>
> Mercury is the observation layer that makes this possible.

**Post 8** (acknowledgments + ask):

> Built solo, no GPU cluster, no grant. Mac mini + DGX Spark. Total compute cost ≈ $0.
>
> If you work in mech interp / model merging / LLM infrastructure, I'd love feedback.
>
> Code + data: github.com/norika1207-lab/mercury-mcp

---

## 3. LinkedIn (professional tone, single post)

```
After several weeks of nights, I shipped Mercury MCP — a Model Context Protocol server that exposes cross-architecture observation data for 23 LLMs to any AI coding agent.

The motivation: most agents today have zero architectural awareness of the LLM they're calling. Mercury fixes part of that — making per-model anchor dimensions, per-layer functional fingerprints, and cross-architecture alignment matrices into queryable infrastructure.

Built entirely on consumer hardware. No GPU cluster, no grant, no institutional backing.

Three findings worth highlighting:

→ Dimension 11 appears as a top hot dim in 11 of 18 surveyed LLMs across 5 architecture families, including AllenAI's fully-independent OLMo2. First large-scale empirical support for the anchor universality hypothesis.

→ DeepSeek-R1:70b (llama base, qwen-style distillation) inherits qwen anchor structure at 44.7× random baseline — anchors transplant through distillation, opening model lineage forensics.

→ qwen-7B layer 15 ↔ falcon-7B layer 16 at 0.868 fingerprint similarity. Different families, near-identical function. Middle layers are the most universally aligned across architectures.

The longer-term vision (Paper G in the series) is composable LLMs — layer-level "lego" assembly across model families. Mercury is the observation layer that makes it tractable.

Repo: https://github.com/norika1207-lab/mercury-mcp

Open to feedback, collaboration, and conversations with anyone working in mechanistic interpretability, model merging, or LLM infrastructure.

#MechanisticInterpretability #LLM #OpenSource #ModelContextProtocol #AIResearch
```

---

## 4. Email to mech-interp researchers (cold but warm)

**Subject:** Cross-architecture LLM observation database (23 models, MCP server) — interested in your feedback

**Recipients** (in priority order):
- Chris Olah <colah@anthropic.com> (Anthropic interp lead)
- Neel Nanda <neelnanda@gmail.com> (mech interp DeepMind, very responsive)
- Anthropic interpretability team general inbox
- AllenAI OLMo team (since OLMo2 features prominently)
- EleutherAI Discord #interp channel

**Body** (personalize per recipient):

```
Hi [Name],

I've been doing mechanistic interpretability work as an independent researcher in Taiwan, and just open-sourced something I'd love your feedback on:

Mercury MCP — a Model Context Protocol server exposing observation data for 23 LLMs across 13 architecture families. Built solo on a Mac mini + DGX Spark.

The headline result: dimension 11 appears in the top-50 hot dims of 11/18 models, including AllenAI's OLMo2 (which shares no training lineage with qwen / llama / etc). This is large-scale empirical evidence for the anchor universality hypothesis from your 2020 Circuits piece.

Other findings:
- Cross-arch layer alignment: qwen-7B L15 ≈ falcon-7B L16 at 0.868 similarity
- DeepSeek-R1:70b inherits qwen anchor structure at 44.7× random baseline (distillation transplants anchors)
- mistral / yi families show alternative residual stream geometry — possible compositional substrate

The MCP server makes all this data queryable from any agent (Claude Code, Cursor, Cline). 7 tools.

Repo: https://github.com/norika1207-lab/mercury-mcp

I'd value any feedback — especially on methodology gaps, scale of the next observation sweep, or framing of the upcoming paper.

Thanks for any time you can spare,
norika (Chen Ho Yiing)
ORCID: 0009-0006-6816-9891
```

---

## 5. Tracking checklist

After launch:

- [ ] Post on HN (Tuesday/Wed morning PT)
- [ ] Tweet thread same day
- [ ] LinkedIn same day
- [ ] Email 3-5 key researchers within 24h
- [ ] Monitor HN for first 4h (reply to comments fast — first hour decides ranking)
- [ ] Monitor X mentions
- [ ] Star/fork counts at 24h, 48h, 7d
- [ ] If HN front page → record metrics → write follow-up post in 2 weeks
