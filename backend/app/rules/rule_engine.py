from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.rule import ComplianceRule, RuleSeverity
from app.models.inspection import ComplianceStatus
from app.rules.legal_references import STATUTORY_REFERENCES
from app.rules.validators import (
    validate_mrp,
    validate_net_quantity,
    validate_manufacturing_date,
    validate_manufacturer,
    validate_consumer_care,
    validate_country_of_origin,
    validate_readability,
)

DEFAULT_RULES = [
    {
        "rule_code": "LM-RULE-6-1-A",
        "name": "Manufacturer Name & Complete Address",
        "description": "Checks for name and complete address of manufacturer/packer with PIN code.",
        "legal_reference": "Rule 6(1)(a) of Legal Metrology (Packaged Commodities) Rules, 2011",
        "required_field": "manufacturer",
        "category_applicability": "ALL",
        "severity": "FAIL"
    },
    {
        "rule_code": "LM-RULE-6-1-B",
        "name": "Common or Generic Commodity Name",
        "description": "Checks for common or generic name of commodity.",
        "legal_reference": "Rule 6(1)(b) of Legal Metrology (Packaged Commodities) Rules, 2011",
        "required_field": "product_name",
        "category_applicability": "ALL",
        "severity": "FAIL"
    },
    {
        "rule_code": "LM-RULE-6-1-C",
        "name": "Net Quantity in Standard Metric Units",
        "description": "Checks net quantity in standard metric units (g, kg, ml, l, N).",
        "legal_reference": "Rule 6(1)(c), Rule 11 & Rule 12 of Legal Metrology (PC) Rules, 2011",
        "required_field": "net_quantity",
        "category_applicability": "ALL",
        "severity": "FAIL"
    },
    {
        "rule_code": "LM-RULE-6-1-D",
        "name": "Month & Year of Manufacture/Packing",
        "description": "Checks month and year of manufacture or pre-packing.",
        "legal_reference": "Rule 6(1)(d) of Legal Metrology (Packaged Commodities) Rules, 2011",
        "required_field": "manufacturing_date",
        "category_applicability": "ALL",
        "severity": "FAIL"
    },
    {
        "rule_code": "LM-RULE-6-1-E",
        "name": "Maximum Retail Price (MRP) & Tax Declaration",
        "description": "Checks MRP in Indian Rupees inclusive of all taxes.",
        "legal_reference": "Rule 6(1)(e) of Legal Metrology (Packaged Commodities) Rules, 2011",
        "required_field": "mrp",
        "category_applicability": "ALL",
        "severity": "FAIL"
    },
    {
        "rule_code": "LM-RULE-6-1-N",
        "name": "Consumer Care Helpline & Email",
        "description": "Checks consumer complaint redressal cell details: telephone and email.",
        "legal_reference": "Rule 6(1)(n) of Legal Metrology (Packaged Commodities) Rules, 2011",
        "required_field": "consumer_care",
        "category_applicability": "ALL",
        "severity": "FAIL"
    },
    {
        "rule_code": "LM-RULE-6-10",
        "name": "Country of Origin (Imported Commodities)",
        "description": "Checks declaration of country of origin or manufacture for imported packages.",
        "legal_reference": "Rule 6(10) of Legal Metrology (Packaged Commodities) Rules, 2011",
        "required_field": "country_of_origin",
        "category_applicability": "ALL",
        "severity": "FAIL"
    },
    {
        "rule_code": "LM-RULE-7",
        "name": "Legibility & Minimum Font Size",
        "description": "Visual check of text clarity and approximate character height.",
        "legal_reference": "Rule 7 & Table-I of Legal Metrology (Packaged Commodities) Rules, 2011",
        "required_field": "readability",
        "category_applicability": "ALL",
        "severity": "WARNING"
    }
]

