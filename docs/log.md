## 2026-09-22: Final results

### What was built
- Parser (Lark): `& | ^ ~`, parentheses, `wire`, precedence ~ > & > ^ > |
- Elaboration: undeclared signal, multiple driver, assign-to-input, duplicate declaration checks
- IR: flat cell graph (AND/OR/XOR/NOT/BUF/TIE)
- Optimizer: CSE, idempotence, double negation, complement, absorption, constant propagation, dead-gate removal
- Technology mapper: minimum-cost tree covering over 15 Sky130 cells (+ conb tie cell)
- Backend and driver: structural Verilog netlist, `synth.py`
- Verification: 36 pytest tests, plus Verilator gate-level simulation (`run_all.sh`)

### Results
| Benchmark | Levels | Cells raw / opt | Direct (um^2) | Tree (um^2) | Saved | Simulation |
|---|---|---|---|---|---|---|
| test2 | 3 | 3 / 2 | 12.5120 | 12.5120 | 0.0% | 8/8 PASS |
| test3 | n/a | 9 / 4 | 15.0144 | 15.0144 | 0.0% | 8/8 PASS |
| adder4 | 9 | 20 / 20 | 145.1392 | 105.1008 | 27.6% | 512/512 PASS |
| cmp4 | 9 | 42 / 27 | 156.4000 | 96.3424 | 38.4% | 256/256 PASS |

### Decisions and why
- Objective is area (cell count and um^2): the circuits are combinational, so clock-based performance does not apply, and area is measurable directly from the Liberty file.
- Bitwise operators only: `&&`, `||`, `!` need reduction semantics and are not used in structural logic.
- Direct tree-covering mapper (slides 55-59) instead of cut-based NPN matching.
- Cell areas hardcoded after checking them against sky130_fd_sc_hd__tt_025C_1v80.lib. No Liberty parser.
- Verilator needed the `verilator-devel` package on Rocky 9 to work.

### Problems solved
- Wrong inverter area in my first table (2.503 vs real 3.7536), found by checking the .lib
- Tie cell pins were entered as inputs, causing "expects 1 input, got 0"

### Known limitations
- No general Boolean minimization (Quine-McCluskey, Espresso)

- 1-bit signals, single module, no always/if/case
- Fixed NAND2/INV decomposition
- Area-only cost, no timing

### Still to do
- Confirm with instructor: area objective acceptable? `wire` allowed? report/demo format and deadline?
- Optional: always @*, vectors, Quine-McCluskey
