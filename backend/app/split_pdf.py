# split_pdf.py — run once locally on your machine, not part of the deployed project
import fitz


def split_pdf(input_path: str, pages_per_chunk: int = 75):
    doc = fitz.open(input_path)
    total = len(doc)
    for start in range(0, total, pages_per_chunk):
        end = min(start + pages_per_chunk, total)
        chunk = fitz.open()
        chunk.insert_pdf(doc, from_page=start, to_page=end - 1)
        chunk.save(f"{input_path.rsplit('.', 1)[0]}_pages_{start+1}-{end}.pdf")
        chunk.close()


split_pdf("part1.pdf")
