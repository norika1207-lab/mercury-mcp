# Example prompts to try with Mercury MCP installed

After installing Mercury MCP and restarting your agent (Claude Code, Cursor, Cline...), try these:

## Discovery
> "What LLMs has Mercury observed? Show me the list grouped by architecture family."

> "What are the universal hot dimensions that appear across the most architectures?"

## Single-model deep dive
> "Show me qwen2.5-7b-instruct's anchor dimensions and how they compare to the qwen-family universal anchor set."

> "How structurally similar is olmo2-7b to qwen2.5-7b — by anchor overlap?"

> "Get the layer 15 fingerprint of falcon3-7b. What's special about that layer?"

## Cross-architecture exploration
> "Find layers in OTHER models that match qwen2.5-7b layer 15 in functional fingerprint."

> "Which layer of mistral-7b is most similar to phi3-medium layer 20?"

## Composition / Frankenstein
> "Compose a layer recipe for a Chinese-writing + reasoning hybrid LLM."

> "I want to build a model that handles instruction-following well. Which layers from which models should I assemble?"

## Lineage detection
> "Compare deepseek-r1:70b's anchor signature to llama3.3-70b and to qwen2.5-7b. Which one is it more like?"

## Background
> "Tell me about the Mercury project — what is it, what's been found, how can I contribute?"
