from typing import Dict, Any, Optional

def validate_mrp(mrp_data: Dict[str, Any], rule_config: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates Maximum Retail Price against Rule 6(1)(e)."""
    status = mrp_data.get("status")
    val = mrp_data.get("value")
    tax_inclusive = mrp_data.get("tax_inclusive_declared", False)
    bb = mrp_data.get("bounding_box")
    conf = mrp_data.get("confidence", 0.0)

    if status == "MISSING" or not val:
        return {
            "status": "FAIL",
            "message": "Maximum Retail Price (MRP) declaration was not detected on the package label.",
            "evidence": "No matching MRP or price pattern found in OCR text.",
            "confidence": 0.0,
            "bounding_box": None
        }

    if not tax_inclusive:
        return {
            "status": "WARNING",
            "message": f"MRP detected ({val}), but mandatory phrase 'inclusive of all taxes' or 'incl. of all taxes' was not explicitly detected.",
            "evidence": f"Found '{mrp_data.get('raw_text')}' without adjacent tax inclusion declaration.",
            "confidence": conf,
            "bounding_box": bb
        }

    return {
        "status": "PASS",
        "message": f"MRP compliant: {val} (inclusive of all taxes).",
        "evidence": mrp_data.get("raw_text"),
        "confidence": conf,
        "bounding_box": bb
    }

def validate_net_quantity(qty_data: Dict[str, Any], rule_config: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates Net Quantity against Rule 6(1)(c), Rule 11 & Rule 12."""
    status = qty_data.get("status")
    val = qty_data.get("value")
    unit = qty_data.get("unit")
    is_std = qty_data.get("is_standard_unit", False)
    bb = qty_data.get("bounding_box")
    conf = qty_data.get("confidence", 0.0)
    notes = qty_data.get("notes", "")

    if status == "MISSING" or not val:
        return {
            "status": "FAIL",
            "message": "Net quantity declaration was not detected in the uploaded packaging label.",
            "evidence": "No weight, volume, or measure expression found in OCR stream.",
            "confidence": 0.0,
            "bounding_box": None
        }

    if status == "AMBIGUOUS":
        return {
            "status": "WARNING",
            "message": f"Review Required: Net quantity expression is ambiguous ({val}). {notes}",
            "evidence": f"Raw OCR detected: '{qty_data.get('raw_text')}'",
            "confidence": conf,
            "bounding_box": bb
        }

    if not is_std:
        return {
            "status": "WARNING",
            "message": f"Non-standard unit symbol detected ('{unit}'). Second Schedule requires metric standard abbreviations.",
            "evidence": qty_data.get("raw_text"),
            "confidence": conf,
            "bounding_box": bb
        }

    return {
        "status": "PASS",
        "message": f"Net quantity compliant: {val}.",
        "evidence": qty_data.get("raw_text"),
        "confidence": conf,
        "bounding_box": bb
    }

def validate_manufacturing_date(date_data: Dict[str, Any], rule_config: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates Month & Year of Manufacture / Packing against Rule 6(1)(d)."""
    status = date_data.get("status")
    val = date_data.get("value")
    bb = date_data.get("bounding_box")
    conf = date_data.get("confidence", 0.0)

    if status == "MISSING" or not val:
        return {
            "status": "FAIL",
            "message": "Month and year of manufacture or pre-packing declaration was not detected.",
            "evidence": "No MFD/MFG/PKD date pattern identified in label.",
            "confidence": 0.0,
            "bounding_box": None
        }

    return {
        "status": "PASS",
        "message": f"Date of manufacture/packing declared: {val} ({date_data.get('type', 'MFD')}).",
        "evidence": date_data.get("raw_text"),
        "confidence": conf,
        "bounding_box": bb
    }

def validate_manufacturer(mfg_data: Dict[str, Any], rule_config: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates Manufacturer/Packer name and complete address against Rule 6(1)(a)."""
    status = mfg_data.get("status")
    name = mfg_data.get("name")
    address = mfg_data.get("address")
    pin = mfg_data.get("pin_code")
    has_complete = mfg_data.get("has_complete_address", False)
    bb = mfg_data.get("bounding_box")
    conf = mfg_data.get("confidence", 0.0)

    if status == "MISSING" or not name:
        return {
            "status": "FAIL",
            "message": "Name and complete address of the manufacturer / packer was not detected.",
            "evidence": "No manufacturer or packer declaration identified.",
            "confidence": 0.0,
            "bounding_box": None
        }

    if not pin:
        return {
            "status": "WARNING",
            "message": f"Manufacturer name detected ({name}), but complete address is missing 6-digit Postal Index Number (PIN Code).",
            "evidence": f"Observed address snippet: '{address}'",
            "confidence": conf,
            "bounding_box": bb
        }

    return {
        "status": "PASS",
        "message": f"Manufacturer and complete address with PIN ({pin}) detected: {name}.",
        "evidence": f"{name}, {address}",
        "confidence": conf,
        "bounding_box": bb
    }

def validate_consumer_care(cc_data: Dict[str, Any], rule_config: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates Consumer Care details against Rule 6(1)(n)."""
    status = cc_data.get("status")
    phone = cc_data.get("phone")
    email = cc_data.get("email")
    is_complete = cc_data.get("is_complete", False)
    bb = cc_data.get("bounding_box")
    conf = cc_data.get("confidence", 0.0)

    if status == "MISSING" or (not phone and not email):
        return {
            "status": "FAIL",
            "message": "Mandatory Consumer Care contact details (telephone number and email address) were not detected.",
            "evidence": "No consumer care telephone or email found on packaging.",
            "confidence": 0.0,
            "bounding_box": None
        }

    if not is_complete:
        missing_item = "email address" if not email else "telephone helpline"
        return {
            "status": "WARNING",
            "message": f"Incomplete consumer care details: {missing_item} is missing. Rule 6(1)(n) mandates both telephone and email.",
            "evidence": f"Phone: {phone or 'None'}, Email: {email or 'None'}",
            "confidence": conf,
            "bounding_box": bb
        }

    return {
        "status": "PASS",
        "message": f"Consumer care details complete (Phone: {phone}, Email: {email}).",
        "evidence": f"Helpline: {phone} | Email: {email}",
        "confidence": conf,
        "bounding_box": bb
    }

def validate_country_of_origin(coo_data: Dict[str, Any], is_imported: bool, rule_config: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates Country of Origin against Rule 6(10)."""
    status = coo_data.get("status")
    val = coo_data.get("value")
    bb = coo_data.get("bounding_box")
    conf = coo_data.get("confidence", 0.0)

    if not is_imported and not val:
        return {
            "status": "NOT_APPLICABLE",
            "message": "Country of origin check not strictly mandatory for domestic packaged commodities unless claimed.",
            "evidence": "Domestic product registration.",
            "confidence": 100.0,
            "bounding_box": None
        }

    if is_imported and (status == "MISSING" or not val):
        return {
            "status": "FAIL",
            "message": "Country of origin declaration is mandatory for imported packaged commodities under Rule 6(10) but was not detected.",
            "evidence": "Product flagged as imported, but no country of origin text found.",
            "confidence": 0.0,
            "bounding_box": None
        }

    return {
        "status": "PASS",
        "message": f"Country of origin declared: {val}.",
        "evidence": f"Declared Origin: {val}",
        "confidence": conf,
        "bounding_box": bb
    }

def validate_readability(readability_data: Dict[str, Any], rule_config: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates font readability & character height approximation under Rule 7 Table-I."""
    approx_mm = readability_data.get("approx_min_font_mm", 2.0)
    avg_px = readability_data.get("avg_char_height_px", 16.0)
    conf = readability_data.get("overall_ocr_confidence", 80.0)

    if approx_mm < 1.0 or avg_px < 10.0:
        return {
            "status": "WARNING",
            "message": f"Preliminary visual assessment: Estimated character height ({approx_mm} mm / {avg_px} px) appears below recommended legibility threshold. Requires physical/legal verification.",
            "evidence": f"Estimated font height: {approx_mm} mm (approx). Overall OCR clarity: {conf}%.",
            "confidence": 70.0,
            "bounding_box": None
        }

    return {
        "status": "PASS",
        "message": f"Conspicuous and legible font detected (approx {approx_mm} mm). Preliminary visual assessment. Requires physical/legal verification.",
        "evidence": f"Estimated font height: {approx_mm} mm, OCR confidence: {conf}%.",
        "confidence": conf,
        "bounding_box": None
    }
