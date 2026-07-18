# worker/extraction/preprocess.py — full file
import cv2
import numpy as np


def preprocess_for_ocr(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    coords = np.column_stack(np.where(gray < 250))

    if coords.shape[0] == 0:
        deskewed = gray  # blank/near-blank page — nothing to deskew against, skip straight through
    else:
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        h, w = gray.shape
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        deskewed = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    denoised = cv2.fastNlMeansDenoising(deskewed, h=10)
    return cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11)
