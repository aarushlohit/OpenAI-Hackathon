"""Test script for PDF rendering and Nemotron OCR pipeline."""

import os
import sys
from pathlib import Path
import fitz

# Ensure backend directory is in path
sys.path.insert(0, str(Path(__file__).parent))

from utils.pdf_processor import ocr_pdf
from providers.nvcf_asset_client import should_use_asset_api


def create_test_pdf(filename: str, text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    # Add a lot of text to make it realistic
    y = 50
    for line in text.split("\n"):
        page.insert_text((50, y), line, fontsize=12)
        y += 20
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def main():
    print("=== Creating Test PDF ===")
    test_text = (
        "CONFIDENTIAL OFFER LETTER\n"
        "Date: May 29, 2026\n"
        "Candidate Name: John Doe\n"
        "Position: Software Engineering Intern\n"
        "Company Name: TechNovation Solutions\n"
        "We are pleased to offer you an internship. However, to confirm your onboarding,\n"
        "you must make a refundable security deposit of 3,500 INR via UPI to confirm your position.\n"
        "Please send the payment to payment@upi and submit a screenshot to your coordinator on Telegram.\n"
        "Failure to do so within 24 hours will result in automatic cancellation of this offer."
    )
    pdf_bytes = create_test_pdf("test_offer.pdf", test_text)
    print(f"Test PDF generated: {len(pdf_bytes)} bytes")

    # Save it to disk for manual inspection/web testing
    Path("test_offer.pdf").write_bytes(pdf_bytes)
    print("Saved test_offer.pdf to current directory.")

    print("\n=== Running PDF OCR Pipeline ===")
    try:
        # Run OCR
        result = ocr_pdf(pdf_bytes)
        print("\nOCR Execution Result:")
        print(f"Page Count: {result['page_count']}")
        print(f"Provider: {result['provider']}")
        print(f"Errors: {result['errors']}")
        print("\n--- Extracted Text ---")
        print(result["full_text"])
        print("----------------------")
    except Exception as e:
        print(f"OCR Pipeline Failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
