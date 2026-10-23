# Universal Academic DOCX Reader

A local-first DOCX extraction toolkit exposed as an MCP server for AI agents. Designed for academic documents (theses, internship reports, papers, course materials) and long documents.

## What it does

- Extracts body text and preserves a best-effort order of paragraphs/tables.
- Extracts headers, footers, footnotes, endnotes, comments, document properties, and embedded images using `docx2python`.
- Optionally OCRs embedded images with Tesseract (`pytesseract` + Pillow).
- Splits extracted text into stable, searchable chunks so long documents need not be sent to the model all at once.
- Exposes MCP tools: `inspect_docx`, `search_docx`, `read_docx_chunk`, `list_docx_chunks`, and `extract_docx`.
- Writes extraction artifacts to a local output folder and reports what was/wasn't available.

## Important limitations

No single parser can guarantee perfect extraction of every Word feature. Text boxes, SmartArt, charts, embedded OLE objects, tracked changes, equations, and complex nested layouts may need extra XML handling or conversion/OCR. OCR is optional and depends on local Tesseract installation. Page numbers are not stable in DOCX; this tool uses chunk IDs and section labels instead. Never treat extraction as proof that every visual element was understood—review the manifest and warnings.

## Requirements

- Python 3.11+
- `uv` recommended, or `pip`
- Tesseract OCR is optional; install it separately to enable OCR.

## Install

### With uv

```bash
uv venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

uv pip install -e .
```

### With pip

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

python -m pip install -e .
```

## Quick start: CLI

```bash
docx-reader inspect "C:/path/to/report.docx"
docx-reader extract "C:/path/to/report.docx" --output ./artifacts
docx-reader search "C:/path/to/report.docx" "metodologi penelitian"
```

On Windows, quote paths containing spaces.

## Run MCP server

```bash
docx-reader-mcp
```

The default transport is `stdio`, which is appropriate for local MCP clients. Configure your MCP host to launch this command or launch `python -m docx_reader.mcp_server` in the host's supported configuration.

### Generic MCP config example

Adapt the field names to the client you use:

```json
{
  "mcpServers": {
    "academic-docx-reader": {
      "command": "docx-reader-mcp",
      "args": [],
      "env": {
        "DOCX_READER_OUTPUT_DIR": "C:/docx-reader-artifacts"
      }
    }
  }
}
```

If the MCP client cannot resolve installed console scripts, use the absolute path to your virtual environment's Python executable and pass `-m docx_reader.mcp_server` as arguments. Do not copy this example blindly; MCP config formats vary by host.

## MCP tools

- `inspect_docx(path, ocr_images=false)`: metadata, counts, extraction status, and warnings.
- `extract_docx(path, output_dir="", ocr_images=false, chunk_chars=9000)`: writes JSON, Markdown, extracted images, and chunk files.
- `search_docx(path, query, max_results=10)`: case-insensitive search across extracted text.
- `list_docx_chunks(path, offset=0, limit=20)`: list chunk IDs and previews.
- `read_docx_chunk(path, chunk_id)`: read one chunk by ID, e.g. `chunk-0001`.

Tools accept local filesystem paths. Only point the server at files you are authorized to read. Consider running it with a restricted working directory if documents are sensitive.

## Long-document workflow

1. Call `inspect_docx`.
2. Call `extract_docx` to create an indexed extraction bundle.
3. Use `search_docx` to locate relevant concepts.
4. Use `list_docx_chunks` to inspect the outline/previews.
5. Read relevant chunks with `read_docx_chunk`.
6. For a whole-document summary, process all chunks in batches and explicitly track processed chunk IDs. Do not infer that a document was fully reviewed after reading only the first few chunks.

## Validation

```bash
pytest -q
```

Create a synthetic DOCX and run the smoke test:

```bash
python examples/create_sample_docx.py
docx-reader inspect examples/sample_academic.docx
docx-reader extract examples/sample_academic.docx --output ./artifacts
```

## Privacy

Extraction runs locally. If the connected LLM sends extracted text to a hosted model, that text may leave the machine according to the LLM provider's policies. This package itself does not upload documents.
