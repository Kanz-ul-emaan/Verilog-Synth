## 2026-10-2 (replace with today's date)
- Completed: Git/GitHub setup, Python venv, Lark + pytest installed
- Built: Lark grammar for assign statements with &, |, ^, ~ and parentheses
- Verified correct precedence: NOT > AND > XOR > OR (matches IEEE Verilog LRM)
- Verified parentheses correctly override default precedence (tested (a|b)&c vs a|b&c)
- Added graceful error handling for unsupported operators (&&, ||, !) — documented as out of scope
- Next: elaboration stage (parameter eval, width inference, driver/undeclared-signal checks)
