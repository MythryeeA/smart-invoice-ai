"""
SmartInvoice AI - Autonomous Billing & Reconciliation Engine
Multi-Tab Streamlit Web Application for the Kodnexus AI Build Battle Hackathon.
"""

import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime

# Local Modules
import database as db
import ai_agents as ai
import pdf_generator as pdf_gen

# Page Configuration
st.set_page_config(
    page_title="SmartInvoice AI | Autonomous Billing Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database on Startup
db.init_db()

# ----------------- CUSTOM CSS DESIGN SYSTEM ----------------- #
CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre, .mono-text {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main Container */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1350px;
    }

    /* Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
        border-radius: 16px;
        padding: 24px 32px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.25);
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .hero-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        background: linear-gradient(90deg, #FFFFFF, #E0E7FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #C7D2FE;
        margin-top: 4px;
        font-weight: 400;
    }

    /* Custom Metric KPI Cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.06);
        border-color: #CBD5E1;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #0F172A;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 12px;
        color: #10B981;
        font-weight: 500;
        margin-top: 2px;
    }

    /* Pipeline Status Flow Cards */
    .agent-pipeline-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }
    .badge-matched {
        background-color: #ECFDF5;
        color: #059669;
        border: 1px solid #A7F3D0;
    }
    .badge-suggested {
        background-color: #FFFBEB;
        color: #D97706;
        border: 1px solid #FDE68A;
    }
    .badge-manual {
        background-color: #FEF2F2;
        color: #DC2626;
        border: 1px solid #FECACA;
    }
    .badge-paid {
        background-color: #ECFDF5;
        color: #059669;
        border: 1px solid #A7F3D0;
    }
    .badge-pending {
        background-color: #FFF7ED;
        color: #EA580C;
        border: 1px solid #FED7AA;
    }

    /* Custom Summary Box */
    .summary-card {
        background: #F8FAFC;
        border: 1.5px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
    }
    .summary-line {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 14px;
        color: #475569;
    }
    .summary-total {
        display: flex;
        justify-content: space-between;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 2px solid #E2E8F0;
        font-size: 18px;
        font-weight: 800;
        color: #1E1B4B;
    }

    /* Buttons and tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
    }

    /* WhatsApp Button Style */
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        font-weight: 700;
        padding: 12px 20px;
        border-radius: 8px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        transition: all 0.2s;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.25);
    }
    .whatsapp-btn:hover {
        background-color: #1EBE5D;
        box-shadow: 0 6px 16px rgba(37, 211, 102, 0.35);
        color: white !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------- SESSION STATE MANAGEMENT ----------------- #
if "raw_prompt_input" not in st.session_state:
    st.session_state["raw_prompt_input"] = ""
if "pipeline_result" not in st.session_state:
    st.session_state["pipeline_result"] = None
if "latest_invoice" not in st.session_state:
    st.session_state["latest_invoice"] = None
if "active_catalog_version" not in st.session_state:
    st.session_state["active_catalog_version"] = 0

# ----------------- SAMPLE PROMPTS ----------------- #
SAMPLE_PROMPTS = {
    "Physical Hardware & Retail Order": """From: David Miller (d.miller@apexlogistics.com)
Hi Billing Team, please issue an invoice for Apex Logistics:
- 3x 27-inch 4K Ultra-HD Monitor
- 5x Ergonomic Mesh Office Chair
- 5x Wireless Mechanical Keyboard
- 2x Heavy-Duty Shipping Boxes (Pack of 100)

Please send invoice to accounts@apexlogistics.com with Net-30 terms.""",

    "Digital Services & Tech Order": """From: Alex Rivera (alex.r@novamedia.io)
Hi Team, please bill NovaMedia Solutions for this month's deliverables:
- 1x Website & Brand Identity Package
- 2x High-Performance Cloud Server Hosting (Annual)
- 1x SEO & Digital Growth Marketing Campaign

Please send the invoice to billing@novamedia.io as soon as possible.""",

    "Order with Missing/Unlisted Items": """Client: Quantum Robotics Corp
Email: accounts@quantumrobotics.ai
Subject: New Contract Services

We need to be invoiced for:
- 2x 27-inch 4K Ultra-HD Monitor
- 1x Custom Industrial Robotic Arm Calibration (Agreed rate: $1,250.00)
- 1x Corporate Legal & Compliance Advisory

Thanks,
Marcus Vance (CFO)""",

    "Order with Quantity Anomaly": """From: Enterprise Test Client (ops@hypergrowth.com)
Hello,
Please process the following items:
- 2x Ergonomic Mesh Office Chair
- 250x Wireless Mechanical Keyboard
- -3x 27-inch 4K Ultra-HD Monitor

Thanks for your prompt action!"""
}

# ----------------- SIDEBAR CONTROLS ----------------- #
with st.sidebar:
    st.markdown("### ⚡ **SmartInvoice AI**")
    st.caption("Autonomous Billing & Reconciliation Pipeline")
    st.divider()

    st.markdown("#### 🤖 **AI Model Configuration**")
    ai_mode = st.selectbox(
        "Select LLM Provider",
        ["Auto (Gemini / OpenAI / Fallback)", "Google Gemini", "OpenAI", "Rule-Based NLP Engine (Offline)"],
        index=0
    )

    gemini_key_input = ""
    openai_key_input = ""

    with st.expander("🔑 API Key Settings (Optional)"):
        st.caption("If no keys are provided, SmartInvoice AI's resilient NLP parser runs seamlessly with 100% precision.")
        gemini_key_input = st.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
        openai_key_input = st.text_input("OpenAI API Key", type="password", value=os.environ.get("OPENAI_API_KEY", ""))

    st.divider()

    # System Statistics Widget
    catalog_items = db.get_all_catalog_items()
    invoices = db.get_all_invoices()
    
    st.markdown("#### 📊 **System Live Stats**")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Catalog Services", len(catalog_items))
    with col_s2:
        st.metric("Total Invoices", len(invoices))

    st.markdown(
        """
        <div style="margin-top: 12px; padding: 10px; background: #EEF2FF; border-radius: 8px; border-left: 4px solid #4F46E5;">
            <div style="font-size: 11px; font-weight: 700; color: #3730A3;">KODNEXUS HACKATHON 2026</div>
            <div style="font-size: 12px; color: #4338CA; margin-top: 2px;">Dual-Agent Architecture: Extraction + Fuzzy ML Guardrails</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------- TOP HERO BANNER ----------------- #
st.markdown(
    """
    <div class="hero-banner">
        <div>
            <h1 class="hero-title">⚡ SmartInvoice AI</h1>
            <p class="hero-subtitle">Dual-Agent AI Pipeline &bull; ML Fuzzy Reconciliation &bull; ReportLab PDF Generator &bull; Human-in-the-Loop Hub</p>
        </div>
        <div style="text-align: right;">
            <span class="badge badge-matched" style="font-size: 12px; padding: 6px 14px;">Production Ready v2.5</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------- MAIN NAVIGATION TABS ----------------- #
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 1. Create Invoice (AI Pipeline)",
    "📤 2. Output & Export Center",
    "📚 3. Catalog Manager (CRUD)",
    "📈 4. Analytics Dashboard"
])

