# ⚡ SmartInvoice AI

**SmartInvoice AI** is a production-grade autonomous billing and reconciliation application built for the **Kodnexus AI Build Battle Hackathon 2026**. It transforms unstructured customer communications into validated, itemized invoices with enterprise guardrails.

---

### 🌟 Key Highlights & Architecture

1. **Dual-Agent AI Pipeline**:
   - **Agent 1 (Extraction)**: Extracts structured customer details, emails, line items, and quantities from messy emails or text prompts (Gemini / GPT-4o / Resilient NLP fallback).
   - **Agent 2 (Fuzzy ML Reconciliation & Guardrails)**: Matches items against the dynamic SQLite catalog using RapidFuzz, assigns confidence scores, detects unlisted items (`REQUIRES_MANUAL_PRICE`), and catches quantity/pricing anomalies.

2. **Enterprise Multi-Tab UI (Streamlit)**:
   - **Create & Review**: Interactive prompt samples, visual agent audit trail, and Human-in-the-Loop editable grid (`st.data_editor`) with live tax/discount calculations.
   - **Export Center**: Instant styled ReportLab PDF download, one-click WhatsApp share button (`wa.me`), and raw JSON inspector.
   - **Catalog Manager (CRUD)**: Dynamic management of database services and pricing.
   - **Analytics Dashboard**: Real-time KPI metric cards, revenue trends, top-selling services, and ledger.

---

### 🚀 Quick Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch application
streamlit run app.py
```
