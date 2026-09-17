import json
import uuid
import datetime
import shutil
from pathlib import Path
from app.database import Base, engine, SessionLocal
from app.config import UPLOAD_DIR, DEMO_ASSETS_DIR
from app.models.user import User, UserRole
from app.models.product import Product, ProductCategory
from app.models.rule import ComplianceRule
from app.models.inspection import Inspection, ComplianceStatus
from app.rules.rule_engine import DEFAULT_RULES, evaluate_compliance
from app.ocr.ocr_engine import run_ocr_with_boxes
from app.ocr.declaration_parser import parse_declarations_from_ocr
from app.utils.security import get_password_hash
from app.utils.demo_data_generator import create_demo_labels

def seed_database():
    print("Initializing Database and Tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Create Demo Labels if missing
    create_demo_labels()

    # 2. Seed Users
    users_to_seed = [
        {
            "email": "admin@doca.gov.in",
            "full_name": "Dr. A. K. Verma (Enforcement Director)",
            "password": "Admin@DocA2026",
            "role": UserRole.SUPER_ADMIN,
            "badge_number": "DOCA-HQ-001",
            "department": "DoCA Central Enforcement Directorate"
        },
        {
            "email": "inspector.sharma@doca.gov.in",
            "full_name": "Rajesh Sharma (Senior Inspector)",
            "password": "Inspector@2026",
            "role": UserRole.INSPECTOR,
            "badge_number": "DOCA-DL-104",
            "department": "Legal Metrology Delhi Zone"
        },
        {
            "email": "viewer@consumeraffairs.nic.in",
            "full_name": "Pooja Mehta (Compliance Auditor)",
            "password": "Viewer@2026",
            "role": UserRole.VIEWER,
            "badge_number": "DOCA-AUD-88",
            "department": "National Consumer Dispute Redressal Cell"
        },
        {
            "email": "consumer.rahul@gmail.com",
            "full_name": "Rahul Verma (Citizen Consumer)",
            "password": "Consumer@2026",
            "role": UserRole.CONSUMER,
            "badge_number": "CITIZEN-IN-2026",
            "department": "Citizen Consumer"
        }
    ]

    seeded_users = {}
    for u in users_to_seed:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user_obj = User(
                email=u["email"],
                full_name=u["full_name"],
                hashed_password=get_password_hash(u["password"]),
                role=u["role"],
                badge_number=u["badge_number"],
                department=u["department"],
                is_active=True
            )
            db.add(user_obj)
            db.commit()
            db.refresh(user_obj)
            seeded_users[u["role"]] = user_obj
            print(f"Created user: {u['email']} [{u['role']}]")
        else:
            seeded_users[u["role"]] = existing

    # 3. Seed Compliance Rules
    for r in DEFAULT_RULES:
        existing_rule = db.query(ComplianceRule).filter(ComplianceRule.rule_code == r["rule_code"]).first()
        if not existing_rule:
            rule_obj = ComplianceRule(
                rule_code=r["rule_code"],
                name=r["name"],
                description=r["description"],
                legal_reference=r["legal_reference"],
                required_field=r["required_field"],
                category_applicability=r["category_applicability"],
                severity=r["severity"],
                is_active=True
            )
            db.add(rule_obj)
            print(f"Created rule: {r['rule_code']}")
    db.commit()

    # 4. Seed Pre-Analyzed Demo Inspections
    images_dir = UPLOAD_DIR / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    inspector = seeded_users.get(UserRole.INSPECTOR) or db.query(User).first()

    demo_scenarios = [
        {
            "file": "demo_compliant_salt.png",
            "code": "INSP-2026-1001",
            "pname": "Tata Pure Refined Iodised Salt",
            "brand": "Tata Consumer Products",
            "cat": ProductCategory.FOOD_BEVERAGE,
            "is_imported": False,
            "remarks": "Fully compliant packaged commodity. All mandatory declarations under Rule 6(1) present and legible."
        },
        {
            "file": "demo_missing_mrp_snack.png",
            "code": "INSP-2026-1002",
            "pname": "Royal Crunch Butter Cookies",
            "brand": "Royal Bakers",
            "cat": ProductCategory.FOOD_BEVERAGE,
            "is_imported": False,
            "remarks": "Violations flagged: Maximum Retail Price (MRP) missing (Rule 6(1)(e)); Consumer Care email missing (Rule 6(1)(n)). Show-cause notice recommended."
        },
        {
            "file": "demo_ambiguous_qty.png",
            "code": "INSP-2026-1003",
            "pname": "Natural Energy Protein Mix",
            "brand": "FitHealth Nutrition",
            "cat": ProductCategory.FOOD_BEVERAGE,
            "is_imported": False,
            "remarks": "Review Required: Net quantity expression ambiguous ('500 9' likely misread for '500 g'). Physical inspection recommended."
        },
        {
            "file": "demo_imported_earbuds.png",
            "code": "INSP-2026-1004",
            "pname": "Aero Wireless Buds",
            "brand": "AeroTech Audio",
            "cat": ProductCategory.ELECTRONICS,
            "is_imported": True,
            "remarks": "Major statutory violation: Imported electronic commodity missing Country of Origin (Rule 6(10)) and Importer name/address (Rule 6(1)(a))."
        },
        {
            "file": "demo_warnings_spice.png",
            "code": "INSP-2026-1005",
            "pname": "Spice Delight Garam Masala",
            "brand": "Spice Delight",
            "cat": ProductCategory.FOOD_BEVERAGE,
            "is_imported": False,
            "remarks": "Review Required: Non-standard unit symbol 'gms' used instead of standard 'g' (Rule 12); MRP lacks explicit 'incl. of all taxes' wording."
        }
    ]

    for scenario in demo_scenarios:
        existing_insp = db.query(Inspection).filter(Inspection.inspection_code == scenario["code"]).first()
        if not existing_insp:
            src_path = DEMO_ASSETS_DIR / scenario["file"]
            dest_name = f"seed_{scenario['file']}"
            dest_path = images_dir / dest_name
            shutil.copyfile(src_path, dest_path)
            rel_path = f"uploads/images/{dest_name}"

            ocr_res = run_ocr_with_boxes(str(dest_path))
            declarations = parse_declarations_from_ocr(ocr_res, {"product_name": scenario["pname"]})
            eval_res = evaluate_compliance(
                extracted_declarations=declarations,
                product_category=scenario["cat"],
                is_imported=scenario["is_imported"],
                db=db
            )

            prod = db.query(Product).filter(Product.name == scenario["pname"]).first()
            if not prod:
                prod = Product(
                    name=scenario["pname"],
                    brand=scenario["brand"],
                    category=scenario["cat"],
                    is_imported=scenario["is_imported"]
                )
                db.add(prod)
                db.commit()
                db.refresh(prod)

            bounding_boxes = []
            for r in eval_res["rule_results"]:
                if r.get("bounding_box"):
                    bounding_boxes.append({
                        "rule_code": r["rule_code"],
                        "field": r["field"],
                        "status": r["status"],
                        "box": r["bounding_box"],
                        "label": r["rule_name"]
                    })

            new_insp = Inspection(
                inspection_code=scenario["code"],
                product_id=prod.id,
                inspector_id=inspector.id,
                status=eval_res["overall_status"],
                pass_count=eval_res["summary"]["pass_count"],
                fail_count=eval_res["summary"]["fail_count"],
                warning_count=eval_res["summary"]["warning_count"],
                confidence_score=eval_res["summary"]["confidence_score"],
                extracted_fields=json.dumps(declarations),
                rule_results=json.dumps(eval_res["rule_results"]),
                bounding_boxes=json.dumps(bounding_boxes),
                raw_ocr_text=ocr_res.get("raw_text", ""),
                image_paths=json.dumps([rel_path]),
                inspector_remarks=scenario["remarks"],
                is_demo=True,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=demo_scenarios.index(scenario))
            )
            db.add(new_insp)
            db.commit()
            print(f"Seeded Inspection {scenario['code']}: {scenario['pname']} -> [{eval_res['overall_status']}]")

    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
