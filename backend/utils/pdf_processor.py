"""
PDF → page images → OCR → combined text pipeline.

Strategy:
  • Uses PyMuPDF (fitz) to render each PDF page as a high-DPI PNG in memory.
  • Sends each page image to the Nemotron OCR provider (which automatically
    handles large pages via the NVCF Asset API).
  • Joins all page transcripts into a single document string.

No temporary files are written to disk; everything is held in memory.
"""

from __future__ import annotations

import io
import logging
from typing import Callable

try:
    import fitz  # PyMuPDF
except ImportError as exc:
    raise ImportError(
        "PyMuPDF is required for PDF processing: pip install pymupdf"
    ) from exc

try:
    from providers.nvidia_ocr_client import ocr_image
except ModuleNotFoundError:
    from backend.providers.nvidia_ocr_client import ocr_image

log = logging.getLogger(__name__)

# Render resolution.  150 DPI is a good balance: ~1240×1754 px for A4,
# produces clean glyphs for OCR while keeping file sizes reasonable.
DEFAULT_DPI = int(150)

# Maximum pages to OCR (guard against huge files at a hackathon demo)
MAX_PAGES = int(30)


def pdf_to_page_images(pdf_bytes: bytes, dpi: int = DEFAULT_DPI) -> list[bytes]:
    """
    Render *pdf_bytes* to a list of PNG byte strings (one per page).

    Raises ValueError for encrypted/corrupt PDFs.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"Could not open PDF: {exc}") from exc

    if doc.is_encrypted:
        raise ValueError("PDF is password-protected — cannot process")

    page_count = min(len(doc), MAX_PAGES)
    matrix = fitz.Matrix(dpi / 72, dpi / 72)  # 72 pt = 1 inch
    images: list[bytes] = []

    for page_num in range(page_count):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        png_bytes = pix.tobytes("png")
        images.append(png_bytes)
        log.debug("Rendered PDF page %d/%d  (%d bytes)", page_num + 1, page_count, len(png_bytes))

    doc.close()
    return images


def ocr_pdf(
    pdf_bytes: bytes,
    progress_cb: Callable[[int, int], None] | None = None,
    dpi: int = DEFAULT_DPI,
) -> dict:
    """
    Full PDF → OCR pipeline.

    Parameters
    ----------
    pdf_bytes   : raw PDF file contents
    progress_cb : optional callback(current_page, total_pages) for streaming
    dpi         : render resolution (default 150)

    Returns
    -------
    dict with keys:
      page_texts   : list[str]   — OCR text per page
      full_text    : str         — pages joined with page-break markers
      page_count   : int
      errors       : list[str]   — per-page OCR errors (empty on success)
      provider     : str
    """
    page_images = pdf_to_page_images(pdf_bytes, dpi=dpi)
    total = len(page_images)
    page_texts: list[str] = []
    errors: list[str] = []

    for idx, png_bytes in enumerate(page_images):
        if progress_cb:
            progress_cb(idx + 1, total)
        try:
            text = ocr_image(png_bytes, mime_type="image/png")
            page_texts.append(text.strip())
        except RuntimeError as exc:
            err_msg = f"Page {idx + 1} OCR failed: {exc}"
            log.warning(err_msg)
            errors.append(err_msg)
            page_texts.append(f"[OCR failed for page {idx + 1}]")

    # Combine all pages with clear separators for downstream analysis
    full_text = "\n\n".join(
        f"=== Page {i + 1} ===\n{t}" for i, t in enumerate(page_texts)
    )

    return {
        "page_texts": page_texts,
        "full_text": full_text,
        "page_count": total,
        "errors": errors,
        "provider": "nvidia/nemotron-ocr-v1",
    }
