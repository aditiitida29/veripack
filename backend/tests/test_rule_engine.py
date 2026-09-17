import pytest
from app.rules.rule_engine import evaluate_compliance
from app.models.inspection import ComplianceStatus

def test_compliant_evaluation():
    extracted = {
        "mrp": {"value": "₹ 120.00", "status": "DETECTED", "tax_inclusive_declared": True, "confidence": 95.0},
        "net_quantity": {"value": "1 kg", "status": "DETECTED", "is_standard_unit": True, "confidence": 90.0},
        "manufacturing_date": {"value": "08/2026", "status": "DETECTED", "confidence": 90.0},
        "manufacturer": {"name": "Tata Consumer Products", "address": "Mithapur", "pin_code": "361345", "has_complete_address": True, "status": "DETECTED"},
        "consumer_care": {"phone": "1800-345-0066", "email": "care@tata.com", "is_complete": True, "status": "DETECTED"},
        "country_of_origin": {"value": "India", "status": "DETECTED"},
        "product_name": {"value": "Tata Salt", "status": "DETECTED"},
        "readability": {"approx_min_font_mm": 2.5, "avg_char_height_px": 18.0, "status": "DETECTED"}
    }
    res = evaluate_compliance(extracted, product_category="FOOD_BEVERAGE", is_imported=False)
    assert res["overall_status"] == ComplianceStatus.COMPLIANT
    assert res["summary"]["fail_count"] == 0
    assert res["summary"]["warning_count"] == 0
    assert res["summary"]["pass_count"] >= 7

def test_missing_mrp_evaluation():
    extracted = {
        "mrp": {"value": None, "status": "MISSING"},
        "net_quantity": {"value": "500 g", "status": "DETECTED", "is_standard_unit": True},
        "manufacturing_date": {"value": "08/2026", "status": "DETECTED"},
        "manufacturer": {"name": "Local Agro", "address": "Jaipur - 302001", "pin_code": "302001", "has_complete_address": True, "status": "DETECTED"},
        "consumer_care": {"phone": "1800-000-1111", "email": "info@agro.com", "is_complete": True, "status": "DETECTED"},
        "country_of_origin": {"value": "India", "status": "DETECTED"},
        "product_name": {"value": "Agro Flour", "status": "DETECTED"},
        "readability": {"approx_min_font_mm": 2.0, "avg_char_height_px": 16.0, "status": "DETECTED"}
    }
    res = evaluate_compliance(extracted, product_category="FOOD_BEVERAGE", is_imported=False)
    assert res["overall_status"] == ComplianceStatus.NON_COMPLIANT
    assert res["summary"]["fail_count"] >= 1
    mrp_rule = next(r for r in res["rule_results"] if r["field"] == "mrp")
    assert mrp_rule["status"] == "FAIL"

def test_imported_missing_origin_evaluation():
    extracted = {
        "mrp": {"value": "₹ 999.00", "status": "DETECTED", "tax_inclusive_declared": True},
        "net_quantity": {"value": "1 U", "status": "DETECTED", "is_standard_unit": True},
        "manufacturing_date": {"value": "06/2026", "status": "DETECTED"},
        "manufacturer": {"name": "Global Tech", "address": "Delhi - 110001", "pin_code": "110001", "has_complete_address": True, "status": "DETECTED"},
        "consumer_care": {"phone": "1800-222-3333", "email": "care@global.com", "is_complete": True, "status": "DETECTED"},
        "country_of_origin": {"value": None, "status": "MISSING"},
        "product_name": {"value": "Wireless Mouse", "status": "DETECTED"},
        "readability": {"approx_min_font_mm": 2.0, "avg_char_height_px": 16.0, "status": "DETECTED"}
    }
    # When is_imported = True, missing origin must FAIL under Rule 6(10)
    res = evaluate_compliance(extracted, product_category="ELECTRONICS", is_imported=True)
    assert res["overall_status"] == ComplianceStatus.NON_COMPLIANT
    origin_rule = next(r for r in res["rule_results"] if r["field"] == "country_of_origin")
    assert origin_rule["status"] == "FAIL"