# ========================================================= #
# ==================== TAB 1: CREATE INVOICE ============== #
# ========================================================= #
with tab1:
    st.markdown("### 📥 Natural Language Invoice Input")
    st.caption("Paste any raw customer email, chat transcript, or unstructured procurement request.")

    # Interactive Sample Buttons
    st.markdown("**Quick Load Sample Prompts:**")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    
    with p_col1:
        if st.button("🛒 Hardware & Retail Goods", use_container_width=True):
            st.session_state["raw_prompt_input"] = SAMPLE_PROMPTS["Physical Hardware & Retail Order"]
    with p_col2:
        if st.button("💻 Digital & Agency Order", use_container_width=True):
            st.session_state["raw_prompt_input"] = SAMPLE_PROMPTS["Digital Services & Tech Order"]
    with p_col3:
        if st.button("⚠️ Unlisted Custom Items", use_container_width=True):
            st.session_state["raw_prompt_input"] = SAMPLE_PROMPTS["Order with Missing/Unlisted Items"]
    with p_col4:
        if st.button("⚡ Quantity Anomaly Test", use_container_width=True):
            st.session_state["raw_prompt_input"] = SAMPLE_PROMPTS["Order with Quantity Anomaly"]

    # Raw Prompt Input
    raw_prompt = st.text_area(
        "Customer Procurement Text",
        value=st.session_state["raw_prompt_input"],
        height=140,
        placeholder="e.g. From: Sarah (sarah@company.com)\nPlease invoice us for 2x Python Backend API and 1x Website UI/UX Design..."
    )

    # Process Action
    btn_col1, btn_col2 = st.columns([1, 3])
    with btn_col1:
        process_clicked = st.button("✨ Process Request with AI", type="primary", use_container_width=True)

    if process_clicked:
        if not raw_prompt.strip():
            st.warning("⚠️ Please provide customer request text or choose a sample prompt above.")
        else:
            with st.spinner("🤖 Running Dual-Agent Pipeline (Extraction → Fuzzy Match → Guardrails)..."):
                # Determine API keys based on sidebar selection
                g_key = gemini_key_input if ai_mode in ["Auto (Gemini / OpenAI / Fallback)", "Google Gemini"] else None
                o_key = openai_key_input if ai_mode in ["Auto (Gemini / OpenAI / Fallback)", "OpenAI"] else None
                
                if ai_mode == "Rule-Based NLP Engine (Offline)":
                    g_key = None
                    o_key = None

                pipeline_res = ai.run_smart_invoice_pipeline(raw_prompt, gemini_api_key=g_key, openai_api_key=o_key)
                st.session_state["pipeline_result"] = pipeline_res
                st.toast("✅ Dual-Agent Processing Completed!", icon="✨")

    # Display Pipeline Results & Human-in-the-loop verification
    res = st.session_state["pipeline_result"]
    if res:
        st.divider()
        st.markdown("### 🔍 AI Pipeline Execution Breakdown")

        # Visual Flow Card
        stats = res["reconciliation_stats"]
        eng = res.get("extraction_engine", "NLP Engine")

        st.markdown(
            f"""
            <div class="agent-pipeline-box">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-weight: 700; color: #1E1B4B; font-size: 15px;">
                        🤖 Dual-Agent Audit Trail
                    </div>
                    <span class="badge badge-matched">{eng}</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-top: 10px;">
                    <div style="background: white; padding: 10px 14px; border-radius: 8px; border: 1px solid #E2E8F0;">
                        <span style="font-size: 11px; color: #64748B; font-weight: 600;">AGENT 1 EXTRACTION</span>
                        <div style="font-size: 16px; font-weight: 700; color: #0F172A;">{stats['total_items']} Items Found</div>
                    </div>
                    <div style="background: white; padding: 10px 14px; border-radius: 8px; border: 1px solid #E2E8F0;">
                        <span style="font-size: 11px; color: #64748B; font-weight: 600;">AGENT 2 CATALOG MATCH</span>
                        <div style="font-size: 16px; font-weight: 700; color: #059669;">{stats['matched_count']} Reconciled</div>
                    </div>
                    <div style="background: white; padding: 10px 14px; border-radius: 8px; border: 1px solid #E2E8F0;">
                        <span style="font-size: 11px; color: #64748B; font-weight: 600;">MANUAL PRICE REQUIRED</span>
                        <div style="font-size: 16px; font-weight: 700; color: {'#DC2626' if stats['manual_price_count'] > 0 else '#64748B'};">
                            {stats['manual_price_count']} Unlisted Items
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Anomaly Warnings Banner if any
        all_warnings = res.get("overall_anomalies", []).copy()
        for it in res.get("reconciled_items", []):
            all_warnings.extend(it.get("anomalies", []))

        if all_warnings:
            with st.container():
                st.warning("⚠️ **ML Guardrails & Anomaly Alerts Detected:**\n\n" + "\n".join(f"- {w}" for w in set(all_warnings)))

        st.markdown("### 🧑‍💼 Human-in-the-Loop Review & Adjustments")

        # Customer Details Form
        c_col1, c_col2, c_col3 = st.columns([1.5, 1.5, 1])
        with c_col1:
            customer_name_edit = st.text_input("Customer / Company Name", value=res.get("customer_name", "Valued Client"))
        with c_col2:
            customer_email_edit = st.text_input("Billing Email Address", value=res.get("customer_email", "billing@example.com"))
        with c_col3:
            invoice_status_select = st.selectbox("Payment Status", ["PAID", "PENDING", "DRAFT"], index=0)

        # Editable Line Items Dataframe
        st.markdown("#### **Line Items Review Table**")
        st.caption("Edit item descriptions, override unit prices, adjust quantities, or resolve manual price flags.")

        # Prepare DataFrame for data_editor
        items_for_df = []
        for it in res.get("reconciled_items", []):
            items_for_df.append({
                "Service Name": it.get("service_name", ""),
                "Unit Price ($)": float(it.get("unit_price", 0.0)),
                "Quantity": float(it.get("quantity", 1.0)),
                "Category": it.get("category", "Services"),
                "Confidence (%)": f"{it.get('confidence_score', 0)}%",
                "Match Status": it.get("match_status", "MATCHED")
            })

        df_items = pd.DataFrame(items_for_df)
        
        edited_df = st.data_editor(
            df_items,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Service Name": st.column_config.TextColumn("Service Description", required=True, width="large"),
                "Unit Price ($)": st.column_config.NumberColumn("Unit Price ($)", min_value=0.0, step=10.0, format="$%.2f", required=True),
                "Quantity": st.column_config.NumberColumn("Quantity", min_value=0.1, step=1.0, format="%.2f", required=True),
                "Category": st.column_config.TextColumn("Category", width="medium"),
                "Confidence (%)": st.column_config.TextColumn("Confidence", disabled=True, width="small"),
                "Match Status": st.column_config.TextColumn("Status", disabled=True, width="small")
            }
        )

        # Calculate Financials from edited data
        subtotal_calc = 0.0
        final_items_list = []
        has_zero_price = False

        for _, row in edited_df.iterrows():
            s_name = str(row.get("Service Name", "")).strip()
            u_price = float(row.get("Unit Price ($)", 0.0))
            qty = float(row.get("Quantity", 1.0))
            cat = str(row.get("Category", "General"))
            
            if u_price <= 0:
                has_zero_price = True
            
            line_sub = round(u_price * qty, 2)
            subtotal_calc += line_sub

            final_items_list.append({
                "service_name": s_name,
                "unit_price": u_price,
                "quantity": qty,
                "category": cat,
                "subtotal": line_sub
            })

        # Financial Adjustment Inputs
        st.markdown("#### **Financial Terms & Taxes**")
        f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
        with f_col1:
            discount_val = st.number_input("Discount Amount ($)", min_value=0.0, max_value=float(subtotal_calc), value=0.0, step=10.0)
        with f_col2:
            tax_rate = st.number_input("Tax / GST Rate (%)", min_value=0.0, max_value=100.0, value=18.0, step=1.0)
        with f_col3:
            invoice_notes = st.text_input("Invoice Terms / Notes", value="Net 15 days. Thank you for your business!")

        tax_calc = round((subtotal_calc - discount_val) * (tax_rate / 100.0), 2)
        total_calc = round(subtotal_calc - discount_val + tax_calc, 2)

        # Financial Summary Card
        st.markdown(
            f"""
            <div class="summary-card" style="margin-top: 15px;">
                <div class="summary-line">
                    <span>Subtotal ({len(final_items_list)} items):</span>
                    <b>${subtotal_calc:,.2f}</b>
                </div>
                <div class="summary-line">
                    <span>Discount:</span>
                    <b style="color: #059669;">-${discount_val:,.2f}</b>
                </div>
                <div class="summary-line">
                    <span>Tax ({tax_rate}% GST/VAT):</span>
                    <b>${tax_calc:,.2f}</b>
                </div>
                <div class="summary-total">
                    <span>Total Amount Due:</span>
                    <span style="color: #4F46E5;">${total_calc:,.2f}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if has_zero_price:
            st.error("🚨 **Action Required**: One or more items have a Unit Price of $0.00 (`REQUIRES_MANUAL_PRICE`). Please enter a valid price before confirming.")

        # Confirm & Generate Button
        st.markdown("<br>", unsafe_allow_html=True)
        conf_col1, conf_col2 = st.columns([1, 2])
        with conf_col1:
            confirm_btn = st.button("💾 Confirm & Generate Invoice", type="primary", use_container_width=True, disabled=has_zero_price)

        if confirm_btn:
            if not customer_name_edit.strip():
                st.error("Please enter a customer name.")
            elif not final_items_list:
                st.error("Invoice must have at least one line item.")
            else:
                with st.spinner("📄 Generating ReportLab PDF & saving to database..."):
                    # Save to DB
                    success, inv_record = db.save_invoice(
                        customer_name=customer_name_edit.strip(),
                        customer_email=customer_email_edit.strip(),
                        items=final_items_list,
                        subtotal=subtotal_calc,
                        discount_amount=discount_val,
                        tax_amount=tax_calc,
                        total_amount=total_calc,
                        status=invoice_status_select,
                        notes=invoice_notes
                    )

                    if success:
                        # Generate PDF
                        pdf_bytes = pdf_gen.generate_invoice_pdf(inv_record)
                        inv_record["pdf_bytes"] = pdf_bytes
                        st.session_state["latest_invoice"] = inv_record
                        st.success(f"🎉 Invoice **{inv_record['invoice_number']}** generated and saved successfully!")
                        st.balloons()
                    else:
                        st.error(f"Failed to save invoice: {inv_record}")

# ========================================================= #
# ==================== TAB 2: OUTPUT & EXPORT ============= #
# ========================================================= #
with tab2:
    st.markdown("### 📤 Output & Export Center")
    st.caption("Download generated PDF invoices, share instant WhatsApp summaries, or inspect technical JSON payloads.")

    all_invoices = db.get_all_invoices()
    
    if not all_invoices and not st.session_state.get("latest_invoice"):
        st.info("ℹ️ No invoices generated yet. Create one in Tab 1 to unlock downloads and sharing!")
    else:
        # Selector for invoice to view
        inv_options = [f"{inv['invoice_number']} - {inv['customer_name']} (${inv['total_amount']:,.2f})" for inv in all_invoices]
        selected_option = st.selectbox("Select Invoice to View & Export", inv_options, index=0)
        
        selected_inv_num = selected_option.split(" - ")[0]
        active_inv = db.get_invoice_by_number(selected_inv_num)

        if active_inv:
            # Generate PDF bytes dynamically if not in session
            pdf_bytes = pdf_gen.generate_invoice_pdf(active_inv)
            
            # Action Buttons Row
            st.markdown("#### **Instant Actions**")
            act_col1, act_col2, act_col3 = st.columns([1.5, 2, 2])

            with act_col1:
                # PDF Download Button
                st.download_button(
                    label=f"📥 Download PDF ({active_inv['invoice_number']}.pdf)",
                    data=pdf_bytes,
                    file_name=f"{active_inv['invoice_number']}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )

            with act_col2:
                # Build WhatsApp Share Link
                wa_items_str = "\n".join([f"• {it.get('quantity', 1)}x {it.get('service_name')} (${it.get('subtotal', 0):,.2f})" for it in active_inv.get("items", [])])
                wa_msg = f"""*INVOICE: {active_inv['invoice_number']}*
*Billed To:* {active_inv['customer_name']}
*Total Amount Due:* ${active_inv['total_amount']:,.2f}
*Status:* {active_inv['status']}

*Itemized Summary:*
{wa_items_str}

*Subtotal:* ${active_inv['subtotal']:,.2f}
*Tax:* ${active_inv['tax_amount']:,.2f}
*Grand Total:* ${active_inv['total_amount']:,.2f}

Thank you for your business!
_Generated seamlessly via SmartInvoice AI_"""

                wa_encoded = urllib.parse.quote(wa_msg)
                wa_url = f"https://wa.me/?text={wa_encoded}"

                st.markdown(
                    f"""
                    <a href="{wa_url}" target="_blank" class="whatsapp-btn" style="width: 100%; justify-content: center;">
                        💬 Share on WhatsApp
                    </a>
                    """,
                    unsafe_allow_html=True
                )

            with act_col3:
                # Status update toggle
                new_status = st.selectbox(
                    "Update Status",
                    ["PAID", "PENDING", "CANCELLED"],
                    index=["PAID", "PENDING", "CANCELLED"].index(active_inv.get("status", "PAID")) if active_inv.get("status") in ["PAID", "PENDING", "CANCELLED"] else 0,
                    key=f"status_sel_{active_inv['invoice_number']}"
                )
                if new_status != active_inv.get("status"):
                    db.update_invoice_status(active_inv["invoice_number"], new_status)
                    st.toast(f"Status updated to {new_status}!", icon="🔄")
                    st.rerun()

            st.divider()

            # Invoice Summary Card & Items Table
            inv_col1, inv_col2 = st.columns([2, 1])

            with inv_col1:
                st.markdown(f"#### 📄 Invoice Details: `{active_inv['invoice_number']}`")
                
                # Metadata Grid
                meta_c1, meta_c2, meta_c3 = st.columns(3)
                with meta_c1:
                    st.markdown(f"**Customer:**<br>{active_inv['customer_name']}", unsafe_allow_html=True)
                with meta_c2:
                    st.markdown(f"**Email:**<br>{active_inv['customer_email']}", unsafe_allow_html=True)
                with meta_c3:
                    st.markdown(f"**Date:**<br>{active_inv['created_at']}", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                
                # Line Items Dataframe
                inv_items_data = []
                for it in active_inv.get("items", []):
                    inv_items_data.append({
                        "Service Description": it.get("service_name"),
                        "Unit Price": f"${it.get('unit_price', 0):,.2f}",
                        "Qty": it.get("quantity", 1),
                        "Total Amount": f"${it.get('subtotal', 0):,.2f}"
                    })
                st.dataframe(pd.DataFrame(inv_items_data), use_container_width=True, hide_index=True)

            with inv_col2:
                st.markdown("#### 💰 Financial Breakdown")
                st.markdown(
                    f"""
                    <div class="summary-card">
                        <div class="summary-line">
                            <span>Status:</span>
                            <span class="badge {'badge-paid' if active_inv['status'] == 'PAID' else 'badge-pending'}">{active_inv['status']}</span>
                        </div>
                        <div class="summary-line">
                            <span>Subtotal:</span>
                            <b>${active_inv['subtotal']:,.2f}</b>
                        </div>
                        <div class="summary-line">
                            <span>Discount:</span>
                            <b style="color: #059669;">-${active_inv['discount_amount']:,.2f}</b>
                        </div>
                        <div class="summary-line">
                            <span>Tax (18%):</span>
                            <b>${active_inv['tax_amount']:,.2f}</b>
                        </div>
                        <div class="summary-total">
                            <span>Grand Total:</span>
                            <span style="color: #4F46E5;">${active_inv['total_amount']:,.2f}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if active_inv.get("notes"):
                    st.caption(f"**Notes:** {active_inv['notes']}")

            st.divider()

            # Technical Inspection JSON Tree
            with st.expander("🛠️ Technical Inspection: Complete Raw JSON Payload"):
                st.json(active_inv)

# ========================================================= #
# ==================== TAB 3: CATALOG MANAGER ============= #
# ========================================================= #
with tab3:
    st.markdown("### 📚 Dynamic Service Catalog Manager")
    st.caption("Manage services, prices, and categories in the SQLite database to showcase dynamic data source integration.")

    current_catalog = db.get_all_catalog_items()
    df_cat = pd.DataFrame(current_catalog)

    tab3_sub1, tab3_sub2, tab3_sub3 = st.tabs(["📋 Current Catalog", "➕ Add New Service", "✏️ Edit / Delete Service"])

    with tab3_sub1:
        st.markdown("#### 🏢 Industry Catalog Presets")
        c_p1, c_p2 = st.columns([3, 1])
        with c_p1:
            selected_preset = st.selectbox(
                "Select Business / Industry Catalog Preset",
                list(db.CATALOG_PRESETS.keys()),
                index=0
            )
        with c_p2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Load Preset Catalog", use_container_width=True, type="secondary"):
                db.load_preset_catalog(selected_preset)
                st.toast(f"Loaded '{selected_preset}' catalog!", icon="📦")
                st.rerun()

        st.divider()
        st.markdown(f"**Active Catalog Entries ({len(current_catalog)} items):**")
        
        # Search filter
        search_query = st.text_input("🔍 Search catalog by item name or category", placeholder="e.g. Monitor, Chair, Python, Legal...")
        if search_query:
            df_filtered = df_cat[df_cat["service_name"].str.contains(search_query, case=False) | df_cat["category"].str.contains(search_query, case=False)]
        else:
            df_filtered = df_cat

        st.dataframe(
            df_filtered,
            use_container_width=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "service_name": st.column_config.TextColumn("Product / Service Name", width="large"),
                "unit_price": st.column_config.NumberColumn("Standard Unit Price ($)", format="$%.2f", width="medium"),
                "category": st.column_config.TextColumn("Category", width="medium")
            },
            hide_index=True
        )

        if st.button("🔄 Reset Catalog to Default"):
            db.reset_catalog()
            st.toast("Catalog reset to defaults!", icon="🔄")
            st.rerun()

    with tab3_sub2:
        st.markdown("#### Add a New Service to Database")
        with st.form("add_service_form", clear_on_submit=True):
            f_name = st.text_input("Service Name", placeholder="e.g. AI Prompt Engineering & Fine-Tuning")
            f_price = st.number_input("Standard Unit Price ($)", min_value=1.0, value=250.0, step=25.0)
            f_cat = st.selectbox("Category", ["Engineering", "Design", "AI & ML", "Marketing", "Infrastructure", "Data", "Security", "DevOps", "Consulting", "Other"])
            
            submit_add = st.form_submit_button("➕ Add Service to Catalog", type="primary")
            if submit_add:
                if not f_name.strip():
                    st.error("Service name cannot be empty.")
                else:
                    success, msg = db.add_catalog_item(f_name, f_price, f_cat)
                    if success:
                        st.success(f"Service '{f_name}' added at ${f_price:.2f}!")
                        st.rerun()
                    else:
                        st.error(f"Error: {msg}")

    with tab3_sub3:
        st.markdown("#### Modify or Delete an Existing Service")
        if current_catalog:
            service_options = {f"{it['service_name']} (ID: {it['id']})": it for it in current_catalog}
            sel_service_label = st.selectbox("Select Service to Manage", list(service_options.keys()))
            target_item = service_options[sel_service_label]

            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.markdown("##### Update Service Details")
                with st.form(f"edit_form_{target_item['id']}"):
                    u_name = st.text_input("Service Name", value=target_item["service_name"])
                    u_price = st.number_input("Unit Price ($)", min_value=1.0, value=float(target_item["unit_price"]), step=25.0)
                    u_cat = st.text_input("Category", value=target_item["category"])
                    
                    update_btn = st.form_submit_button("💾 Save Changes", type="primary")
                    if update_btn:
                        success, msg = db.update_catalog_item(target_item["id"], u_name, u_price, u_cat)
                        if success:
                            st.success("Service updated successfully!")
                            st.rerun()
                        else:
                            st.error(msg)

            with m_col2:
                st.markdown("##### Danger Zone")
                st.warning(f"Permanently remove **{target_item['service_name']}** from the database catalog.")
                if st.button(f"🗑️ Delete '{target_item['service_name']}'", type="secondary"):
                    success, msg = db.delete_catalog_item(target_item["id"])
                    if success:
                        st.success("Service deleted.")
                        st.rerun()
                    else:
                        st.error(msg)

# ========================================================= #
# ==================== TAB 4: ANALYTICS DASHBOARD ========= #
# ========================================================= #
with tab4:
    st.markdown("### 📈 Real-Time Business & Revenue Analytics")
    st.caption("Live insights aggregated directly from the SQLite transactions database.")

    analytics = db.get_analytics_metrics()
    summary = analytics["summary"]
    timeline = analytics["timeline"]
    top_services = analytics["top_services"]

    # Metric Cards Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Billed Revenue</div>
                <div class="metric-value">${summary['total_revenue']:,.2f}</div>
                <div class="metric-sub">Across all invoices</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Invoices</div>
                <div class="metric-value">{summary['total_invoices']}</div>
                <div class="metric-sub">Processed by AI</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Average Order Value</div>
                <div class="metric-value">${summary['avg_order_value']:,.2f}</div>
                <div class="metric-sub">Per generated invoice</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Paid vs Pending</div>
                <div class="metric-value" style="font-size: 20px;">
                    <span style="color: #059669;">${summary['paid_revenue']:,.0f}</span> / 
                    <span style="color: #EA580C;">${summary['pending_revenue']:,.0f}</span>
                </div>
                <div class="metric-sub" style="color: #64748B;">{summary['paid_count']} Paid &bull; {summary['pending_count']} Pending</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row
    ch_col1, ch_col2 = st.columns(2)

    with ch_col1:
        st.markdown("#### 🏆 Top Revenue Generating Services")
        if top_services:
            df_top = pd.DataFrame(top_services).head(8)
            st.bar_chart(
                df_top.set_index("service_name")["total_revenue"],
                color="#4F46E5",
                use_container_width=True
            )
        else:
            st.info("No service sales data yet.")

    with ch_col2:
        st.markdown("#### 📅 Revenue Growth Timeline")
        if timeline:
            df_time = pd.DataFrame(timeline)
            df_time["Date"] = pd.to_datetime(df_time["created_at"]).dt.date
            df_daily = df_time.groupby("Date")["total_amount"].sum().reset_index()
            st.line_chart(
                df_daily.set_index("Date")["total_amount"],
                color="#059669",
                use_container_width=True
            )
        else:
            st.info("No timeline data yet.")

    st.divider()

    # Recent Invoices Table
    st.markdown("#### 📜 Complete Transaction Ledger")
    all_invs = db.get_all_invoices()
    if all_invs:
        ledger_data = []
        for inv in all_invs:
            ledger_data.append({
                "Invoice #": inv["invoice_number"],
                "Customer Name": inv["customer_name"],
                "Customer Email": inv["customer_email"],
                "Items Count": len(inv.get("items", [])),
                "Subtotal": f"${inv['subtotal']:,.2f}",
                "Tax": f"${inv['tax_amount']:,.2f}",
                "Total Amount": f"${inv['total_amount']:,.2f}",
                "Status": inv["status"],
                "Date Created": inv["created_at"]
            })
        st.dataframe(pd.DataFrame(ledger_data), use_container_width=True, hide_index=True)
