import pytest
from app.ocr.declaration_parser import parse_declarations_from_ocr
from app.ocr.text_normalizer import detect_quantity_ambiguity, normalize_quantity

def test_detect_quantity_ambiguity():
    ambig = detect_quantity_ambiguity("500 9")
    assert ambig is not None
    assert "may represent \"500 g\"" in ambig

    non_std = detect_quantity_ambiguity("200 gms")
    assert non_std is not None
    assert "Non-standard unit symbol" in non_std

    normal = detect_quantity_ambiguity("500 g")
    assert normal is None

def test_normalize_quantity():
    num, unit, display = normalize_quantity("Net Wt. 1 kg")
    assert num == "1"
    assert unit == "kg"
    assert display == "1 kg"

    num2, unit2, display2 = normalize_quantity("250 ml")
    assert num2 == "250"
    assert unit2 == "ml"
    assert display2 == "250 ml"

def test_declaration_parser_mrp_detection():
    sample_ocr = {
        "raw_text": "Product Name\nMRP Rs. 150.00 (Inclusive of all taxes)\nNET QTY: 500 g\nMFD: 08/2026",
        "lines": [
            {"text": "MRP Rs. 150.00 (Inclusive of all taxes)", "x": 10, "y": 20, "width": 200, "height": 30, "confidence": 95.0}
        ],
        "font_metrics": {"avg_char_height_px": 18.0, "approx_min_font_mm": 2.5}
    }
    decl = parse_declarations_from_ocr(sample_ocr)
    assert decl["mrp"]["status"] == "DETECTED"
    assert decl["mrp"]["numeric_value"] == 150.0
    assert decl["mrp"]["tax_inclusive_declared"] is True
    assert decl["net_quantity"]["status"] == "DETECTED"
    assert decl["net_quantity"]["value"] == "500 g"

def test_declaration_parser_consumer_care():
    sample_ocr = {
        "raw_text": "Manufactured by ABC Pvt Ltd, Sector 5, Pune - 411001\nCustomer Care Helpline: 1800-222-3344\nEmail: contact@abc.in",
        "lines": [],
        "font_metrics": {}
    }
    decl = parse_declarations_from_ocr(sample_ocr)
    assert decl["consumer_care"]["status"] == "DETECTED"
    assert decl["consumer_care"]["is_complete"] is True
    assert "1800-222-3344" in decl["consumer_care"]["phone"]
    assert decl["consumer_care"]["email"] == "contact@abc.in"
    assert decl["manufacturer"]["pin_code"] == "411001"
