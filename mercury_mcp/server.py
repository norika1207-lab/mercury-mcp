"""Mercury MCP Server — exposes LLM internal observation data as agent tools.

Run via stdio (standard for MCP):
    python -m mercury_mcp.server

Then point your agent (Claude Code, Cursor, Cline, etc) at this server.
Example Claude Code config snippet (~/.claude/mcp_settings.json):
    {
        "mcpServers": {
            "mercury": {
                "command": "python",
                "args": ["-m", "mercury_mcp.server"],
                "env": {"MERCURY_DATA_DIR": "/path/to/mercury-mcp/data"}
            }
        }
    }
"""
import asyncio
import json
import sys
from typing import Any

from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
import mcp.types as types

from .data_loader import get_db

server = Server("mercury")


# ----- Tool definitions -----

TOOLS = [
    types.Tool(
        name="mercury_list_models",
        description=(
            "List all LLMs that have been observed by Mercury. Returns model labels, "
            "architecture family, layer count, hidden size, and observation tier "
            "(A=output-layer-only, B=per-layer). Use this first to see what's available."
        ),
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    types.Tool(
        name="mercury_anchor_dims",
        description=(
            "Get the top hot hidden dimensions ('anchors') of a specific model. "
            "These are the dimensions that consistently fire across diverse prompts. "
            "Includes overlap analysis against the qwen-family universal anchor set "
            "(dims 11, 12, 25, 279, 334, 382, 476, 481, 510, 715, 758) with ratio vs "
            "hypergeometric random baseline."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Model label (e.g. 'qwen2.5-7b-instruct', 'olmo2-7b-tierb'). Call mercury_list_models to see options."},
                "top_k": {"type": "integer", "default": 50, "minimum": 5, "maximum": 500},
            },
            "required": ["model"],
        },
    ),
    types.Tool(
        name="mercury_universal_anchors",
        description=(
            "Find hidden dimensions that appear in top-K hottest across multiple architecture "
            "families — these are candidate 'universal residual stream landmarks'. "
            "Returns per-dim presence count across all observed models, marking which are "
            "in the original qwen 11-anchor set. dim 11 currently appears in 11/18 models."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "min_models": {"type": "integer", "default": 3, "description": "Minimum number of models a dim must appear in."},
            },
        },
    ),
    types.Tool(
        name="mercury_layer_fingerprint",
        description=(
            "Get the functional fingerprint of a specific layer in a specific model "
            "(Tier-B observation required). Includes top hot dims at this layer, "
            "heat concentration, dim-range distribution (low/mid/high), and quantile "
            "buckets. Use to understand 'what this layer does'."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "layer": {"type": "integer", "minimum": 0},
            },
            "required": ["model", "layer"],
        },
    ),
    types.Tool(
        name="mercury_cross_arch_equivalent",
        description=(
            "Find layers in OTHER models that have similar functional fingerprint to a "
            "given (model, layer). Useful for cross-architecture layer-swap experiments "
            "(Frankenstein-style hybrid building). Strongest known match: "
            "qwen-7b L15 ↔ falcon-7b L16 at similarity 0.868."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "layer": {"type": "integer", "minimum": 0},
                "top_k": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
            },
            "required": ["model", "layer"],
        },
    ),
    types.Tool(
        name="mercury_compose_recipe",
        description=(
            "Generate a layer recipe (composable LLM 'lego' blueprint) for requested "
            "capabilities. Maps high-level needs (e.g. 'chinese_writing', 'code', "
            "'reasoning') to specific (model, layer-range) tuples based on Mercury's "
            "observed anchor → behavior mappings (Paper B). v0.1 returns curated "
            "recipes; v0.2 will compile from fingerprint similarity."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "capabilities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of desired capabilities. Call with empty list to see available.",
                },
            },
            "required": ["capabilities"],
        },
    ),
    types.Tool(
        name="mercury_about",
        description="Background on Mercury — what this dataset is, citations, paper status, and how to contribute new observations.",
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
]


# ----- Server handlers -----

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return TOOLS


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    args = arguments or {}
    db = get_db()
    try:
        if name == "mercury_list_models":
            result = {"models": db.list_models(), "total": len(db.models)}
        elif name == "mercury_anchor_dims":
            result = db.anchor_dims(args["model"], args.get("top_k", 50))
        elif name == "mercury_universal_anchors":
            result = db.universal_anchors(args.get("min_models", 3))
        elif name == "mercury_layer_fingerprint":
            result = db.layer_fingerprint(args["model"], args["layer"])
        elif name == "mercury_cross_arch_equivalent":
            result = db.cross_arch_equivalent(
                args["model"], args["layer"], args.get("top_k", 5))
        elif name == "mercury_compose_recipe":
            result = db.compose_recipe(args["capabilities"])
        elif name == "mercury_about":
            result = {
                "what": "Mercury is a 18-LLM cross-architecture observation database "
                        "built on consumer hardware (DGX Spark + Mac mini). It quantifies "
                        "each LLM's internal anchor structure, layer-level functional "
                        "fingerprint, and cross-architecture layer alignment.",
                "models_observed": len(db.models),
                "families_covered": "qwen / qwen-distill / llama / phi3 / falcon3 / "
                                    "internlm2 / mistral / mistral-SWA / yi / gemma2 / "
                                    "granite / olmo2",
                "key_findings": [
                    "dim 11 appears in top-50 hot dims of 11/18 models across 5+ families",
                    "OLMo2 (AllenAI fully-open) shows 4/11 qwen-anchor hits at 29.8x random",
                    "qwen-7B L15 ↔ falcon-7B L16 cross-arch similarity = 0.868",
                    "Mistral / Yi exhibit alternative residual stream geometry (0/11)",
                ],
                "papers": ["A: cross-arch anchor conservation",
                           "B: single-dim functional control",
                           "C: merge failures catalog",
                           "D: tier-B per-layer evolution",
                           "E: 100M-cell observability",
                           "F: cross-arch layer alignment",
                           "G: composable LLMs vision"],
                "author": "norika (Chen Ho Yiing), ORCID 0009-0006-6816-9891",
                "repo": "https://github.com/norikaoda/mercury-mcp",
                "data_doi_base": "10.5281/zenodo.20313154",
            }
        else:
            result = {"error": f"unknown tool: {name}"}
    except Exception as e:
        result = {"error": str(e), "tool": name}
    return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


# ----- Entrypoint -----

async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream,
            InitializationOptions(
                server_name="mercury",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    asyncio.run(_run())


if __name__ == "__main__":
    main()
