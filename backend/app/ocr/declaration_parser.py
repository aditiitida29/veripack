import re
from typing import Dict, Any, List, Optional
from app.ocr.text_normalizer import clean_ocr_text, detect_quantity_ambiguity, normalize_quantity, LEGAL_METRIC_SYMBOLS

def parse_declarations_from_ocr(ocr_result: Dict[str, Any], manual_product_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Parses raw OCR output into structured Legal Metrology declaration fields.
    Extracts MRP, Net Qty, Dates, Address, Consumer Care, Origin, Name, and Font metrics.
    """
    raw_text = ocr_result.get("raw_text", "")
    lines = ocr_result.get("lines", [])
    full_text_single = clean_ocr_text(raw_text)

    declarations: Dict[str, Any] = {}

    # 1. MAXIMUM RETAIL PRICE (MRP) - Rule 6(1)(e)
    # ----------------------------------------------------
    mrp_line = None
    mrp_val = None
    mrp_raw = None
    mrp_tax_inclusive = False
    mrp_bb = None
    mrp_conf = 0.0

    # Explicitly check for Maximum Retail Price / MRP first, excluding generic 'unit sale price'
    mrp_regexes = [
        r'(?:M\.?R\.?P\.?|MAX(?:IMUM)?\s*RETAIL\s*PRICE)[\s\:\.\-\(\)]*[₹Rs\.\%]*\s*(\d+(?:[\.,]\d{1,2})?)',
        r'\bMRP[\s\:\.\-]*Rs\.?\s*(\d+(?:[\.,]\d{1,2})?)',
        r'[₹Rs\.]+\s*(\d+(?:[\.,]\d{1,2})?)\s*(?:M\.?R\.?P|\(INCL)',
        r'\bPRICE[\s\:\.\-]*[₹Rs\.]*\s*(\d+(?:[\.,]\d{1,2})?)'
    ]

    for rgx in mrp_regexes:
        m = re.search(rgx, full_text_single, re.IGNORECASE)
        if m:
            mrp_val = m.group(1).replace(',', '.')
            mrp_raw = m.group(0)
            break

    for line in lines:
        if re.search(r'(?:M\.?R\.?P|MAX(?:IMUM)?\s*RETAIL)', line["text"], re.IGNORECASE):
            mrp_line = line
            mrp_bb = {"x": line["x"], "y": line["y"], "width": line["width"], "height": line["height"]}
            mrp_conf = line.get("confidence", 85.0)
            break

    taxes_pattern = r'(?:INCL(?:USIVE)?\s*OF\s*ALL\s*TAXES|INCL\.\s*OF\s*ALL\s*TAXES|INCL\s*TAXES|INCL\.\s*TAX)'
    if re.search(taxes_pattern, full_text_single, re.IGNORECASE):
        mrp_tax_inclusive = True

    if mrp_val:
        declarations["mrp"] = {
            "value": f"₹ {mrp_val}",
            "numeric_value": float(mrp_val),
            "raw_text": mrp_raw or (mrp_line["text"] if mrp_line else f"MRP ₹{mrp_val}"),
            "tax_inclusive_declared": mrp_tax_inclusive,
            "status": "DETECTED",
            "confidence": mrp_conf if mrp_conf > 0 else 85.0,
            "bounding_box": mrp_bb,
            "notes": "Inclusive of all taxes declared." if mrp_tax_inclusive else "Warning: 'Inclusive of all taxes' declaration not explicitly detected adjacent to MRP."
        }
    else:
        declarations["mrp"] = {
            "value": None,
            "numeric_value": None,
            "raw_text": None,
            "tax_inclusive_declared": False,
            "status": "MISSING",
            "confidence": 0.0,
            "bounding_box": None,
            "notes": "No MRP declaration found in label."
        }

    # 2. NET QUANTITY - Rule 6(1)(c), Rule 11, Rule 12
    # ----------------------------------------------------
    qty_val = None
    qty_unit = None
    qty_display = None
    qty_raw = None
    qty_bb = None
    qty_conf = 0.0
    qty_ambiguity = None

    ambig_match = re.search(r'(\d+)\s+9\b', full_text_single)
    if ambig_match:
        qty_ambiguity = f'Possible OCR ambiguity: "{ambig_match.group(0)}" may represent "{ambig_match.group(1)} g".'
        qty_raw = ambig_match.group(0)
        for line in lines:
            if ambig_match.group(0) in line["text"]:
                qty_bb = {"x": line["x"], "y": line["y"], "width": line["width"], "height": line["height"]}
                qty_conf = line.get("confidence", 60.0)
                break

    qty_regexes = [
        r'(?:NET\s*(?:QTY|QUANTITY|WT|WEIGHT|CONTENTS?)|NETTO)[\s\:\.\-]*(\d+(?:\.\d+)?\s*(?:g|gm|gms|kg|kgs|ml|mls|l|lt|ltr|ltrs|N|U|m|cm|mm|units?|pieces?|pc|pcs|nos))\b',
        r'(?:NET\s*(?:QTY|QUANTITY|WT|WEIGHT))[\s\:\.\-]*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)',
        r'\b(\d+(?:\.\d+)?)\s*(kg|kgs|g|gm|gms|ml|mls|ltr|ltrs|l|N|U)\b'
    ]

    for rgx in qty_regexes:
        qm = re.search(rgx, full_text_single, re.IGNORECASE)
        if qm:
            raw_target = qm.group(0)
            qty_raw = raw_target
            num, unit, display = normalize_quantity(raw_target)
            if num and unit:
                qty_val = num
                qty_unit = unit
                qty_display = display
                potential_ambig = detect_quantity_ambiguity(raw_target)
                if potential_ambig:
                    qty_ambiguity = potential_ambig
                break

    for line in lines:
        if re.search(r'(?:NET\s*(?:QTY|QUANTITY|WT|WEIGHT)|NETTO|\b\d+\s*(?:g|kg|ml|l|N|U)\b)', line["text"], re.IGNORECASE):
            qty_bb = {"x": line["x"], "y": line["y"], "width": line["width"], "height": line["height"]}
            qty_conf = line.get("confidence", 85.0)
            break

    if qty_ambiguity and not qty_display:
        declarations["net_quantity"] = {
            "value": qty_raw,
            "unit": "UNKNOWN",
            "is_standard_unit": False,
            "raw_text": qty_raw,
            "status": "AMBIGUOUS",
            "confidence": qty_conf if qty_conf > 0 else 55.0,
            "bounding_box": qty_bb,
            "notes": qty_ambiguity
        }
    elif qty_display:
        is_std = qty_unit in LEGAL_METRIC_SYMBOLS
        declarations["net_quantity"] = {
            "value": qty_display,
            "numeric_value": float(qty_val) if qty_val else None,
            "unit": qty_unit,
            "is_standard_unit": is_std,
            "raw_text": qty_raw,
            "status": "AMBIGUOUS" if qty_ambiguity else "DETECTED",
            "confidence": qty_conf if qty_conf > 0 else 90.0,
            "bounding_box": qty_bb,
            "notes": qty_ambiguity or ("Compliant standard unit." if is_std else f"Non-standard metric unit '{qty_unit}'.")
        }
    else:
        declarations["net_quantity"] = {
            "value": None,
            "unit": None,
            "is_standard_unit": False,
            "raw_text": None,
            "status": "MISSING",
            "confidence": 0.0,
            "bounding_box": None,
            "notes": "Net quantity declaration was not detected."
        }

    # 3. DATE OF MANUFACTURE / PACKING - Rule 6(1)(d)
    # ----------------------------------------------------
    date_val = None
    date_type = "MFD"
    date_raw = None
    date_bb = None
    date_conf = 0.0

    # Specifically search for month/year patterns
    date_pattern_explicit = r'\b(0[1-9]|1[0-2])[\/\.\-](202[0-9]|203[0-9])\b'
    m_exp = re.search(date_pattern_explicit, full_text_single)
    if m_exp:
        date_val = m_exp.group(0)
        date_raw = m_exp.group(0)
    else:
        m_mon = re.search(r'\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[a-z]*[\s\/\.\-]+(202[0-9]|203[0-9])\b', full_text_single, re.IGNORECASE)
        if m_mon:
            date_val = m_mon.group(0)
            date_raw = m_mon.group(0)

    for line in lines:
        if re.search(r'(?:MFD|MFG|PKD|PACKED|PKG\s*DATE|MONTH\s*&\s*YEAR)', line["text"], re.IGNORECASE):
            date_bb = {"x": line["x"], "y": line["y"], "width": line["width"], "height": line["height"]}
            date_conf = line.get("confidence", 85.0)
            if "PKD" in line["text"].upper() or "PACKED" in line["text"].upper():
                date_type = "PKD"
            break

    if date_val:
        declarations["manufacturing_date"] = {
            "value": date_val,
            "type": date_type,
            "raw_text": date_raw or date_val,
            "status": "DETECTED",
            "confidence": date_conf if date_conf > 0 else 85.0,
            "bounding_box": date_bb,
            "notes": f"Detected {date_type} date declaration: {date_val}."
        }
    else:
        declarations["manufacturing_date"] = {
            "value": None,
            "type": None,
            "raw_text": None,
            "status": "MISSING",
            "confidence": 0.0,
            "bounding_box": None,
            "notes": "Month and year of manufacture/packing not detected."
        }

    # 4. BEST BEFORE / EXPIRY DATE
    # ----------------------------------------------------
    exp_val = None
    exp_raw = None
    exp_bb = None
    exp_regex = r'(?:EXP|EXPIRY|USE BY|BEST BEFORE)[\s\:\.\-]*([A-Za-z0-9\/\.\-\s]{3,20})'
    em = re.search(exp_regex, full_text_single, re.IGNORECASE)
    if em:
        exp_raw = em.group(0)
        exp_val = em.group(1).strip()
        for line in lines:
            if re.search(r'(?:EXP|EXPIRY|USE BY|BEST BEFORE)', line["text"], re.IGNORECASE):
                exp_bb = {"x": line["x"], "y": line["y"], "width": line["width"], "height": line["height"]}
                break

    declarations["expiry_date"] = {
        "value": exp_val,
        "raw_text": exp_raw,
        "status": "DETECTED" if exp_val else "MISSING",
        "bounding_box": exp_bb
    }

    # 5. MANUFACTURER / PACKER NAME & COMPLETE ADDRESS - Rule 6(1)(a)
    # ----------------------------------------------------
    mfg_name = None
    mfg_address = None
    mfg_pin = None
    mfg_bb = None
    mfg_conf = 0.0

    pin_match = re.search(r'\b([1-9][0-9]{5})\b', full_text_single)
    if pin_match:
        mfg_pin = pin_match.group(1)

    mfg_markers = [
        r'(?:MFD\s*BY|MANUFACTURED\s*(?:&\s*PACKED\s*)?BY|PACKED\s*BY|PKD\s*BY|MARKETED\s*BY)[\s\:\.\-]+(.+?)(?=\bCOMPLETE|\bADDRESS|\bCONSUMER|\bCOUNTRY|\bBATCH|\bMRP|$)',
        r'([A-Z0-9\s\.\,\'\-]{3,40}(?:Pvt\.?\s*Ltd\.?|Limited|Industries|Enterprises|Foods|Agro))'
    ]

    for m_rgx in mfg_markers:
        mm = re.search(m_rgx, full_text_single, re.IGNORECASE)
        if mm:
            mfg_name = mm.group(1).strip(" :,-")
            break

    for line in lines:
        if re.search(r'(?:MFD\s*BY|MANUFACTURED|PACKED\s*BY|PKD\s*BY|MARKETED\s*BY)', line["text"], re.IGNORECASE):
            mfg_bb = {"x": line["x"], "y": line["y"], "width": line["width"], "height": line["height"]}
            mfg_conf = line.get("confidence", 80.0)
            break

    addr_match = re.search(r'(?:COMPLETE\s*ADDRESS|ADDRESS)[\s\:\.\-]+(.+?)(?=\bCONSUMER|\bCOUNTRY|\bBATCH|\bMRP|\bHELPLINE|$)', full_text_single, re.IGNORECASE)
    if addr_match:
        mfg_address = addr_match.group(1).strip(" :,-")
    else:
        addr_keywords = re.findall(r'(?:Plot|Sector|Phase|Road|Street|Estate|Dist|District|State|Industrial|Nagar|Marg|Shop|Food\s*Park)[^\,\.\n]*', full_text_single, re.IGNORECASE)
        if addr_keywords or mfg_pin:
            mfg_address = ", ".join(addr_keywords[:3])
            if mfg_pin and mfg_pin not in mfg_address:
                mfg_address = f"{mfg_address} - {mfg_pin}".strip(" ,-")

    is_complete_addr = bool(mfg_pin and len(mfg_address or "") > 15)

    if mfg_name or mfg_address:
        declarations["manufacturer"] = {
            "name": mfg_name or "Detected Manufacturer",
            "address": mfg_address or "Address details detected without PIN code",
            "pin_code": mfg_pin,
            "has_complete_address": is_complete_addr,
            "status": "DETECTED",
            "confidence": mfg_conf if mfg_conf > 0 else 80.0,
            "bounding_box": mfg_bb,
            "notes": "Complete address with PIN code detected." if is_complete_addr else "Address detected but missing mandatory 6-digit PIN code."
        }
    else:
        declarations["manufacturer"] = {
            "name": None,
            "address": None,
            "pin_code": None,
            "has_complete_address": False,
            "status": "MISSING",
            "confidence": 0.0,
            "bounding_box": None,
            "notes": "Manufacturer name and address not detected."
        }

    # 6. CONSUMER CARE DETAILS - Rule 6(1)(n)
    # ----------------------------------------------------
    cc_phone = None
    cc_email = None
    cc_bb = None
    cc_conf = 0.0

    phone_match = re.search(r'(?:1800[\s\-]*\d{3}[\s\-]*\d{3,4}|(?:TEL|PHONE|MOBILE|HELPLINE|CALL)[\s\:\.\-]*([0-9\+\s\-]{8,15}))', full_text_single, re.IGNORECASE)
    if phone_match:
        cc_phone = phone_match.group(0).strip()

    email_match = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', full_text_single)
    if email_match:
        cc_email = email_match.group(1).strip()

    for line in lines:
        if re.search(r'(?:CONSUMER|CUSTOMER\s*CARE|HELPLINE|FEEDBACK|COMPLAINTS?|1800|@)', line["text"], re.IGNORECASE):
            cc_bb = {"x": line["x"], "y": line["y"], "width": line["width"], "height": line["height"]}
            cc_conf = line.get("confidence", 85.0)
            break

    cc_detected = bool(cc_phone or cc_email)
    cc_complete = bool(cc_phone and cc_email)

    if cc_detected:
        notes = []
        if cc_phone:
            notes.append(f"Phone: {cc_phone}")
        else:
            notes.append("Missing helpline telephone")
        if cc_email:
            notes.append(f"Email: {cc_email}")
        else:
            notes.append("Missing consumer email")

        declarations["consumer_care"] = {
            "phone": cc_phone,
            "email": cc_email,
            "is_complete": cc_complete,
            "status": "DETECTED",
            "confidence": cc_conf if cc_conf > 0 else 85.0,
            "bounding_box": cc_bb,
            "notes": "; ".join(notes)
        }
    else:
        declarations["consumer_care"] = {
            "phone": None,
            "email": None,
            "is_complete": False,
            "status": "MISSING",
            "confidence": 0.0,
            "bounding_box": None,
            "notes": "No consumer care contact details (telephone/email) detected."
        }

    # 7. COUNTRY OF ORIGIN - Rule 6(10)
    # ----------------------------------------------------
    coo_val = None
    coo_bb = None
    coo_conf = 0.0
    coo_match = re.search(r'(?:COUNTRY\s*OF\s*ORIGIN|MADE\s*IN|PRODUCT\s*OF|ORIGIN)[\s\:\.\-]+([A-Za-z\s]{2,20})', full_text_single, re.IGNORECASE)
    if coo_match:
        coo_val = coo_match.group(1).strip()
        for line in lines:
            if re.search(r'(?:COUNTRY\s*OF\s*ORIGIN|MADE\s*IN|PRODUCT\s*OF)', line["text"], re.IGNORECASE):
                coo_bb = {"x": line["x"], "y": line["y"], "width": line["width"], "height": line["height"]}
                coo_conf = line.get("confidence", 85.0)
                break

    declarations["country_of_origin"] = {
        "value": coo_val,
        "status": "DETECTED" if coo_val else "MISSING",
        "confidence": coo_conf if coo_val else 0.0,
        "bounding_box": coo_bb,
        "notes": f"Country of origin declared as '{coo_val}'." if coo_val else "Country of origin declaration not detected."
    }

    # 8. COMMON / GENERIC COMMODITY NAME - Rule 6(1)(b)
    # ----------------------------------------------------
    product_name = None
    if manual_product_info and manual_product_info.get("product_name"):
        product_name = manual_product_info["product_name"]
    else:
        name_match = re.search(r'(?:COMMON\s*NAME|GENERIC\s*NAME|COMMODITY\s*NAME|GENERIC\s*COMMODITY)[\s\:\.\-]+(.+?)(?=\bNET|\bMRP|\bMFD|\bBATCH|\bMANUFACTURED|\bPRICE|$)', full_text_single, re.IGNORECASE)
        if name_match:
            product_name = name_match.group(1).strip(" :,-")
        else:
            for line in lines[:3]:
                if len(line["text"].strip()) > 3 and not re.search(r'(?:MRP|NET|BATCH|MFD|PKD)', line["text"], re.IGNORECASE):
                    product_name = line["text"].strip()
                    break

    declarations["product_name"] = {
        "value": product_name or "Packaged Commodity",
        "status": "DETECTED" if product_name else "MISSING",
        "notes": "Generic or brand name of packaged commodity."
    }

    # 9. FONT SIZE & READABILITY ASSESSMENT - Rule 7 & Table-I
    # ----------------------------------------------------
    font_metrics = ocr_result.get("font_metrics", {})
    declarations["readability"] = {
        "avg_char_height_px": font_metrics.get("avg_char_height_px", 16.0),
        "approx_min_font_mm": font_metrics.get("approx_min_font_mm", 2.5),
        "overall_ocr_confidence": font_metrics.get("overall_ocr_confidence", 80.0),
        "status": "DETECTED",
        "notes": font_metrics.get("disclaimer", "Preliminary visual assessment. Requires physical/legal verification.")
    }

    return declarations
