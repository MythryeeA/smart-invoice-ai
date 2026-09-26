"""
Dual-Agent AI & ML Pipeline for SmartInvoice AI
- Agent 1: Natural Language Extraction Agent (Gemini / OpenAI / Intelligent Fallback)
- Agent 2: Catalog Reconciliation & ML Guardrails Agent (RapidFuzz matching & Anomaly checks)
"""

import os
import re
import json
from typing import Dict, List, Any, Optional

try:
    from rapidfuzz import process, fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    import difflib
    RAPIDFUZZ_AVAILABLE = False

from database import get_all_catalog_items

SYSTEM_PROMPT = """
You are an expert AI Billing & Invoice Data Extraction Agent.
Your task is to analyze raw customer messages, procurement emails, or order notes and extract structured invoice details.

You must extract:
1. customer_name: The client's name or company name (String).
2. customer_email: The client's email address (String). If not provided, return "".
3. items: A list of ordered services/products with:
   - service_name: Name or description of the service (String).
   - quantity: Numeric quantity requested (Float or Integer, default 1.0 if not specified).
4. raw_notes: Any special instructions, terms, or notes mentioned in the text (String).

Output MUST be strictly valid JSON matching this schema:
{
  "customer_name": "...",
  "customer_email": "...",
  "items": [
    {"service_name": "...", "quantity": 1.0}
  ],
  "raw_notes": "..."
}
"""

