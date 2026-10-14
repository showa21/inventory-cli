# Inventory CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) ![Built with](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

```text
$ python -m inventory add Widget 10 2.50
Added Widget (x10 @ $2.50)
$ python -m inventory add Gadget 3 19.99
Added Gadget (x3 @ $19.99)
$ python -m inventory stock Widget -4
Widget: 6 in stock
$ python -m inventory list
  2  Gadget                   3  $   19.99
  1  Widget                   6  $    2.50
$ python -m inventory low --threshold 5
  2  Gadget                   3  $   19.99
$ python -m inventory value
Total value: $74.97
```

A Python command-line inventory manager backed by SQLite. Standard library only.

```bash
python -m inventory add "Widget" 10 2.50
python -m inventory list --search wid
python -m inventory stock Widget -3
python -m inventory low --threshold 5
python -m inventory value
python -m inventory remove Widget
```

Use `--db path.db` to pick the database file (default `inventory.db`).

## Tests
```bash
python -m unittest discover -s tests
```

## Highlights
- Layered design: storage (`db.py`) is separate from the CLI (`cli.py`)
- DB-level constraints (`CHECK`, case-insensitive `UNIQUE`) plus input validation
- Parameterised queries throughout; clean error messages and exit codes
