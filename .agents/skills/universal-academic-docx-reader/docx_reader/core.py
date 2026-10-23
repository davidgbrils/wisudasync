from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from docx2python import docx2python

DEFAULT_OUTPUT = Path(os.environ.get("DOCX_READER_OUTPUT_DIR", "./docx-reader-artifacts")).resolve()
MAX_FILE_BYTES = int(os.environ.get("DOCX_READER_MAX_FILE_BYTES", str(200 * 1024 * 1024)))
DEFAULT_CHUNK_CHARS = 9000


def _validate_docx(path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    if p.suffix.lower() != ".docx":
        raise ValueError("Only .docx files are supported. .doc is not a ZIP-based DOCX file.")
    size = p.stat().st_size
    if size > MAX_FILE_BYTES:
        raise ValueError(f"File is {size} bytes; configured limit is {MAX_FILE_BYTES} bytes.")
    if not zipfile.is_zipfile(p):
        raise ValueError("The file is not a valid DOCX/ZIP package.")
    with zipfile.ZipFile(p) as zf:
        names = set(zf.namelist())
        if "word/document.xml" not in names:
            raise ValueError("ZIP package does not contain word/document.xml; it may not be a valid DOCX.")
    return p


def _flatten(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _flatten(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _flatten(item)


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return cleaned[:100] or "document"


def _xml_counts(path: Path) -> dict[str, int]:
    """Counts common package parts; this is inventory, not proof of semantic extraction."""
    counts = {
        "images": 0, "charts": 0, "diagrams": 0, "embedded_objects": 0,
        "footnotes_part": 0, "endnotes_part": 0, "comments_part": 0,
        "tracked_change_markers": 0, "textboxes": 0, "equations": 0
    }
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            counts["images"] = sum(1 for n in names if n.startswith("word/media/"))
            counts["charts"] = sum(1 for n in names if n.startswith("word/charts/") and n.endswith(".xml"))
            counts["diagrams"] = sum(1 for n in names if n.startswith("word/diagrams/") and n.endswith(".xml"))
            counts["embedded_objects"] = sum(1 for n in names if n.startswith("word/embeddings/"))
            counts["footnotes_part"] = int("word/footnotes.xml" in names)
            counts["endnotes_part"] = int("word/endnotes.xml" in names)
            counts["comments_part"] = int(any(n.startswith("word/comments") and n.endswith(".xml") for n in names))
            for n in names:
                if n.endswith(".xml") and n.startswith("word/") and not n.startswith("word/media/"):
                    try:
                        data = zf.read(n)
                        counts["tracked_change_markers"] += data.count(b"<w:ins") + data.count(b"<w:del")
                        counts["textboxes"] += data.count(b"<w:txbxContent")
                        counts["equations"] += data.count(b"<m:oMath")
                    except (KeyError, RuntimeError, zipfile.BadZipFile):
                        pass
    except zipfile.BadZipFile:
        pass
    return counts


def _metadata(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        props = {}
        if "docProps/core.xml" in names:
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(zf.read("docProps/core.xml"))
                for child in root:
                    props[child.tag.split("}")[-1]] = (child.text or "").strip()
            except ET.ParseError:
                props["warning"] = "Could not parse docProps/core.xml"
    return {
        "file_name": path.name,
        "absolute_path": str(path),
        "size_bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "core_properties": props,
        "package_inventory": _xml_counts(path),
    }


def _extract_sections(path: Path, image_dir: Path | None = None) -> dict[str, Any]:
    # docx2python retains useful nesting and extracts headers/footers/notes/comments/images.
    with docx2python(str(path), image_folder=str(image_dir) if image_dir else None) as doc:
        sections = {
            "header": "\n".join(x.strip() for x in _flatten(doc.header) if x.strip()),
            "footer": "\n".join(x.strip() for x in _flatten(doc.footer) if x.strip()),
            "body": "\n".join(x.strip() for x in _flatten(doc.body) if x.strip()),
            "footnotes": "\n".join(x.strip() for x in _flatten(getattr(doc, "footnotes", [])) if x.strip()),
            "endnotes": "\n".join(x.strip() for x in _flatten(getattr(doc, "endnotes", [])) if x.strip()),
        }
        comments = []
        for c in getattr(doc, "comments", []) or []:
            try:
                reference_text, author, date, comment_text = c
                comments.append({
                    "reference_text": str(reference_text or ""),
                    "author": str(author or ""),
                    "date": str(date or ""),
                    "comment_text": str(comment_text or "")
                })
            except Exception:
                comments.append({"raw": str(c)})
        props = {}
        for key in ("properties", "core_properties"):
            val = getattr(doc, key, None)
            if val:
                try:
                    props[key] = {str(k): str(v) for k, v in vars(val).items()}
                except Exception:
                    props[key] = str(val)
        return {"sections": sections, "comments": comments, "docx2python_properties": props}


def _chunks_from_sections(sections: dict[str, str], chunk_chars: int) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    # Sections are kept separate to avoid mixing note/header/footer content into body chunks.
    for section_name in ("body", "header", "footer", "footnotes", "endnotes"):
        text = sections.get(section_name, "").strip()
        if not text:
            continue
        paragraphs = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
        buffer: list[str] = []
        length = 0
        part = 1
        for paragraph in paragraphs:
            # Avoid splitting a paragraph unless it is itself larger than the chunk target.
            pieces = [paragraph[i:i + chunk_chars] for i in range(0, len(paragraph), chunk_chars)] if len(paragraph) > chunk_chars else [paragraph]
            for piece in pieces:
                if buffer and length + len(piece) + 1 > chunk_chars:
                    chunks.append({
                        "chunk_id": f"chunk-{len(chunks)+1:04d}",
                        "section": section_name,
                        "section_part": part,
                        "text": "\n".join(buffer),
                        "char_count": length
                    })
                    part += 1
                    buffer, length = [], 0
                buffer.append(piece)
                length += len(piece) + 1
        if buffer:
            chunks.append({
                "chunk_id": f"chunk-{len(chunks)+1:04d}",
                "section": section_name,
                "section_part": part,
                "text": "\n".join(buffer),
                "char_count": length
            })
    return chunks


def _ocr_images(image_dir: Path) -> list[dict[str, str]]:
    results = []
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return [{"warning": "OCR requested but optional dependencies are missing. Install with: pip install -e '.[ocr]'"}]
    image_files = sorted(p for p in image_dir.rglob("*") if p.is_file())
    for p in image_files:
        try:
            with Image.open(p) as im:
                text = pytesseract.image_to_string(im, lang=os.environ.get("DOCX_READER_OCR_LANG", "eng+ind"))
            results.append({"file": str(p), "text": text.strip()})
        except Exception as exc:
            results.append({"file": str(p), "warning": f"OCR failed: {type(exc).__name__}: {exc}"})
    return results


def extract_docx(path: str | Path, output_dir: str | Path | None = None,
                 ocr_images: bool = False, chunk_chars: int = DEFAULT_CHUNK_CHARS) -> dict[str, Any]:
    p = _validate_docx(path)
    if chunk_chars < 500 or chunk_chars > 50000:
        raise ValueError("chunk_chars must be between 500 and 50000.")
    out_root = Path(output_dir).expanduser().resolve() if output_dir else DEFAULT_OUTPUT
    doc_dir = out_root / f"{_safe_filename(p.stem)}-{hashlib.sha256(str(p).encode()).hexdigest()[:8]}"
    doc_dir.mkdir(parents=True, exist_ok=True)
    image_dir = doc_dir / "images"
    image_dir.mkdir(exist_ok=True)

    extracted = _extract_sections(p, image_dir=image_dir)
    sections = extracted["sections"]
    chunks = _chunks_from_sections(sections, chunk_chars)
    ocr_results = _ocr_images(image_dir) if ocr_images else []
    metadata = _metadata(p)
    warnings = [
        "DOCX pagination is not stable; references use chunk IDs and section names, not page numbers.",
        "Text boxes, SmartArt, chart labels, embedded OLE files, tracked changes, and complex equations may need additional extraction or OCR."
    ]
    inventory = metadata["package_inventory"]
    if inventory["tracked_change_markers"]:
        warnings.append("Tracked-change XML markers were found. This baseline parser does not reconstruct a complete 'final' or 'original' revision view.")
    if inventory["textboxes"]:
        warnings.append("Text box content markers were found. Verify whether their text appears in extracted body text.")
    if inventory["charts"] or inventory["diagrams"] or inventory["embedded_objects"]:
        warnings.append("Charts, diagrams, or embedded objects exist in the package; their semantic content may not be fully represented in extracted text.")
    if not chunks:
        warnings.append("No text chunks were extracted. The document may be image-only, empty, encrypted, or use unsupported structures.")
    if ocr_images and any("warning" in x for x in ocr_results):
        warnings.append("One or more OCR tasks could not run or failed.")

    manifest = {
        "schema_version": "1.0",
        "metadata": metadata,
        "counts": {
            "body_chars": len(sections["body"]),
            "header_chars": len(sections["header"]),
            "footer_chars": len(sections["footer"]),
            "footnotes_chars": len(sections["footnotes"]),
            "endnotes_chars": len(sections["endnotes"]),
            "comments": len(extracted["comments"]),
            "chunks": len(chunks),
            "images_extracted": sum(1 for x in image_dir.iterdir() if x.is_file()),
            "ocr_items": len(ocr_results),
        },
        "warnings": warnings,
        "chunk_index": [
            {"chunk_id": c["chunk_id"], "section": c["section"], "char_count": c["char_count"],
             "preview": c["text"][:220].replace("\n", " ")}
            for c in chunks
        ],
    }

    (doc_dir / "sections.json").write_text(json.dumps(sections, ensure_ascii=False, indent=2), encoding="utf-8")
    (doc_dir / "comments.json").write_text(json.dumps(extracted["comments"], ensure_ascii=False, indent=2), encoding="utf-8")
    (doc_dir / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    (doc_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (doc_dir / "properties.json").write_text(json.dumps(extracted["docx2python_properties"], ensure_ascii=False, indent=2), encoding="utf-8")
    if ocr_images:
        (doc_dir / "ocr.json").write_text(json.dumps(ocr_results, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        f"# Extracted document: {p.name}",
        "",
        f"- SHA-256: `{metadata['sha256']}`",
        f"- Chunks: {len(chunks)}",
        "",
        "## Body",
        sections["body"],
        "",
        "## Headers",
        sections["header"],
        "",
        "## Footers",
        sections["footer"],
        "",
        "## Footnotes",
        sections["footnotes"],
        "",
        "## Endnotes",
        sections["endnotes"],
    ]
    if extracted["comments"]:
        md.extend(["", "## Comments"])
        for c in extracted["comments"]:
            md.append(f"- **{c.get('author','')}** ({c.get('date','')}), anchor: {c.get('reference_text','')}\n  {c.get('comment_text', c.get('raw',''))}")
    if ocr_results:
        md.extend(["", "## OCR results"])
        for item in ocr_results:
            md.append(f"\n### {item.get('file','OCR warning')}\n\n{item.get('text', item.get('warning',''))}")
    (doc_dir / "document.md").write_text("\n".join(md), encoding="utf-8")

    for c in chunks:
        (doc_dir / f"{c['chunk_id']}.txt").write_text(c["text"], encoding="utf-8")

    return {
        "ok": True,
        "output_dir": str(doc_dir),
        "manifest": manifest,
        "comments": extracted["comments"],
        "ocr_results": ocr_results if ocr_images else [],
        "next_steps": [
            "Use search_docx to find relevant topics.",
            "Use list_docx_chunks to see all chunk IDs and previews.",
            "Read every chunk in batches if you need a full-document review; track processed chunk IDs."
        ]
    }


def inspect_docx(path: str | Path, ocr_images: bool = False) -> dict[str, Any]:
    result = extract_docx(path, ocr_images=ocr_images)
    return {
        "ok": result["ok"],
        "file": result["manifest"]["metadata"]["file_name"],
        "metadata": result["manifest"]["metadata"],
        "counts": result["manifest"]["counts"],
        "warnings": result["manifest"]["warnings"],
        "output_dir": result["output_dir"],
    }


def _load_bundle(path: str | Path, output_dir: str | Path | None = None) -> tuple[Path, list[dict[str, Any]]]:
    p = _validate_docx(path)
    out_root = Path(output_dir).expanduser().resolve() if output_dir else DEFAULT_OUTPUT
    doc_dir = out_root / f"{_safe_filename(p.stem)}-{hashlib.sha256(str(p).encode()).hexdigest()[:8]}"
    chunks_path = doc_dir / "chunks.json"
    if not chunks_path.exists():
        result = extract_docx(p, output_dir=out_root)
        doc_dir = Path(result["output_dir"])
        chunks_path = doc_dir / "chunks.json"
    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    return doc_dir, chunks


def search_docx(path: str | Path, query: str, max_results: int = 10,
                output_dir: str | Path | None = None) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("query cannot be empty.")
    if not 1 <= max_results <= 100:
        raise ValueError("max_results must be between 1 and 100.")
    doc_dir, chunks = _load_bundle(path, output_dir)
    q = query.casefold()
    results = []
    for c in chunks:
        text = c["text"]
        pos = text.casefold().find(q)
        if pos >= 0:
            results.append({
                "chunk_id": c["chunk_id"], "section": c["section"],
                "match_index": pos, "snippet": text[max(0, pos-180):min(len(text), pos+len(query)+260)]
            })
            if len(results) >= max_results:
                break
    return {"query": query, "result_count": len(results), "results": results, "output_dir": str(doc_dir)}


def list_docx_chunks(path: str | Path, offset: int = 0, limit: int = 20,
                     output_dir: str | Path | None = None) -> dict[str, Any]:
    if offset < 0 or not 1 <= limit <= 100:
        raise ValueError("offset must be >= 0 and limit must be between 1 and 100.")
    doc_dir, chunks = _load_bundle(path, output_dir)
    items = [{
        "chunk_id": c["chunk_id"], "section": c["section"], "char_count": c["char_count"],
        "preview": c["text"][:260].replace("\n", " ")
    } for c in chunks[offset:offset+limit]]
    return {"total_chunks": len(chunks), "offset": offset, "returned": len(items), "chunks": items, "output_dir": str(doc_dir)}


def read_docx_chunk(path: str | Path, chunk_id: str,
                    output_dir: str | Path | None = None) -> dict[str, Any]:
    doc_dir, chunks = _load_bundle(path, output_dir)
    for c in chunks:
        if c["chunk_id"] == chunk_id:
            return {"chunk_id": c["chunk_id"], "section": c["section"], "char_count": c["char_count"], "text": c["text"]}
    raise ValueError(f"Unknown chunk_id {chunk_id!r}. Use list_docx_chunks first.")
