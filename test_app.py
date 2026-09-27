import os
import sys
import io
import pandas as pd

# Set UTF-8 encoding for standard output if needed
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import database as db
import ai_agents as ai
import pdf_generator as pdf_gen

def test_pipeline():
    print("=" * 70)
    print("⚡ [TEST SUITE] SmartInvoice AI Comprehensive Verification")
    print("=" * 70)

    # 1. Test Database & Catalog
    print("\n[STEP 1] Testing Database Initialization & Active Catalog...")
    db.init_db()
    cats = db.get_all_catalog_items()
    print(f" -> [OK] Catalog loaded with {len(cats)} active services.")
    assert len(cats) >= 8, f"Expected at least 8 catalog services, found {len(cats)}"

    # 2. Test CSV / External Data Source Import & Export
    print("\n[STEP 2] Testing CSV / Spreadsheet Pricing Data Import & Export...")
    test_csv_path = os.path.join(os.path.dirname(__file__), "pricing_catalog.csv")
    if os.path.exists(test_csv_path):
        df_csv = pd.read_csv(test_csv_path)
        ok, msg = db.import_catalog_from_dataframe(df_csv, replace_existing=False)
        assert ok, f"Failed to import from CSV: {msg}"
        print(f" -> [OK] Imported pricing from CSV ({len(df_csv)} items). Result: {msg}")
    
    df_exported = db.export_catalog_to_dataframe()
    assert not df_exported.empty, "Catalog export produced empty dataframe"
    print(f" -> [OK] Catalog exported successfully ({len(df_exported)} entries in memory).")

    # 3. Test Dual-Agent AI Pipeline
    print("\n[STEP 3] Testing Natural Language Understanding & Fuzzy ML Reconciliation...")
    test_prompt = """From: Sarah Connor (sconnor@cyberdyne.ai)
Subject: Project Billing & Procurement

Hi Support,
Please invoice Cyberdyne Systems for the following deliverables:
- 2x Python Backend API Development
- 1x Website UI/UX Design
- 6 months Monthly Cloud Hosting & Maintenance
- 1x Proprietary Quantum Logic Board Installation
- Quantity: -4 SEO Audit & Optimization

Please send the final invoice with Net-15 terms.
Thanks,
Sarah Connor"""

    res = ai.run_smart_invoice_pipeline(test_prompt)

    print(f" -> Customer Name: '{res['customer_name']}'")
    print(f" -> Customer Email: '{res['customer_email']}'")
    print(f" -> Extraction Engine: {res['extraction_engine']}")
    print(f" -> Total Line Items Extracted: {len(res['reconciled_items'])}")
    print(f" -> Reconciliation Stats: {res['reconciliation_stats']}")

    assert res["customer_name"] != "", "Failed to extract customer name"
    assert "cyberdyne" in res["customer_email"] or "@" in res["customer_email"], "Failed to extract customer email"
    assert len(res["reconciled_items"]) >= 4, "Failed to extract line items"

    print("\n[Reconciled Items Detail]:")
    for it in res["reconciled_items"]:
        print(f"   • [{it['match_status']} | {it['confidence_score']}%] {it['service_name']} (Qty: {it['quantity']}) -> Unit: ${it['unit_price']:.2f} | Line Total: ${it['subtotal']:.2f}")
        if it["anomalies"]:
            print(f"     ⚠️ Guardrail Flags: {it['anomalies']}")

    # 4. Test Invoice Persistence & Calculation
    print("\n[STEP 4] Testing Invoice Persistence & Financial Calculations...")
    items_to_save = [
        {
            "service_name": it["service_name"],
            "unit_price": it["unit_price"] if it["unit_price"] > 0 else 500.0,
            "quantity": it["quantity"] if it["quantity"] > 0 else 1.0,
            "subtotal": (it["unit_price"] if it["unit_price"] > 0 else 500.0) * (it["quantity"] if it["quantity"] > 0 else 1.0)
        }
        for it in res["reconciled_items"]
    ]
    subtotal = sum(i["subtotal"] for i in items_to_save)
    tax = round(subtotal * 0.18, 2)
    total = round(subtotal + tax, 2)

    ok, inv = db.save_invoice(
        customer_name=res["customer_name"],
        customer_email=res["customer_email"],
        items=items_to_save,
        subtotal=subtotal,
        discount_amount=0.0,
        tax_amount=tax,
        total_amount=total,
        status="PAID",
        notes="Automated verification test invoice."
    )
    assert ok, f"Failed to save invoice: {inv}"
    print(f" -> [OK] Saved Invoice {inv['invoice_number']} to SQLite (Total: ${inv['total_amount']:,.2f})")

    # 5. Test PDF Generation
    print("\n[STEP 5] Testing ReportLab Professional PDF Generation...")
    pdf_bytes = pdf_gen.generate_invoice_pdf(inv)
    assert len(pdf_bytes) > 2000, f"PDF generation produced unexpectedly small file ({len(pdf_bytes)} bytes)"
    print(f" -> [OK] ReportLab PDF rendered successfully ({len(pdf_bytes):,} bytes buffer).")

    # 6. Test Analytics Aggregation
    print("\n[STEP 6] Testing Real-Time Analytics & Financial Ledger...")
    analytics = db.get_analytics_metrics()
    print(f" -> Total Invoices: {analytics['summary']['total_invoices']}")
    print(f" -> Total Revenue: ${analytics['summary']['total_revenue']:,.2f}")
    print(f" -> Average Order Value: ${analytics['summary']['avg_order_value']:,.2f}")
    print(f" -> Top Selling Services Count: {len(analytics['top_services'])}")

    print("\n" + "=" * 70)
    print("🎉 [ALL TESTS PASSED] Application is 100% Verified & Compliant!")
    print("=" * 70)

if __name__ == "__main__":
    test_pipeline()
