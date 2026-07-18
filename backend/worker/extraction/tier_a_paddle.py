from paddleocr import PaddleOCR
import pytesseract
import numpy as np

# Initialize once to avoid reloading model weights
paddle_ocr = PaddleOCR(lang="ar", use_angle_cls=True)
CONFIDENCE_CROSSCHECK_THRESHOLD = 0.75


def extract_page_tier_a(image: np.ndarray) -> list[dict]:
    # PaddleOCR expects a numpy array from preprocess_for_ocr
    result = paddle_ocr.ocr(image, cls=False)

    # Paddle returns a list of results per page (we process 1 page at a time)
    if not result or result[0] is None:
        return []

    lines = []
    for line in result[0]:
        box, (text, confidence) = line
        lines.append({"text": text, "confidence": confidence, "bbox": box})

    # Cross-check low confidence lines with Tesseract
    for line in lines:
        if line["confidence"] < CONFIDENCE_CROSSCHECK_THRESHOLD:
            # Tesseract needs a specific format, keep it simple for now
            crosscheck = pytesseract.image_to_string(image, lang="ara").strip()
            line["tesseract_agrees"] = crosscheck == line["text"]

    return lines
