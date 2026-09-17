from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from app.config import DEMO_ASSETS_DIR

def create_demo_labels():
    """Generates 5 realistic sample packaging labels for instant evaluation."""
    DEMO_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_med = ImageFont.truetype("arial.ttf", 17)
        font_bold = ImageFont.truetype("arialbd.ttf", 18)
    except Exception:
        font_large = font_med = font_bold = ImageFont.load_default()

    # 1. DEMO 1: Fully Compliant Product (Tata Pure Refined Iodised Salt)
    img1 = Image.new("RGB", (850, 680), "#F8FAFC")
    d1 = ImageDraw.Draw(img1)
    d1.rectangle([(0, 0), (850, 65)], fill="#0F2942")
    d1.text((25, 18), "TATA PURE REFINED IODISED EDIBLE SALT", fill="#FFFFFF", font=font_large)
    d1.rectangle([(15, 80), (835, 660)], outline="#0F2942", width=2)
    
    lines1 = [
        "COMMON NAME: Refined Iodised Edible Salt",
        "NET QUANTITY: 1 kg",
        "MAXIMUM RETAIL PRICE (MRP): Rs. 28.00 (Inclusive of all taxes)",
        "UNIT SALE PRICE: Rs. 0.028 / g",
        "MONTH & YEAR OF PKG: 08/2026",
        "BATCH NO: TS-B7892",
        "MANUFACTURED & PACKED BY: Tata Consumer Products Limited",
        "COMPLETE ADDRESS: Plot 12, GIDC Industrial Area, Mithapur, Gujarat - 361345",
        "CONSUMER CARE HELPLINE: 1800-345-0066",
        "CONSUMER CARE EMAIL: customercare@tataconsumer.com",
        "CONSUMER ADDRESS: Customer Care Cell, PO Box 34, Mumbai - 400001",
        "COUNTRY OF ORIGIN: India"
    ]
    
    y = 95
    for item in lines1:
        d1.text((35, y), item, fill="#1E293B", font=font_med)
        y += 44
        
    img1.save(DEMO_ASSETS_DIR / "demo_compliant_salt.png")

    # 2. DEMO 2: Missing MRP & Missing Consumer Email (Local Confectionery Brand)
    img2 = Image.new("RGB", (850, 580), "#FFFBEB")
    d2 = ImageDraw.Draw(img2)
    d2.rectangle([(0, 0), (850, 65)], fill="#B45309")
    d2.text((25, 18), "ROYAL CRUNCH BUTTER COOKIES (DEMO: MISSING MRP)", fill="#FFFFFF", font=font_large)
    d2.rectangle([(15, 80), (835, 560)], outline="#B45309", width=2)
    
    lines2 = [
        "COMMODITY NAME: Butter Cookies",
        "NET QUANTITY: 200 g",
        "DATE OF MANUFACTURE: 07/2026",
        "BATCH NUMBER: RC-402",
        "MANUFACTURED BY: Royal Bakers & Confectioners",
        "ADDRESS: Shop 4, Market Road, Pune, Maharashtra - 411001",
        "CONSUMER CARE TEL: 020-25541299",
        "COUNTRY OF ORIGIN: India"
        # MRP and Consumer Email intentionally missing
    ]
    y = 95
    for item in lines2:
        d2.text((35, y), item, fill="#1E293B", font=font_med)
        y += 50
    img2.save(DEMO_ASSETS_DIR / "demo_missing_mrp_snack.png")

    # 3. DEMO 3: Ambiguous Quantity OCR ("500 9")
    img3 = Image.new("RGB", (850, 620), "#F0FDF4")
    d3 = ImageDraw.Draw(img3)
    d3.rectangle([(0, 0), (850, 65)], fill="#15803D")
    d3.text((25, 18), "NATURAL ENERGY PROTEIN MIX (DEMO: 500 9)", fill="#FFFFFF", font=font_large)
    d3.rectangle([(15, 80), (835, 600)], outline="#15803D", width=2)
    
    lines3 = [
        "GENERIC NAME: Cereal Protein Food",
        "NET WEIGHT: 500 9",  # Simulates OCR ambiguity of 500 g
        "MAXIMUM RETAIL PRICE: MRP Rs. 350.00 (Incl. of all taxes)",
        "MFD DATE: 09/2026",
        "PACKED BY: FitHealth Nutrition Pvt Ltd",
        "ADDRESS: Plot 88, Electronic City, Bengaluru, Karnataka - 560100",
        "CONSUMER HELPLINE: 1800-200-4499",
        "CUSTOMER EMAIL: support@fithealth.in",
        "COUNTRY OF ORIGIN: India"
    ]
    y = 95
    for item in lines3:
        d3.text((35, y), item, fill="#1E293B", font=font_med)
        y += 50
    img3.save(DEMO_ASSETS_DIR / "demo_ambiguous_qty.png")

    # 4. DEMO 4: Imported Electronics Missing Country of Origin & Importer Name
    img4 = Image.new("RGB", (850, 580), "#EFF6FF")
    d4 = ImageDraw.Draw(img4)
    d4.rectangle([(0, 0), (850, 65)], fill="#1E40AF")
    d4.text((25, 18), "AERO WIRELESS BUDS (DEMO: IMPORT VIOLATION)", fill="#FFFFFF", font=font_large)
    d4.rectangle([(15, 80), (835, 560)], outline="#1E40AF", width=2)
    
    lines4 = [
        "GENERIC COMMODITY: Bluetooth Wireless Earbuds",
        "NET QUANTITY: 1 U",
        "MRP: Rs. 2499.00 (Inclusive of all taxes)",
        "MONTH & YEAR OF IMPORT: 06/2026",
        "BATTERY CAPACITY: 400 mAh",
        "CONSUMER CARE TEL: 1800-111-9876",
        "CONSUMER CARE EMAIL: service@aerobuds.com"
        # Missing Country of Origin and Importer Name/Address
    ]
    y = 95
    for item in lines4:
        d4.text((35, y), item, fill="#1E293B", font=font_med)
        y += 50
    img4.save(DEMO_ASSETS_DIR / "demo_imported_earbuds.png")

    # 5. DEMO 5: Non-standard unit ("gms") & Missing "incl. of all taxes"
    img5 = Image.new("RGB", (850, 600), "#FEF2F2")
    d5 = ImageDraw.Draw(img5)
    d5.rectangle([(0, 0), (850, 65)], fill="#991B1B")
    d5.text((25, 18), "SPICE DELIGHT GARAM MASALA (DEMO: WARNINGS)", fill="#FFFFFF", font=font_large)
    d5.rectangle([(15, 80), (835, 580)], outline="#991B1B", width=2)

    lines5 = [
        "COMMODITY NAME: Blended Spice Powder",
        "NET QUANTITY: 100 gms",  # Non-standard unit 'gms'
        "PRICE: MRP Rs. 85.00",    # Missing mandatory "incl. of all taxes"
        "PKD DATE: 05/2026",
        "PACKED BY: Spice Delight Agro",
        "ADDRESS: Sector 3, Food Park, Jaipur, Rajasthan - 302013",
        "HELPLINE: 0141-2334455",
        "EMAIL: care@spicedelight.in",
        "COUNTRY OF ORIGIN: India"
    ]
    y = 95
    for item in lines5:
        d5.text((35, y), item, fill="#1E293B", font=font_med)
        y += 50
    img5.save(DEMO_ASSETS_DIR / "demo_warnings_spice.png")

    print("Regenerated 5 demo packaging labels with clear layout.")

if __name__ == "__main__":
    create_demo_labels()
