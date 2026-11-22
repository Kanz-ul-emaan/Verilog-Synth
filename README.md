# Python-based Verilog Synthesizer (ASIC target)

<h1 align="center">Python-based Verilog Synthesizer for Sky130</h1>

<p align="center">
A combinational RTL synthesizer written in Python that maps Verilog to SkyWater Sky130 standard cells.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9+-blue">
  <img alt="Tests" src="https://img.shields.io/badge/tests-36%20passing-brightgreen">
  <img alt="PDK" src="https://img.shields.io/badge/PDK-sky130__fd__sc__hd-orange">
</p>

**Author:** Kanz-ul-emaan Ahmed

---

## Overview

The tool reads a combinational Verilog subset, optimizes the logic, maps it to `sky130_fd_sc_hd` cells, and writes a structural Verilog netlist. Every result is verified by exhaustive simulation against the original RTL.

## Key results

Benchmarks with at least 6 logic levels (both have 9):

| Benchmark | Inputs | Raw gates | After optimization | Direct mapping | Tree covering | Area saved |
|:--|:-:|:-:|:-:|--:|--:|:-:|
| 4-bit adder (`adder4`) | 9 | 20 | 20 | 145.14 µm² | **105.10 µm²** | **27.6%** |
| 4-bit comparator (`cmp4`) | 8 | 42 | **27** | 156.40 µm² | **96.34 µm²** | **38.4%** |

Small checks: `test2` (3 → 2 cells, 12.51 µm²) and `test3`, which exercises the redundancy rules (9 → 4 cells, 15.01 µm²).

All four netlists pass exhaustive simulation (8, 8, 512 and 256 input combinations).


## Pipeline

```mermaid
flowchart LR
    A[Verilog] --> B[Parse<br/>Lark]
    B --> C[Elaborate<br/>checks]
    C --> D[IR<br/>cell graph]
    D --> E[Optimize]
    E --> F[Tree-covering<br/>tech mapping]
    F --> G[Sky130<br/>netlist]
```

| Stage | What it does | File |
|:--|:--|:--|
| Parse | Grammar with operator precedence and parentheses | `src/parser.py` |
| Elaborate | Signal table; undeclared, multi-driver and input-assign checks | `src/elaborate.py` |
| IR | Flattens expressions into AND/OR/XOR/NOT cells | `src/ir.py` |
| Optimize | Boolean identities and common-subexpression elimination | `src/optimize.py` |
| Map | Minimum-cost tree covering over 15 Sky130 cells | `src/techmap2.py` |
| Baseline map | One-to-one mapping, used for comparison | `src/techmap.py` |
| Backend | Writes structural Verilog | `src/backend.py` |
| Driver | Runs the whole flow | `src/synth.py` |

## Optimization

**Objective:** minimize area (cell count and µm², taken from the Sky130 Liberty file).

**1. Pre-mapping optimization**

| Rule | Example |
|:--|:--|

| Common-subexpression elimination | two copies of `a ^ b` become one |
| Idempotence | `x & x = x` |
| Double negation | `~~x = x` |
| Complement | `a & ~a = 0`, `a \| ~a = 1` |
| Absorption | `x \| (x & y) = x` |
| Constant propagation | `1 ^ y = ~y` |
| Dead-gate removal | gates that feed no output are deleted |

**2. Technology mapping:** the netlist is decomposed into NAND2/INV, split into trees at shared signals, and covered by dynamic programming with `cost(node) = min( area(cell) + Σ cost(inputs) )`. Each pattern is self-checked against its cell's Boolean function.

## Example

Input:

```verilog
module top(input a, input b, input c, input p, output y);
  assign y = (a & b) | (c & p);
endmodule
```

Output (three gates collapse into one cell):

```verilog
sky130_fd_sc_hd__a22o_1 u0 (.A1(a), .A2(b), .B1(c), .B2(p), .X(y));
```

## Supported Verilog subset

| Supported | Not supported |
|:--|:--|
| One module, 1-bit `input`/`output` ports | Vectors, multiple modules, hierarchy |
| `wire` declarations | `always`, `if`, `case` |

| `assign` with `&`, `\|`, `^`, `~`, parentheses | `&&`, `\|\|`, `!`, arithmetic operators |
| Precedence `~` > `&` > `^` > `\|` | Sequential logic |

Signals must be assigned before they are used.

## Usage

```bash
source venv/bin/activate
python3 src/synth.py examples/adder4.v reports/adder4_netlist.v
./run_all.sh            # synthesize and simulate every benchmark
python3 -m pytest -v    # 36 unit and end-to-end tests
```

Simulation needs Verilator and the Sky130 PDK. Set `VDIR` to the PDK's `sky130_fd_sc_hd/verilog` directory.

## Verification

- **36 pytest tests** cover the parser, elaboration, optimizer, mapper and end-to-end behaviour. The adder and comparator are checked against Python's own `+`, `==`, `>` and `<`.
- **Gate-level simulation** with Verilator and the Sky130 cell models compares each mapped netlist with the original RTL for every input combination.

## Limitations

- Combinational and bitwise logic only; 1-bit signals; single module
- No general Boolean minimization (Quine-McCluskey, Espresso); only local identities
- Fixed NAND2/INV decomposition; tree covering is optimal per tree, not globally
- Area-only cost; no timing or power optimization
- Cell areas are hardcoded and verified against `sky130_fd_sc_hd__tt_025C_1v80.lib`; there is no Liberty parser
