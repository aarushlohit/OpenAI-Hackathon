"""
PDF → page images → OCR → combined text pipeline.

Strategy:
  • Uses PyMuPDF (fitz) to render each PDF page as a JPEG in memory.
  • JPEG is used instead of PNG — it compresses text-heavy offer letters
    ~8x better, keeping most pages under the 180 KB inline base64 limit
    without needing the NVCF Asset API.
  • Sends each page image to the Nemotron OCR provider (which automatically
    handles unusually large pages via the NVCF Asset API as a fallback).
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

# Render resolution. 100 DPI gives a good balance of OCR quality vs file size
# for A4 text documents. JPEG at 100 DPI ≈ 80–150 KB for typical offer letters,
# well within the 180 KB inline limit for Nemotron OCR.
DEFAULT_DPI = int(100)

# JPEG quality setting (85 is visually lossless for text at 100 DPI)
JPEG_QUALITY = 85

# Maximum pages to OCR (guard against huge files at a hackathon demo)
MAX_PAGES = int(30)


def pdf_to_page_images(pdf_bytes: bytes, dpi: int = DEFAULT_DPI) -> list[bytes]:
    """
    Render *pdf_bytes* to a list of JPEG byte strings (one per page).

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
        jpeg_bytes = pix.tobytes("jpg", jpg_quality=JPEG_QUALITY)
        images.append(jpeg_bytes)
        log.debug(
            "Rendered PDF page %d/%d  (%d KB JPEG)",
            page_num + 1, page_count, len(jpeg_bytes) // 1024,
        )

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
    dpi         : render resolution (default 100)

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

    for idx, jpeg_bytes in enumerate(page_images):
        if progress_cb:
            progress_cb(idx + 1, total)
        try:
            # Send as JPEG — smaller payload, widely supported by Nemotron OCR
            text = ocr_image(jpeg_bytes, mime_type="image/jpeg")
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

