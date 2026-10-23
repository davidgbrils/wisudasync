from __future__ import annotations

import json
from mcp.server.fastmcp import FastMCP
from .core import extract_docx, inspect_docx, search_docx, list_docx_chunks, read_docx_chunk

mcp = FastMCP("Universal Academic DOCX Reader")


@mcp.tool()
def inspect_docx_tool(path: str, ocr_images: bool = False) -> str:
    """Inspect a local DOCX, report extraction counts, package features, and warnings."""
    return json.dumps(inspect_docx(path, ocr_images=ocr_images), ensure_ascii=False)


@mcp.tool()
def extract_docx_tool(path: str, output_dir: str = "", ocr_images: bool = False, chunk_chars: int = 9000) -> str:
    """Extract DOCX content to local artifacts: Markdown, JSON sections, comments, images, and chunks."""
    return json.dumps(extract_docx(path, output_dir or None, ocr_images, chunk_chars), ensure_ascii=False)


@mcp.tool()
def search_docx_tool(path: str, query: str, max_results: int = 10, output_dir: str = "") -> str:
    """Search extracted DOCX text case-insensitively and return chunk IDs plus contextual snippets."""
    return json.dumps(search_docx(path, query, max_results, output_dir or None), ensure_ascii=False)


@mcp.tool()
def list_docx_chunks_tool(path: str, offset: int = 0, limit: int = 20, output_dir: str = "") -> str:
    """List chunk IDs and previews for a long DOCX. Use offset/limit to paginate."""
    return json.dumps(list_docx_chunks(path, offset, limit, output_dir or None), ensure_ascii=False)


@mcp.tool()
def read_docx_chunk_tool(path: str, chunk_id: str, output_dir: str = "") -> str:
    """Read one chunk by ID, for example chunk-0001, without loading the entire document into the model context."""
    return json.dumps(read_docx_chunk(path, chunk_id, output_dir or None), ensure_ascii=False)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
