import re
from typing import Dict, Any, Optional, Tuple

STANDARD_UNITS = {
    # Mass
    "g": "g", "gm": "g", "gms": "g", "gram": "g", "grams": "g",
    "kg": "kg", "kgs": "kg", "kilo": "kg", "kilogram": "kg", "kilograms": "kg",
    # Volume
    "ml": "ml", "mls": "ml", "millilitre": "ml", "milliliter": "ml",
    "l": "l", "lt": "l", "ltr": "l", "ltrs": "l", "liter": "l", "litre": "l",
    # Length / Area
    "m": "m", "meter": "m", "metre": "m",
    "cm": "cm", "centimeter": "cm",
    "mm": "mm", "millimeter": "mm",
    # Count / Units
    "n": "N", "u": "U", "nos": "N", "no": "N", "units": "U", "unit": "U", "pieces": "N", "pc": "N", "pcs": "N"
}

LEGAL_METRIC_SYMBOLS = {"g", "kg", "ml", "l", "m", "cm", "mm", "N", "U", "sq m", "cu m"}

def clean_ocr_text(text: str) -> str:
    """Basic cleanup of raw OCR text."""
    if not text:
        return ""
    # Replace weird invisible characters
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', ' ', text)
    # Unify linebreaks and whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def detect_quantity_ambiguity(raw_match: str) -> Optional[str]:
    """
    Detects if raw OCR contains common unit ambiguities,
    such as '500 9' representing '500 g'.
    """
    # Check for digit followed by space and 9, which is a classic Tesseract error for 'g'
    ambiguous_9_match = re.search(r'(\d+)\s+9\b', raw_match, re.IGNORECASE)
    if ambiguous_9_match:
        val = ambiguous_9_match.group(1)
        return f'Possible OCR ambiguity: "{raw_match}" may represent "{val} g" (misrecognition of "g" as "9").'

    # Check for non-standard colloquial units like 'gms', 'kgs', 'ltrs'
    non_std_match = re.search(r'(\d+(?:\.\d+)?)\s*(gms|kgs|ltrs|pcs)\b', raw_match, re.IGNORECASE)
    if non_std_match:
        unit = non_std_match.group(2).lower()
        std_equiv = "g" if unit == "gms" else ("kg" if unit == "kgs" else ("l" if unit == "ltrs" else "N"))
        return f'Non-standard unit symbol "{unit}" detected. Legal Metrology Rule 12 specifies standard symbol "{std_equiv}".'

    return None

def normalize_quantity(raw_str: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Normalizes quantity string into (numeric_value, standard_unit, display_str).
    Example: '500 gm' -> ('500', 'g', '500 g')
    """
    # Match number and unit
    m = re.search(r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)', raw_str)
    if not m:
        return None, None, None
    num_str = m.group(1)
    unit_str = m.group(2).lower()
    std_unit = STANDARD_UNITS.get(unit_str, unit_str)
    
    return num_str, std_unit, f"{num_str} {std_unit}"
