import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, Dict, Any

def get_image_metadata(image_path: str) -> Dict[str, Any]:
    """Extract dimensions and basic metadata."""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            format_name = img.format
            mode = img.mode
            dpi = img.info.get("dpi", (150, 150))
            if isinstance(dpi, tuple) and len(dpi) > 0:
                dpi_val = float(dpi[0])
            else:
                dpi_val = 150.0
            return {
                "width": width,
                "height": height,
                "aspect_ratio": round(width / max(height, 1), 2),
                "format": format_name,
                "mode": mode,
                "estimated_dpi": dpi_val if dpi_val > 50 else 150.0
            }
    except Exception as e:
        return {
            "width": 800,
            "height": 600,
            "aspect_ratio": 1.33,
            "format": "JPEG",
            "mode": "RGB",
            "estimated_dpi": 150.0,
            "error": str(e)
        }

def preprocess_image(image_path: str) -> np.ndarray:
    """
    Apply OpenCV preprocessing:
    - Grayscale conversion
    - Contrast Limited Adaptive Histogram Equalization (CLAHE)
    - Bilateral filter for noise reduction while preserving text edges
    """
    img = cv2.imread(str(image_path))
    if img is None:
        pil_img = Image.open(image_path).convert("RGB")
        img = np.array(pil_img)[:, :, ::-1]

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Bilateral filter to smooth texture while keeping sharp text edges
    denoised = cv2.bilateralFilter(enhanced, d=5, sigmaColor=50, sigmaSpace=50)

    return denoised
