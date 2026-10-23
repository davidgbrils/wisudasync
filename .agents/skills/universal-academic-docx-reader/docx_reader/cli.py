from __future__ import annotations

import argparse
import json
from .core import extract_docx, inspect_docx, search_docx


def main():
    parser = argparse.ArgumentParser(prog="docx-reader", description="Extract and search academic DOCX files.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_inspect = sub.add_parser("inspect")
    p_inspect.add_argument("path")
    p_inspect.add_argument("--ocr", action="store_true")

    p_extract = sub.add_parser("extract")
    p_extract.add_argument("path")
    p_extract.add_argument("--output", default=None)
    p_extract.add_argument("--ocr", action="store_true")
    p_extract.add_argument("--chunk-chars", type=int, default=9000)

    p_search = sub.add_parser("search")
    p_search.add_argument("path")
    p_search.add_argument("query")
    p_search.add_argument("--max-results", type=int, default=10)
    p_search.add_argument("--output", default=None)

    args = parser.parse_args()
    if args.command == "inspect":
        result = inspect_docx(args.path, args.ocr)
    elif args.command == "extract":
        result = extract_docx(args.path, args.output, args.ocr, args.chunk_chars)
    else:
        result = search_docx(args.path, args.query, args.max_results, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
