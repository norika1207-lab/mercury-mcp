"""Load Mercury observation data from disk into queryable structures.

Schema (heat-summary JSON):
    {
        "ts": int,
        "tag" / "model": str,
        "arch": str,
        "n_layer": int,
        "hidden": int,
        "tier": "A" or "B",
        "hottest" / "hottest_top100" / "hottest_top200": [
            {"nid":int, "layer":int, "dim":int, "q":int, "heat":int}, ...
        ]
    }
"""
import json, os, glob
from pathlib import Path
from typing import Optional
from collections import defaultdict

# 11 anchor dims identified within Qwen2.5 family — used as universal probe set
QWEN_ANCHORS = [11, 12, 25, 279, 334, 382, 476, 481, 510, 715, 758]

DATA_DIR = Path(os.environ.get(
    "MERCURY_DATA_DIR",
    Path(__file__).resolve().parent.parent / "data"
))


class MercuryDB:
    """In-memory store for all observed models. Loads at startup."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        self.models: dict[str, dict] = {}      # label -> heat-summary dict
        self.fingerprints: dict[str, dict] = {} # label -> fingerprint dict
        self.match_matrices: dict[tuple, dict] = {}  # (a,b) -> {matrix, n_layer_a, n_layer_b}
        self._load_all()

    def _normalize_label(self, raw: dict) -> str:
        """Pick a stable label for the model."""
        return (raw.get("tag") or raw.get("model") or "unknown").lower()\
            .replace(":", "-").replace("/", "_").replace(" ", "")

    def _load_heat_summary(self, path: Path) -> Optional[dict]:
        try:
            d = json.load(open(path))
            label = self._normalize_label(d)
            # Normalize hottest list location
            hottest = d.get("hottest") or d.get("hottest_top200") \
                or d.get("hottest_top100") or d.get("hottest_top500") or []
            d["_hottest"] = hottest
            d["_label"] = label
            # Normalize hidden/n_layer keys across schema versions
            if "hidden" not in d:
                d["hidden"] = d.get("hidden_size") or d.get("embedding_length") or 0
            if "n_layer" not in d:
                d["n_layer"] = d.get("num_hidden_layers") or d.get("block_count") or 0
            return d
        except Exception as e:
            print(f"WARN: failed to load {path}: {e}")
            return None

    def _load_all(self):
        # Heat summaries
        for p in self.data_dir.glob("heat-summaries/*.json"):
            d = self._load_heat_summary(p)
            if d:
                label = d["_label"]
                # Keep the most recent if multiple
                if label not in self.models or d.get("ts", 0) > self.models[label].get("ts", 0):
                    self.models[label] = d
        # Also check root data dir
        for p in self.data_dir.glob("*.json"):
            d = self._load_heat_summary(p)
            if d:
                label = d["_label"]
                if label not in self.models:
                    self.models[label] = d

        # Layer fingerprints
        fp_dir = self.data_dir / "layer-fingerprints"
        if fp_dir.exists():
            for p in fp_dir.glob("*.json"):
                if p.name.startswith("match-"):
                    self._load_match(p)
                else:
                    try:
                        d = json.load(open(p))
                        self.fingerprints[d.get("label", p.stem).lower()] = d
                    except Exception as e:
                        print(f"WARN fp {p}: {e}")

    def _load_match(self, path: Path):
        try:
            d = json.load(open(path))
            a, b = d.get("a"), d.get("b")
            if a and b:
                self.match_matrices[(a.lower(), b.lower())] = d
                self.match_matrices[(b.lower(), a.lower())] = {
                    "a": b, "b": a,
                    "n_layer_a": d["n_layer_b"], "n_layer_b": d["n_layer_a"],
                    "matrix": [[d["matrix"][i][j] for i in range(d["n_layer_a"])]
                               for j in range(d["n_layer_b"])],
                }
        except Exception as e:
            print(f"WARN match {path}: {e}")

    # ---- Query API ----

    def list_models(self) -> list[dict]:
        out = []
        for lbl, d in sorted(self.models.items()):
            out.append({
                "label": lbl,
                "model": d.get("model") or d.get("tag"),
                "arch": d.get("arch", "unknown"),
                "n_layer": d.get("n_layer"),
                "hidden": d.get("hidden"),
                "tier": d.get("tier"),
                "hot_cells_observed": len(d["_hottest"]),
            })
        return out

    def get_model(self, label: str) -> Optional[dict]:
        return self.models.get(label.lower())

    def anchor_dims(self, label: str, top_k: int = 50) -> dict:
        d = self.get_model(label)
        if not d:
            return {"error": f"unknown model: {label}", "available": list(self.models.keys())}
        H = d["hidden"]
        # ordered unique dims by hotness
        dims = []
        for e in d["_hottest"]:
            if e["dim"] not in dims:
                dims.append(e["dim"])
        top = dims[:top_k]
        # check qwen-anchor presence
        qwen_hits = [a for a in QWEN_ANCHORS if a in top]
        expected = top_k * 11 / H
        ratio = (len(qwen_hits) / expected) if expected > 0 else 0
        return {
            "label": label,
            "arch": d.get("arch"),
            "n_layer": d["n_layer"],
            "hidden": H,
            "tier": d.get("tier"),
            "top_hot_dims": top,
            "qwen_anchor_overlap": {
                "hits": qwen_hits,
                "count": len(qwen_hits),
                "expected_random": round(expected, 3),
                "ratio_vs_random": round(ratio, 1),
            },
        }

    def universal_anchors(self, min_models: int = 3) -> dict:
        """Anchors that appear in top-50 of at least min_models observed models."""
        rank_by_dim_by_model: dict[int, dict[str, int]] = defaultdict(dict)
        for lbl, d in self.models.items():
            H = d["hidden"]
            dims = []
            for e in d["_hottest"]:
                if e["dim"] not in dims:
                    dims.append(e["dim"])
            for rank, dim in enumerate(dims[:50], 1):
                rank_by_dim_by_model[dim][lbl] = rank
        # rank dims by cross-model presence
        results = []
        for dim, by_model in rank_by_dim_by_model.items():
            if len(by_model) >= min_models:
                results.append({
                    "dim": dim,
                    "models_containing": len(by_model),
                    "total_observed": len(self.models),
                    "presence_pct": round(100 * len(by_model) / len(self.models), 1),
                    "is_qwen_anchor": dim in QWEN_ANCHORS,
                    "in_models": list(by_model.keys()),
                    "best_rank": min(by_model.values()),
                })
        results.sort(key=lambda x: -x["models_containing"])
        return {
            "total_universal_dims": len(results),
            "total_models_surveyed": len(self.models),
            "min_presence_threshold": min_models,
            "anchors": results,
        }

    def layer_fingerprint(self, label: str, layer: int) -> dict:
        norm_label = label.lower().replace(":", "-")
        # try exact + close matches
        fp = self.fingerprints.get(norm_label)
        if not fp:
            for k in self.fingerprints:
                if norm_label in k or k in norm_label:
                    fp = self.fingerprints[k]; break
        if not fp:
            return {"error": f"no fingerprint for {label}",
                    "available": list(self.fingerprints.keys())}
        per_layer = fp["fingerprints"]
        if layer < 0 or layer >= len(per_layer):
            return {"error": f"layer out of range 0..{len(per_layer)-1}"}
        return {
            "label": fp["label"], "n_layer": fp["n_layer"], "hidden": fp["hidden"],
            "layer": layer, "depth_pct": round(100 * layer / max(1, fp["n_layer"]-1), 1),
            **per_layer[layer],
        }

    def cross_arch_equivalent(self, label: str, layer: int, top_k: int = 5) -> dict:
        norm_label = label.lower().replace(":", "-")
        matches = []
        for (a, b), m in self.match_matrices.items():
            if a == norm_label or a.endswith(norm_label):
                NB = m["n_layer_b"]
                row = m["matrix"][layer] if layer < len(m["matrix"]) else None
                if not row:
                    continue
                for j, sim in enumerate(row):
                    if sim > 0:
                        matches.append({
                            "target_model": b,
                            "target_layer": j,
                            "target_depth_pct": round(100 * j / max(1, NB-1), 1),
                            "similarity": round(sim, 3),
                        })
        matches.sort(key=lambda x: -x["similarity"])
        return {
            "source_model": label,
            "source_layer": layer,
            "matches": matches[:top_k],
        }

    def compose_recipe(self, capabilities: list[str]) -> dict:
        """Heuristic: map requested capabilities to layer recipe across models.

        v0.1: returns rough suggestions based on known anchor → behavior mappings.
        Future: trained recipe compiler.
        """
        # Known mappings from Paper B + observation
        CAPABILITY_MAP = {
            "chinese_writing": [
                {"model": "qwen2.5-7b-instruct", "layers": list(range(24, 28)),
                 "reason": "dim 758 (Chinese narrative trigger) lives in last 4 layers"},
                {"model": "qwen3b-tierb", "layers": list(range(28, 36)),
                 "reason": "qwen 3B late layers, same family"},
            ],
            "code": [
                {"model": "qwen-coder", "layers": list(range(20, 28)),
                 "reason": "code-specialized fine-tune later layers"},
            ],
            "reasoning": [
                {"model": "ds-r1-7b-tierb", "layers": list(range(10, 28)),
                 "reason": "DeepSeek R1 distilled reasoning anchors"},
            ],
            "instruction_following": [
                {"model": "phi3-medium-tierb", "layers": list(range(20, 40)),
                 "reason": "phi3 dim 4271-4366 instruction-cluster in upper layers"},
            ],
            "multilayer_thinking": [
                {"model": "mistral-7b-tierb", "layers": "all",
                 "reason": "mistral SWA distributes processing across all layers"},
            ],
        }
        recipe = []
        unknown = []
        for cap in capabilities:
            c = cap.lower().replace(" ", "_")
            if c in CAPABILITY_MAP:
                recipe.append({"capability": cap, "layers": CAPABILITY_MAP[c]})
            else:
                unknown.append(cap)
        return {
            "requested": capabilities,
            "recipe": recipe,
            "unknown_capabilities": unknown,
            "available_capabilities": list(CAPABILITY_MAP.keys()),
            "note": "v0.1 returns curated recipes from Paper B observations. "
                    "v0.2 will compile recipes from layer-fingerprint similarity.",
        }


# Module-level singleton (lazy init)
_db: Optional[MercuryDB] = None

def get_db() -> MercuryDB:
    global _db
    if _db is None:
        _db = MercuryDB()
    return _db
