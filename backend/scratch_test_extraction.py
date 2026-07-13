# a throwaway script, backend/scratch_test_extraction.py
import fitz
from worker.extraction.pdf_to_images import pdf_page_to_array
from worker.extraction.preprocess import preprocess_for_ocr
from worker.extraction.tier_a_paddle import extract_page_tier_a
from worker.extraction.structure_entries import structure_page

PDF_PATH = "path/to/sample_3_pages.pdf"
for page_num in range(len(fitz.open(PDF_PATH))):
    arr = pdf_page_to_array(PDF_PATH, page_num)
    lines = extract_page_tier_a(preprocess_for_ocr(arr))
    entries = structure_page(lines)
    print(f"--- page {page_num} ---")
    for e in entries:
        print(e)
