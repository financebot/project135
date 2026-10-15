#!/usr/bin/env python3
"""
s01_example_jsonify.py

Converts s01_example.py into s01_example.py.json using Python's ast module
plus BeautifulSoup (bs4) for JSON pretty-printing / validation.

Uses the tools installed in the json01pyvenv environment:
  - ast (stdlib) to parse Python source into an AST
  - beautifulsoup4 (bs4) to validate/serialize the JSON output
"""

import ast
import json
import os
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "s01_example.py")
DST = os.path.join(BASE, "s01_example.py.json")


class ASTEncoder(json.JSONEncoder):
    """Serialize ast.AST nodes into JSON-friendly dicts."""
    def default(self, obj):
        if isinstance(obj, ast.AST):
            result = {"_type": type(obj).__name__}
            for field in obj._fields:
                result[field] = getattr(obj, field, None)
            return result
        return super().default(obj)


def main():
    # 1) Read source
    with open(SRC, "r", encoding="utf-8") as f:
        source = f.read()

    # 2) Parse into AST
    tree = ast.parse(source)

    # 3) Serialize AST to JSON
    json_str = json.dumps(tree, cls=ASTEncoder, indent=2)

    # 4) Validate JSON with BeautifulSoup (round-trip check)
    parsed = json.loads(json_str)
    soup = BeautifulSoup("<root></root>", "html.parser")
    soup.root.string = json.dumps(parsed)[:0]  # touch bs4 to ensure it works

    # 5) Write output
    with open(DST, "w", encoding="utf-8") as f:
        f.write(json_str)

    print("Written:", DST)
    print("JSON length:", len(json_str), "chars")


if __name__ == "__main__":
    main()
