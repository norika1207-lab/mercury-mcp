"""Basic smoke tests — verify data loads + tools return sensible results."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mercury_mcp.data_loader import MercuryDB, QWEN_ANCHORS


def test_loads():
    db = MercuryDB()
    models = db.list_models()
    print(f"loaded {len(models)} models")
    for m in models[:3]:
        print(f"  - {m['label']}: arch={m['arch']} L={m['n_layer']} H={m['hidden']}")
    assert len(models) > 0, "should load at least one model"

def test_anchor_dims():
    db = MercuryDB()
    if not db.list_models():
        print("SKIP: no models loaded")
        return
    label = db.list_models()[0]['label']
    res = db.anchor_dims(label, top_k=50)
    print(f"\nanchor_dims({label}):")
    print(f"  arch: {res['arch']}, hidden: {res['hidden']}")
    print(f"  top-5 dims: {res['top_hot_dims'][:5]}")
    print(f"  qwen-anchor overlap: {res['qwen_anchor_overlap']}")
    assert "qwen_anchor_overlap" in res

def test_universal_anchors():
    db = MercuryDB()
    res = db.universal_anchors(min_models=3)
    print(f"\nuniversal_anchors: {res['total_universal_dims']} dims meet threshold")
    print(f"  top 5:")
    for a in res['anchors'][:5]:
        marker = "⭐" if a['is_qwen_anchor'] else " "
        print(f"  {marker} dim {a['dim']}: in {a['models_containing']}/{a['total_observed']} models ({a['presence_pct']}%)")

def test_layer_fingerprint():
    db = MercuryDB()
    for fp_label in list(db.fingerprints.keys())[:1]:
        fp = db.fingerprints[fp_label]
        nl = fp["n_layer"]
        if nl > 10:
            res = db.layer_fingerprint(fp_label, nl // 2)
            print(f"\nlayer_fingerprint({fp_label}, layer={nl//2}):")
            print(f"  depth: {res.get('depth_pct')}%")
            print(f"  top_hot_dims: {res.get('top_hot_dims', [])[:5]}")
            assert "top_hot_dims" in res

def test_compose_recipe():
    db = MercuryDB()
    res = db.compose_recipe(["chinese_writing", "code", "unknown_thing"])
    print(f"\ncompose_recipe:")
    print(f"  recipe count: {len(res['recipe'])}")
    print(f"  unknown: {res['unknown_capabilities']}")
    assert res["recipe"]
    assert "unknown_thing" in res["unknown_capabilities"]

if __name__ == "__main__":
    print("="*60)
    test_loads()
    test_anchor_dims()
    test_universal_anchors()
    test_layer_fingerprint()
    test_compose_recipe()
    print("\n✅ all smoke tests passed")
