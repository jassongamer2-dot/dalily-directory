import fitz
import numpy as np
import cv2


def pdf_page_to_array(pdf_path: str, page_num: int, dpi: int = 200) -> np.ndarray:
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)


def array_to_png_bytes(img: np.ndarray) -> bytes:
    ok, encoded = cv2.imencode(".png", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    if not ok:
        raise ValueError("PNG encoding failed")
    return encoded.tobytes()
