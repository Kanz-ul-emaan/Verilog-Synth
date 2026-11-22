import os
import pytest
from helpers import synth, simulate, equivalent

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    with open(os.path.join(ROOT, "examples", name)) as f:
        return synth(f.read())


def bits(prefix, n, v):
    return {f"{prefix}{i}": (v >> i) & 1 for i in range(n)}


def test_adder4_matches_addition():
    _, opt = load("adder4.v")
    for a in range(16):
        for b in range(16):
            for cin in (0, 1):
                out = simulate(opt, {**bits("a", 4, a), **bits("b", 4, b), "cin": cin})
                s = sum(out[f"s{i}"] << i for i in range(4)) + (out["cout"] << 4)
                assert s == a + b + cin


def test_cmp4_matches_comparison():
    _, opt = load("cmp4.v")
    for a in range(16):
        for b in range(16):
            out = simulate(opt, {**bits("a", 4, a), **bits("b", 4, b)})
            assert out["eq"] == int(a == b)

            assert out["gt"] == int(a > b)
            assert out["lt"] == int(a < b)


@pytest.mark.parametrize("name", ["test2.v", "test3.v", "adder4.v", "cmp4.v"])
def test_optimization_preserves_behaviour(name):
    raw, opt = load(name)
    assert equivalent(raw, opt)


def test_cmp4_optimizer_reduces_cells():
    raw, opt = load("cmp4.v")
    assert (len(raw.cells), len(opt.cells)) == (42, 27)


def test_adder4_tree_mapping_saves_area():
    from techmap import map_to_sky130
    from techmap2 import tree_map
    _, opt = load("adder4.v")
    assert tree_map(opt)[1] < map_to_sky130(opt)[1]
