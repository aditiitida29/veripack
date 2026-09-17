import os
import shutil
import pytesseract
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from app.config import settings
from app.ocr.preprocessor import preprocess_image, get_image_metadata

# Ensure Tesseract binary is set
if os.path.exists(settings.TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
else:
    fallback_bin = shutil.which("tesseract")
    if fallback_bin:
        pytesseract.pytesseract.tesseract_cmd = fallback_bin

def run_ocr_with_boxes(image_path: str) -> Dict[str, Any]:
    """
    Runs Tesseract OCR extracting raw text, words, and line-level bounding boxes.
    Calculates readability and approximate font height distribution.
    """
    meta = get_image_metadata(image_path)
    width = meta["width"]
    height = meta["height"]
    estimated_dpi = meta["estimated_dpi"]

    try:
        # Preprocess with OpenCV
        processed_cv = preprocess_image(image_path)
        processed_pil = Image.fromarray(processed_cv)
        
        # Primary OCR extraction
        data = pytesseract.image_to_data(
            processed_pil, 
            output_type=pytesseract.Output.DICT,
            config="--psm 3"
        )
        
        raw_text = pytesseract.image_to_string(processed_pil, config="--psm 3")
        
        # If text is too short, try original image as fallback
        if len(raw_text.strip()) < 10:
            with Image.open(image_path) as orig:
                raw_text_orig = pytesseract.image_to_string(orig, config="--psm 3")
                if len(raw_text_orig.strip()) > len(raw_text.strip()):
                    data = pytesseract.image_to_data(orig, output_type=pytesseract.Output.DICT, config="--psm 3")
                    raw_text = raw_text_orig

    except Exception as e:
        # Graceful fallback in case of OCR error
        return {
            "raw_text": "",
            "words": [],
            "lines": [],
            "image_size": {"width": width, "height": height},
            "font_metrics": {
                "avg_char_height_px": 0,
                "approx_min_font_mm": 0,
                "readability_score": 0,
                "disclaimer": "Preliminary visual assessment. Requires physical/legal verification."
            },
            "error": str(e)
        }

    words: List[Dict[str, Any]] = []
    lines_dict: Dict[str, Dict[str, Any]] = {}
    n_boxes = len(data["text"])
    
    char_heights = []

    for i in range(n_boxes):
        word_text = data["text"][i].strip()
        conf = float(data["conf"][i])
        
        if not word_text:
            continue
            
        x = int(data["left"][i])
        y = int(data["top"][i])
        w = int(data["width"][i])
        h = int(data["height"][i])
        block_num = data["block_num"][i]
        line_num = data["line_num"][i]
        
        word_item = {
            "text": word_text,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "confidence": conf if conf >= 0 else 50.0,
            "line_num": line_num,
            "block_num": block_num
        }
        words.append(word_item)
        
        if h > 4 and conf > 20:
            char_heights.append(h)

        line_key = f"{block_num}_{line_num}"
        if line_key not in lines_dict:
            lines_dict[line_key] = {
                "text": word_text,
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "confidences": [conf if conf >= 0 else 50.0],
                "words": [word_item]
            }
        else:
            prev = lines_dict[line_key]
            new_x = min(prev["x"], x)
            new_y = min(prev["y"], y)
            new_right = max(prev["x"] + prev["width"], x + w)
            new_bottom = max(prev["y"] + prev["height"], y + h)
            
            lines_dict[line_key] = {
                "text": prev["text"] + " " + word_text,
                "x": new_x,
                "y": new_y,
                "width": new_right - new_x,
                "height": new_bottom - new_y,
                "confidences": prev["confidences"] + [conf if conf >= 0 else 50.0],
                "words": prev["words"] + [word_item]
            }

    lines = []
    for k, v in lines_dict.items():
        avg_conf = sum(v["confidences"]) / max(len(v["confidences"]), 1)
        lines.append({
            "text": v["text"],
            "x": v["x"],
            "y": v["y"],
            "width": v["width"],
            "height": v["height"],
            "confidence": round(avg_conf, 1),
            "words": v["words"]
        })

    # Sort lines top-to-bottom
    lines.sort(key=lambda item: (item["y"] // 20, item["x"]))

    # Font size & readability assessment
    avg_h_px = (sum(char_heights) / len(char_heights)) if char_heights else 16.0
    # Approximate mm conversion: mm = (px * 25.4) / DPI
    approx_mm = round((avg_h_px * 25.4) / estimated_dpi, 2)
    overall_conf = round(sum([w["confidence"] for w in words]) / max(len(words), 1), 1) if words else 0.0

    return {
        "raw_text": raw_text.strip(),
        "words": words,
        "lines": lines,
        "image_size": {"width": width, "height": height},
        "font_metrics": {
            "avg_char_height_px": round(avg_h_px, 1),
            "approx_min_font_mm": approx_mm,
            "overall_ocr_confidence": overall_conf,
            "total_words_detected": len(words),
            "disclaimer": "Preliminary visual assessment. Requires physical/legal verification."
        }
    }