def extract_with_gemini(text: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Extract invoice data using Google Gemini API."""
    try:
        # Try google-genai client first
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{SYSTEM_PROMPT}\n\nCustomer Request:\n{text}",
            )
            raw_text = response.text
        except Exception:
            # Fallback to google.generativeai
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=api_key)
            model = genai_legacy.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(f"{SYSTEM_PROMPT}\n\nCustomer Request:\n{text}")
            raw_text = response.text

        # Clean JSON from markdown code blocks
        clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
        data = json.loads(clean_json)
        return data
    except Exception as e:
        print(f"Gemini API Extraction error: {e}")
        return None

def extract_with_openai(text: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Extract invoice data using OpenAI API."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Customer Request:\n{text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI API Extraction error: {e}")
        return None

def extract_rule_based_fallback(text: str) -> Dict[str, Any]:
    """
    Intelligent NLP & Heuristic Rule-Based fallback parser.
    Ensures seamless operation without an API key or when offline.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # 1. Extract Email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    customer_email = email_match.group(0) if email_match else "billing@example.com"

    # 2. Extract Customer Name / Organization
    customer_name = "Enterprise Client"
    name_patterns = [
        r"(?:client|customer|attn|from|bill to|invoice to|company)\s*[:,-]?\s*([A-Za-z0-9\s&]+?)(?:\n|\.|,|<|$)",
        r"(?:thanks|regards|sincerely|cheers),\s*([A-Za-z0-9\s&]+?)(?:\n|\.|\(|$)",
        r"^([A-Za-z0-9\s&]{3,40})(?:\s*-\s*Invoice Request)",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cand = match.group(1).strip()
            # Ignore non-names
            if cand.lower() not in ["team", "there", "all", "sir", "madam", "smartinvoice", "support", "please", "we need"]:
                customer_name = cand
                break

    # If domain in email looks informative and name is still default
    if customer_name == "Enterprise Client" and email_match:
        domain = customer_email.split("@")[1].split(".")[0].capitalize()
        if domain not in ["Gmail", "Yahoo", "Outlook", "Hotmail", "Example"]:
            customer_name = f"{domain} Corp"

    # 3. Extract Items and Quantities
    items = []
    
    number_words = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
        "seven": 7, "eight": 8, "nine": 9, "ten": 10, "single": 1, "double": 2, "monthly": 1
    }

    ignore_prefixes = [
        "hi", "hello", "dear", "regards", "sincerely", "thanks", "best", "cheers",
        "email:", "from:", "to:", "subject:", "client:", "customer:", "attn:", "company:",
        "please", "we need", "total", "subtotal", "invoice for"
    ]

    for line in lines:
        cleaned_line = line.strip()
        lower_line = cleaned_line.lower()

        # Skip headers / footers / emails
        if any(lower_line.startswith(ig) for ig in ignore_prefixes):
            continue
        if "@" in cleaned_line and len(cleaned_line.split()) <= 4:
            continue
        # Skip pure signature like "Sarah Connor" or "Marcus Vance (CFO)" if without quantity / bullets
        if not re.match(r"^[\s*\-\d\.\)\>•]+", line) and not re.search(r"\b(\d+|qty|quantity|x|\$)\b", lower_line):
            continue

        # Strip purely bullet markers (-, *, •, >, or numbered list like "1.", "2)")
        item_text = re.sub(r"^[\s*\-•\>]+", "", cleaned_line).strip()
        item_text = re.sub(r"^\d+[\.\)]\s+", "", item_text).strip()
        if not item_text or len(item_text) < 3:
            continue

        qty = 1.0
        service_str = item_text

        # Pattern: (qty: 3), (quantity: 2), x2, 2x, 6 months, etc.
        prefix_pattern = re.search(r"^(\-?\d+(?:\.\d+)?)\s*(?:x|units|hrs|hours|months|month)?\s+(?:of\s+)?([A-Za-z].*)$", item_text, re.IGNORECASE)
        qty_paren_pattern = re.search(r"^(.*?)\s*\(?(?:qty|quantity|count)\s*[:x]?\s*(\-?\d+(?:\.\d+)?)\s*\)?", item_text, re.IGNORECASE)
        
        if prefix_pattern:
            try:
                qty = float(prefix_pattern.group(1))
            except ValueError:
                qty = 1.0
            service_str = prefix_pattern.group(2).strip()
        elif qty_paren_pattern:
            service_str = qty_paren_pattern.group(1).strip()
            try:
                qty = float(qty_paren_pattern.group(2))
            except ValueError:
                qty = 1.0
        else:
            # Check number words like "two SEO Audits"
            words = item_text.split()
            if words and words[0].lower() in number_words:
                qty = float(number_words[words[0].lower()])
                service_str = " ".join(words[1:]).strip()

        # Clean trailing prices or details
        service_str = re.sub(r"\s*-\s*\$\d+.*$", "", service_str)
        service_str = re.sub(r"\s*\(\s*(?:not in|agreed|unit price).*?\)", "", service_str, flags=re.IGNORECASE)
        service_str = re.sub(r"[\.,;:!]+$", "", service_str).strip()

        # If valid service string remains
        if len(service_str) >= 3 and not any(service_str.lower().startswith(ig) for ig in ignore_prefixes):
            items.append({
                "service_name": service_str,
                "quantity": qty
            })

    # If no items parsed, fallback to general service
    if not items:
        items = [{"service_name": "Custom Software Consulting & Development", "quantity": 1.0}]

    return {
        "customer_name": customer_name,
        "customer_email": customer_email,
        "items": items,
        "raw_notes": "Extracted via SmartInvoice AI Natural Language Pipeline"
    }

# ----------------- AGENT 1: EXTRACTION ----------------- #

def agent_extract_invoice_data(raw_text: str, gemini_api_key: str = None, openai_api_key: str = None) -> Dict[str, Any]:
    """
    Agent 1 (Extraction): Extracts structured customer & line item details from raw natural language.
    """
    extracted_data = None
    extraction_source = "Fallback Rule-Based NLP Parser"

    # 1. Check Gemini
    api_key_gemini = gemini_api_key or os.environ.get("GEMINI_API_KEY")
    if api_key_gemini and not extracted_data:
        res = extract_with_gemini(raw_text, api_key_gemini)
        if res and isinstance(res, dict) and "items" in res:
            extracted_data = res
            extraction_source = "Google Gemini LLM (Structured Output)"

    # 2. Check OpenAI
    api_key_openai = openai_api_key or os.environ.get("OPENAI_API_KEY")
    if api_key_openai and not extracted_data:
        res = extract_with_openai(raw_text, api_key_openai)
        if res and isinstance(res, dict) and "items" in res:
            extracted_data = res
            extraction_source = "OpenAI GPT-4o-mini (Structured Output)"

    # 3. Fallback
    if not extracted_data:
        extracted_data = extract_rule_based_fallback(raw_text)

    # Sanitize and guarantee schema structure
    items = extracted_data.get("items", [])
    sanitized_items = []
    for it in items:
        if isinstance(it, dict):
            s_name = str(it.get("service_name", "General Service")).strip()
            try:
                qty = float(it.get("quantity", 1.0))
            except (ValueError, TypeError):
                qty = 1.0
            sanitized_items.append({"service_name": s_name, "quantity": qty})

    result = {
        "customer_name": str(extracted_data.get("customer_name", "Enterprise Client")).strip(),
        "customer_email": str(extracted_data.get("customer_email", "billing@example.com")).strip(),
        "items": sanitized_items if sanitized_items else [{"service_name": "General Consulting", "quantity": 1.0}],
        "raw_notes": str(extracted_data.get("raw_notes", "")).strip(),
        "extraction_engine": extraction_source
    }
    return result

# ----------------- AGENT 2: RECONCILIATION & ML GUARDRAILS ----------------- #

def calculate_similarity(query: str, target: str) -> float:
    """Calculate string similarity score between 0 and 100."""
    q_clean = query.lower().strip()
    t_clean = target.lower().strip()
    
    if RAPIDFUZZ_AVAILABLE:
        # Token sort ratio gives high score even if words are reordered (e.g. "API Backend Python" vs "Python Backend API")
        score_token = fuzz.token_sort_ratio(q_clean, t_clean)
        score_partial = fuzz.partial_ratio(q_clean, t_clean)
        score_ratio = fuzz.ratio(q_clean, t_clean)
        return max(score_token, score_partial * 0.9, score_ratio)
    else:
        seq = difflib.SequenceMatcher(None, q_clean, t_clean)
        return seq.ratio() * 100.0

def agent_reconcile_and_guardrails(extracted_data: Dict[str, Any], catalog_items: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Agent 2 (Reconciliation & ML Guardrails):
    - Matches extracted items against SQLite catalog using ML fuzzy similarity.
    - Evaluates match confidence scores (0-100%).
    - Detects unlisted items -> flags 'REQUIRES_MANUAL_PRICE'.
    - Runs safety guardrails & anomaly detection (Quantity <= 0, high orders, missing emails, etc.).
    """
    if catalog_items is None:
        catalog_items = get_all_catalog_items()

    catalog_dict = {item["service_name"]: item for item in catalog_items}
    catalog_names = list(catalog_dict.keys())

    reconciled_items = []
    overall_anomalies = []
    
    # 1. Customer Email & Name Guardrails
    cust_email = extracted_data.get("customer_email", "")
    cust_name = extracted_data.get("customer_name", "")

    if not cust_email or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", cust_email):
        overall_anomalies.append("⚠️ Customer email is invalid or missing. Please verify before dispatching.")
    
    if not cust_name or cust_name.lower() in ["enterprise client", "client", "customer", ""]:
        overall_anomalies.append("ℹ️ Generic customer name detected. Confirm company or client name.")

    # 2. Line Items Reconciliation & Guardrails
    for idx, raw_item in enumerate(extracted_data.get("items", []), start=1):
        extracted_name = raw_item.get("service_name", "").strip()
        raw_qty = raw_item.get("quantity", 1.0)
        
        try:
            qty = float(raw_qty)
        except (ValueError, TypeError):
            qty = 1.0

        item_anomalies = []
        
        # Check Quantity Anomalies
        if qty <= 0:
            item_anomalies.append("❌ Quantity <= 0 detected. Auto-adjusted to 1.0 for calculation safety.")
            qty = 1.0
        elif qty > 100:
            item_anomalies.append(f"⚠️ High volume order ({qty:.0f} units) detected. Please double-check bulk discount terms.")

        # Fuzzy Matching against Catalog
        best_match_name = None
        best_score = 0.0

        for cat_name in catalog_names:
            score = calculate_similarity(extracted_name, cat_name)
            if score > best_score:
                best_score = score
                best_match_name = cat_name

        # Determine Match Classification & Price
        # Threshold: >= 75% = MATCHED, 50-74% = SUGGESTED, < 50% = REQUIRES_MANUAL_PRICE
        if best_match_name and best_score >= 75.0:
            match_status = "MATCHED"
            catalog_entry = catalog_dict[best_match_name]
            unit_price = float(catalog_entry["unit_price"])
            category = catalog_entry["category"]
            matched_id = catalog_entry["id"]
        elif best_match_name and best_score >= 50.0:
            match_status = "SUGGESTED"
            catalog_entry = catalog_dict[best_match_name]
            unit_price = float(catalog_entry["unit_price"])
            category = catalog_entry["category"]
            matched_id = catalog_entry["id"]
            item_anomalies.append(f"🔍 Fuzzy match '{extracted_name}' → '{best_match_name}' ({best_score:.1f}% confidence). Review recommended.")
        else:
            match_status = "REQUIRES_MANUAL_PRICE"
            best_match_name = None
            unit_price = 0.0
            category = "Custom Service"
            matched_id = None
            item_anomalies.append("⚠️ Item not found in active catalog. Marked as REQUIRES_MANUAL_PRICE.")

        subtotal = round(qty * unit_price, 2)

        reconciled_items.append({
            "line_number": idx,
            "extracted_service_name": extracted_name,
            "service_name": best_match_name if best_match_name else extracted_name,
            "matched_catalog_name": best_match_name,
            "matched_catalog_id": matched_id,
            "category": category,
            "quantity": qty,
            "unit_price": unit_price,
            "subtotal": subtotal,
            "confidence_score": round(best_score, 1),
            "match_status": match_status,
            "anomalies": item_anomalies
        })

    # Calculate overall financial metrics
    subtotal_sum = sum(it["subtotal"] for it in reconciled_items)
    tax_default = round(subtotal_sum * 0.18, 2)
    total_default = round(subtotal_sum + tax_default, 2)

    # Reconciled Summary
    matched_count = sum(1 for it in reconciled_items if it["match_status"] == "MATCHED")
    manual_count = sum(1 for it in reconciled_items if it["match_status"] == "REQUIRES_MANUAL_PRICE")
    suggested_count = sum(1 for it in reconciled_items if it["match_status"] == "SUGGESTED")

    return {
        "customer_name": cust_name,
        "customer_email": cust_email,
        "raw_notes": extracted_data.get("raw_notes", ""),
        "extraction_engine": extracted_data.get("extraction_engine", "Unknown"),
        "reconciled_items": reconciled_items,
        "subtotal": subtotal_sum,
        "discount_amount": 0.0,
        "tax_rate_percent": 18.0,
        "tax_amount": tax_default,
        "total_amount": total_default,
        "overall_anomalies": overall_anomalies,
        "reconciliation_stats": {
            "total_items": len(reconciled_items),
            "matched_count": matched_count,
            "suggested_count": suggested_count,
            "manual_price_count": manual_count,
            "has_blocking_anomalies": (manual_count > 0)
        }
    }

# ----------------- FULL PIPELINE EXECUTION ----------------- #

def run_smart_invoice_pipeline(raw_prompt: str, gemini_api_key: str = None, openai_api_key: str = None) -> Dict[str, Any]:
    """
    Executes the complete end-to-end Dual-Agent AI & ML Pipeline:
    Agent 1 (Extraction) -> Agent 2 (Reconciliation & ML Guardrails)
    """
    # Step 1: Agent 1 Extraction
    agent1_output = agent_extract_invoice_data(
        raw_prompt,
        gemini_api_key=gemini_api_key,
        openai_api_key=openai_api_key
    )

    # Step 2: Agent 2 Reconciliation & Guardrails
    catalog_items = get_all_catalog_items()
    pipeline_result = agent_reconcile_and_guardrails(agent1_output, catalog_items)
    pipeline_result["agent1_raw_output"] = agent1_output
    
    return pipeline_result

if __name__ == "__main__":
    from database import init_db
    init_db()
    
    sample_text = """
    From: Sarah Jenkins (sarah.j@novastack.tech)
    Hi team, please prepare an invoice for NovaStack Technologies.
    We need:
    - 2 Python Backend APIs
    - 1 UI UX Design for website
    - 6 months cloud hosting & maintenance
    - 1 Custom Kubernetes Microservices Cluster Setup
    - Quantity: -2 SEO optimization (anomaly test)
    
    Thanks!
    """
    
    print("Testing Dual-Agent Pipeline...")
    res = run_smart_invoice_pipeline(sample_text)
    print("\n--- Pipeline Results ---")
    print(f"Customer: {res['customer_name']} <{res['customer_email']}>")
    print(f"Engine: {res['extraction_engine']}")
    print(f"Stats: {res['reconciliation_stats']}")
    print("\nReconciled Items:")
    for item in res["reconciled_items"]:
        print(f" - [{item['match_status']} {item['confidence_score']}%] {item['service_name']} | Qty: {item['quantity']} | Unit: ${item['unit_price']} | Total: ${item['subtotal']}")
        if item["anomalies"]:
            print(f"   Flags: {item['anomalies']}")
