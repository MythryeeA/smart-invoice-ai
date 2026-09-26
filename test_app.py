import os
import sys
import io

# Set UTF-8 encoding for standard output if needed
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import database as db
import ai_agents as ai
import pdf_generator as pdf_gen

def test_pipeline():
    print("[TEST] Starting SmartInvoice AI End-to-End Verification...")

    # 1. Test Database
    db.init_db()
    cats = db.get_all_catalog_items()
    print(f"[OK] Catalog loaded with {len(cats)} active services.")
    assert len(cats) >= 8, f"Expected at least 8 catalog services, found {len(cats)}"

    # 2. Test Dual-Agent AI Pipeline
    test_prompt = """From: Sarah Connor (sconnor@cyberdyne.ai)
Subject: Project Billing

Hi Support,
Please invoice Cyberdyne Systems for the following:
- 2x Python Backend API Development
- 1x Website UI/UX Design
- 6 months Monthly Cloud Hosting & Maintenance
- 1x Proprietary Quantum Logic Board Installation
- Quantity: -4 SEO Audit & Optimization

Thanks,
Sarah Connor"""

    print("\n[TEST] Running Agent 1 (Extraction) & Agent 2 (Reconciliation + Guardrails)...")
    res = ai.run_smart_invoice_pipeline(test_prompt)

    print(f"Extracted Customer: {res['customer_name']}")
    print(f"Extracted Email: {res['customer_email']}")
    print(f"Extraction Engine: {res['extraction_engine']}")
    print(f"Total Items Extracted: {len(res['reconciled_items'])}")
    print(f"Reconciliation Stats: {res['reconciliation_stats']}")

    assert res["customer_name"] != "", "Failed to extract customer name"
    assert len(res["reconciled_items"]) >= 4, "Failed to extract line items"

    for it in res["reconciled_items"]:
        print(f" - [{it['match_status']} | {it['confidence_score']}%] {it['service_name']} (Qty: {it['quantity']}) -> Unit: ${it['unit_price']} | Total: ${it['subtotal']}")
        if it["anomalies"]:
            print(f"   Flags: {it['anomalies']}")

    # 3. Test Invoice Persistence
    items_to_save = [
        {"service_name": it["service_name"], "unit_price": it["unit_price"] if it["unit_price"] > 0 else 500.0, "quantity": it["quantity"], "subtotal": it["unit_price"] * it["quantity"] if it["unit_price"] > 0 else 500.0}
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
        notes="Automated test generation."
    )
    assert ok, f"Failed to save invoice: {inv}"
    print(f"\n[OK] Invoice saved successfully: {inv['invoice_number']} (Total: ${inv['total_amount']:,.2f})")

    # 4. Test PDF Generation
    pdf_bytes = pdf_gen.generate_invoice_pdf(inv)
    assert len(pdf_bytes) > 2000, f"PDF generation produced unexpectedly small file ({len(pdf_bytes)} bytes)"
    print(f"[OK] ReportLab PDF generated successfully: {len(pdf_bytes):,} bytes")

    # 5. Test Analytics Aggregation
    analytics = db.get_analytics_metrics()
    print(f"\n[OK] Analytics Summary:")
    print(f" - Total Invoices: {analytics['summary']['total_invoices']}")
    print(f" - Total Revenue: ${analytics['summary']['total_revenue']:,.2f}")
    print(f" - Average Order Value: ${analytics['summary']['avg_order_value']:,.2f}")
    print(f" - Top Selling Services Count: {len(analytics['top_services'])}")

    print("\n[PASS] ALL TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_pipeline()