def evaluate_compliance(
    extracted_declarations: Dict[str, Any],
    product_category: str = "GENERAL",
    is_imported: bool = False,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Runs the configurable Legal Metrology Rule Engine.
    Evaluates each statutory rule against extracted fields.
    """
    # Fetch active rules from DB if available, else use DEFAULT_RULES
    active_rules = []
    if db:
        db_rules = db.query(ComplianceRule).filter(ComplianceRule.is_active == True).all()
        for r in db_rules:
            active_rules.append({
                "rule_code": r.rule_code,
                "name": r.name,
                "description": r.description,
                "legal_reference": r.legal_reference,
                "required_field": r.required_field,
                "category_applicability": r.category_applicability,
                "severity": r.severity
            })
    
    if not active_rules:
        active_rules = DEFAULT_RULES

    results: List[Dict[str, Any]] = []
    pass_cnt = 0
    fail_cnt = 0
    warning_cnt = 0
    na_cnt = 0

    for rule in active_rules:
        field = rule["required_field"]
        code = rule["rule_code"]
        name = rule["name"]
        ref = rule["legal_reference"]
        severity = rule["severity"]
        cat_app = rule.get("category_applicability", "ALL")

        # Category check
        if cat_app != "ALL" and product_category not in cat_app:
            results.append({
                "rule_code": code,
                "rule_name": name,
                "field": field,
                "status": "NOT_APPLICABLE",
                "message": f"Rule not applicable to category {product_category}.",
                "evidence": None,
                "confidence": 100.0,
                "legal_reference": ref,
                "severity": severity,
                "bounding_box": None
            })
            na_cnt += 1
            continue

        # Execute field validator
        eval_res = {}
        if field == "mrp":
            eval_res = validate_mrp(extracted_declarations.get("mrp", {}), rule)
        elif field == "net_quantity":
            eval_res = validate_net_quantity(extracted_declarations.get("net_quantity", {}), rule)
        elif field == "manufacturing_date":
            eval_res = validate_manufacturing_date(extracted_declarations.get("manufacturing_date", {}), rule)
        elif field == "manufacturer":
            eval_res = validate_manufacturer(extracted_declarations.get("manufacturer", {}), rule)
        elif field == "consumer_care":
            eval_res = validate_consumer_care(extracted_declarations.get("consumer_care", {}), rule)
        elif field == "country_of_origin":
            eval_res = validate_country_of_origin(extracted_declarations.get("country_of_origin", {}), is_imported, rule)
        elif field == "readability":
            eval_res = validate_readability(extracted_declarations.get("readability", {}), rule)
        elif field == "product_name":
            pname_data = extracted_declarations.get("product_name", {})
            if pname_data.get("status") == "DETECTED" and pname_data.get("value"):
                eval_res = {
                    "status": "PASS",
                    "message": f"Commodity generic/product name identified: {pname_data.get('value')}.",
                    "evidence": pname_data.get("value"),
                    "confidence": 95.0,
                    "bounding_box": None
                }
            else:
                eval_res = {
                    "status": "FAIL",
                    "message": "Common or generic name of commodity was not declared or identified.",
                    "evidence": "Missing generic name declaration.",
                    "confidence": 0.0,
                    "bounding_box": None
                }
        else:
            eval_res = {
                "status": "PASS",
                "message": f"Generic rule passed for {field}.",
                "evidence": None,
                "confidence": 80.0,
                "bounding_box": None
            }

        status = eval_res["status"]
        if status == "PASS":
            pass_cnt += 1
        elif status == "FAIL":
            fail_cnt += 1
        elif status == "WARNING":
            warning_cnt += 1
        elif status == "NOT_APPLICABLE":
            na_cnt += 1

        results.append({
            "rule_code": code,
            "rule_name": name,
            "field": field,
            "status": status,
            "message": eval_res.get("message", ""),
            "evidence": eval_res.get("evidence"),
            "confidence": eval_res.get("confidence", 80.0),
            "legal_reference": ref,
            "severity": severity,
            "bounding_box": eval_res.get("bounding_box")
        })

    # Determine overall status
    if fail_cnt > 0:
        overall_status = ComplianceStatus.NON_COMPLIANT
    elif warning_cnt > 0:
        overall_status = ComplianceStatus.REVIEW_REQUIRED
    else:
        overall_status = ComplianceStatus.COMPLIANT

    total_evaluated = pass_cnt + fail_cnt + warning_cnt
    confidence_score = round((pass_cnt / max(total_evaluated, 1)) * 100)

    return {
        "overall_status": overall_status,
        "summary": {
            "pass_count": pass_cnt,
            "fail_count": fail_cnt,
            "warning_count": warning_cnt,
            "not_applicable_count": na_cnt,
            "total_rules": len(results),
            "confidence_score": confidence_score
        },
        "rule_results": results,
        "disclaimer": "AI-assisted preliminary assessment. Final legal determination must be made by an authorized officer under the Legal Metrology Act, 2009."
    }
