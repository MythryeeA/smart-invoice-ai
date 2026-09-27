# ⚡ SmartInvoice AI — Autonomous Invoicing & Billing Engine

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**SmartInvoice AI** is an intelligent, production-ready AI billing and invoice reconciliation chatbot application. It understands customer requirements written in normal natural language (emails, chat logs, procurement requests), extracts customer details and requested line items, dynamically fetches and reconciles prices from data sources (SQLite, CSV, Excel, Google Sheets, Airtable), detects anomalies with ML guardrails, and generates professional PDF invoices with complete analytics.

---

## 🎯 Problem Statement Addressed

> **"Build a small AI-powered invoice Chatbot that understands a customer's requirement written in normal language, extracts customer details and requested services, and fetches the correct service prices from a simple source such as Google information Sheets, Airtable or Excel/CSV and generates a professional invoice for review."**

### ✅ How SmartInvoice AI Solves It:
1. **Natural Language Understanding**: Parses unstructured text/emails to extract Client Name, Billing Email, Requested Items, and Quantities using Gemini 2.5, GPT-4o, or an offline rule-based NLP engine.
2. **Dynamic Price Source Fetching**: Connects to SQLite catalog presets, uploads CSV/Excel pricing sheets, or syncs live from published Google Sheets/Airtable CSV URLs.
3. **Fuzzy ML Reconciliation & Guardrails**: Employs RapidFuzz token matching to map colloquial service names to official catalog items, assigns match confidence scores, flags unlisted items (`REQUIRES_MANUAL_PRICE`), and detects quantity/rate anomalies.
4. **Interactive Human-in-the-Loop Review**: Editable data grid (`st.data_editor`) with live taxes, discounts, and terms adjustment.
5. **Multi-Channel Professional Export**: Renders formatted ReportLab PDF invoices, one-click WhatsApp billing share links, and raw JSON technical exports.
6. **Live Business Analytics**: Real-time revenue charts, top-selling items breakdown, and transaction ledger.

---

## 🏗️ System Architecture

```
                               ┌─────────────────────────────────────────┐
                               │     Customer Natural Language Input     │
                               │  (Messy email, chat, procurement notes) │
                               └────────────────────┬────────────────────┘
                                                    │
                                                    ▼
    ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ AGENT 1: Natural Language Extraction Agent                                             │
    │ • Extracts: Customer Name, Email, Requested Items, Quantities                          │
    │ • Engines: Google Gemini 2.5 Flash / OpenAI GPT-4o-mini / Offline Rule-Based Parser    │
    └───────────────────────────────────────────────┬────────────────────────────────────────┘
                                                    │
                                                    ▼
    ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ AGENT 2: Dynamic Catalog Reconciliation & ML Guardrails                                │
    │ • Dynamic Sources: SQLite Catalog, CSV/Excel Uploads, Google Sheets / Airtable URLs    │
    │ • Matching Engine: RapidFuzz Levenshtein Token Sort Ratio                              │
    │ • Guardrails: Confidence Scores, Outlier Detection, Negative / Extreme Quantity Flags  │
    └───────────────────────────────────────────────┬────────────────────────────────────────┘
                                                    │
                                                    ▼
    ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ HUMAN-IN-THE-LOOP REVIEW & FINANCIAL ADJUSTMENTS                                       │
    │ • Interactive Data Grid (st.data_editor) with live calculation of Subtotal, Tax, Discs │
    └───────────────────────────────────────────────┬────────────────────────────────────────┘
                                                    │
                                                    ▼
    ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ OUTPUT & EXPORT ENGINE                                                                 │
    │ • ReportLab Vector PDF Invoice Generator                                               │
    │ • One-Click WhatsApp Billing Share Link (`wa.me`)                                      │
    │ • SQLite Transaction Ledger & Live Real-Time Analytics Dashboard                       │
    └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Setup & Local Execution

### 1. Clone the Repository
```bash
git clone https://github.com/MythryeeA/smart-invoice-ai.git
cd smart-invoice-ai
```

### 2. Create and Activate Virtual Environment (Optional)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Automated Test Suite
```bash
python test_app.py
```

### 5. Launch Application
```bash
streamlit run app.py
```
*The app will open automatically at `http://localhost:8501`.*

---

## 🧪 Testing & Verification

Run the built-in automated test suite to verify all pipeline components:
```bash
python test_app.py
```

**Test Coverage:**
- [x] Database initialization & schema verification
- [x] Pricing catalog import & export from CSV / Spreadsheet
- [x] Agent 1: Customer name, email, and item extraction
- [x] Agent 2: RapidFuzz ML matching & guardrail anomalies
- [x] Financial calculation & SQLite invoice persistence
- [x] ReportLab professional PDF generation (byte buffer verification)
- [x] Real-time analytics aggregation

---

## ☁️ Deployment Guide (Streamlit Community Cloud)

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "Deploy SmartInvoice AI"
   git push origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New App"**.
4. Select:
   - **Repository:** `MythryeeA/smart-invoice-ai`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. *(Optional)* In Advanced Settings, add your API keys (e.g. `GEMINI_API_KEY` or `OPENAI_API_KEY`).
6. Click **Deploy!** — Your app will be live with a public URL in seconds.

---

## 📁 Project Structure

```
smart-invoice-ai/
├── app.py                  # Main Streamlit Multi-Tab Application & UI
├── ai_agents.py            # Dual-Agent AI Extraction & Fuzzy ML Reconciliation Pipeline
├── database.py             # SQLite Data Layer, Catalog Presets, CSV/Sheets Engine
├── pdf_generator.py        # ReportLab Professional PDF Invoice Builder
├── test_app.py             # End-to-End Automated Test & Verification Suite
├── pricing_catalog.csv     # Sample External Pricing Catalog Data Source
├── requirements.txt        # Python Dependencies
├── .gitignore              # Git Ignore Configuration
└── README.md               # Project Documentation
```

---

## ⚖️ License
MIT License. Created for the **Kodnexus AI Build Battle Hackathon 2026**.
