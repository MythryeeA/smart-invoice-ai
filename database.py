"""
Database & Data Layer for SmartInvoice AI
SQLite implementation for managing Service Catalog and Invoices.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "invoice_app.db")

CATALOG_PRESETS = {
    "Multi-Industry (Retail, Hardware & Services)": [
        ("27-inch 4K Ultra-HD Monitor", 380.0, "Electronics & Hardware"),
        ("Ergonomic Mesh Office Chair", 240.0, "Office Furniture"),
        ("Wireless Mechanical Keyboard", 110.0, "Computer Accessories"),
        ("Website & Brand Identity Package", 650.0, "Creative & Design"),
        ("Corporate Legal & Compliance Advisory", 350.0, "Professional Consulting"),
        ("High-Performance Cloud Server Hosting (Annual)", 450.0, "IT & Infrastructure"),
        ("SEO & Digital Growth Marketing Campaign", 200.0, "Marketing"),
        ("Heavy-Duty Shipping Boxes (Pack of 100)", 85.0, "Logistics & Supplies"),
        ("Enterprise Software License (Annual)", 500.0, "Software"),
        ("Corporate Training & Onboarding Workshop", 300.0, "Human Resources")
    ],
    "Tech & Software Agency": [
        ("Website UI/UX Design", 500.0, "Design"),
        ("Python Backend API Development", 400.0, "Engineering"),
        ("SEO Audit & Optimization", 200.0, "Marketing"),
        ("Monthly Cloud Hosting & Maintenance", 50.0, "Infrastructure"),
        ("Mobile App Development (Flutter/React Native)", 800.0, "Engineering"),
        ("Database Optimization & Migration", 350.0, "Data"),
        ("AI Chatbot Integration", 600.0, "AI & ML"),
        ("Cybersecurity Vulnerability Assessment", 450.0, "Security"),
        ("Content Writing & Copywriting (1000 words)", 75.0, "Marketing"),
        ("DevOps CI/CD Pipeline Setup", 300.0, "DevOps")
    ],
    "Retail & Hardware Goods": [
        ("27-inch 4K Ultra-HD Monitor", 380.0, "Electronics"),
        ("Ergonomic Mesh Office Chair", 240.0, "Furniture"),
        ("Wireless Mechanical Keyboard", 110.0, "Accessories"),
        ("USB-C Dual 4K Docking Station", 160.0, "Electronics"),
        ("Noise-Cancelling Bluetooth Headset", 190.0, "Audio"),
        ("Heavy-Duty Shipping Boxes (Pack of 100)", 85.0, "Supplies"),
        ("Thermal Label Printer", 140.0, "Logistics"),
        ("Adjustable Standing Desk Converter", 220.0, "Furniture")
    ],
    "Corporate Consulting & Professional Services": [
        ("Corporate Legal & Compliance Advisory", 350.0, "Legal"),
        ("Financial Audit & Tax Strategy Session", 500.0, "Finance"),
        ("Brand Strategy & Go-To-Market Workshop", 600.0, "Strategy"),
        ("HR Recruitment & Executive Search (Per Role)", 750.0, "Human Resources"),
        ("Corporate Training & Skill Development (Per Day)", 450.0, "Training"),
        ("PR & Media Relations Management (Monthly)", 400.0, "Public Relations")
    ]
}

DEFAULT_CATALOG = CATALOG_PRESETS["Multi-Industry (Retail, Hardware & Services)"]

def get_db_connection():
    """Create and return a thread-safe connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables and pre-seed with default data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table 1: catalog
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT UNIQUE NOT NULL,
            unit_price REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)

    # Table 2: invoices
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            subtotal REAL NOT NULL,
            discount_amount REAL NOT NULL DEFAULT 0.0,
            tax_amount REAL NOT NULL DEFAULT 0.0,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'PAID',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            items_json TEXT NOT NULL,
            notes TEXT
        )
    """)

    # Pre-seed catalog if empty
    cursor.execute("SELECT COUNT(*) as count FROM catalog")
    if cursor.fetchone()["count"] == 0:
        cursor.executemany(
            "INSERT INTO catalog (service_name, unit_price, category) VALUES (?, ?, ?)",
            DEFAULT_CATALOG
        )

    # Pre-seed sample historical invoices if invoices table is empty
    cursor.execute("SELECT COUNT(*) as count FROM invoices")
    if cursor.fetchone()["count"] == 0:
        seed_sample_invoices(cursor)

    conn.commit()
    conn.close()

def seed_sample_invoices(cursor):
    """Seed initial sample invoices for rich analytics on first launch."""
    sample_customers = [
        ("Acme Corp", "billing@acmecorp.com", [
            {"service_name": "Website UI/UX Design", "quantity": 1, "unit_price": 500.0, "subtotal": 500.0},
            {"service_name": "Monthly Cloud Hosting & Maintenance", "quantity": 6, "unit_price": 50.0, "subtotal": 300.0}
        ], "PAID", 10),
        ("Starlight FinTech", "finance@starlight.io", [
            {"service_name": "Python Backend API Development", "quantity": 2, "unit_price": 400.0, "subtotal": 800.0},
            {"service_name": "Database Optimization & Migration", "quantity": 1, "unit_price": 350.0, "subtotal": 350.0},
            {"service_name": "AI Chatbot Integration", "quantity": 1, "unit_price": 600.0, "subtotal": 600.0}
        ], "PAID", 8),
        ("Nexus Media", "contact@nexusmedia.org", [
            {"service_name": "SEO Audit & Optimization", "quantity": 2, "unit_price": 200.0, "subtotal": 400.0},
            {"service_name": "Content Writing & Copywriting (1000 words)", "quantity": 5, "unit_price": 75.0, "subtotal": 375.0}
        ], "PAID", 5),
        ("CyberShield Ltd", "security@cybershield.net", [
            {"service_name": "Cybersecurity Vulnerability Assessment", "quantity": 1, "unit_price": 450.0, "subtotal": 450.0},
            {"service_name": "DevOps CI/CD Pipeline Setup", "quantity": 1, "unit_price": 300.0, "subtotal": 300.0}
        ], "PENDING", 2),
        ("HyperScale AI", "founders@hyperscale.ai", [
            {"service_name": "AI Chatbot Integration", "quantity": 2, "unit_price": 600.0, "subtotal": 1200.0},
            {"service_name": "Python Backend API Development", "quantity": 1, "unit_price": 400.0, "subtotal": 400.0}
        ], "PAID", 1),
    ]

    now = datetime.now()
    for idx, (name, email, items, status, days_ago) in enumerate(sample_customers, start=1001):
        subtotal = sum(item["subtotal"] for item in items)
        tax = round(subtotal * 0.18, 2)
        total = round(subtotal + tax, 2)
        inv_date = (now - timedelta(days=days_ago, hours=random.randint(1, 12))).strftime("%Y-%m-%d %H:%M:%S")
        inv_number = f"INV-2026-{idx}"
        
        cursor.execute("""
            INSERT INTO invoices (invoice_number, customer_name, customer_email, subtotal, discount_amount, tax_amount, total_amount, status, created_at, items_json, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (inv_number, name, email, subtotal, 0.0, tax, total, status, inv_date, json.dumps(items), "Thank you for partnering with us."))

# ----------------- CATALOG CRUD ----------------- #

def get_all_catalog_items():
    """Retrieve all items from the catalog sorted by category and name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, service_name, unit_price, category FROM catalog ORDER BY category, service_name")
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

def add_catalog_item(service_name: str, unit_price: float, category: str):
    """Add a new service item to the catalog."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO catalog (service_name, unit_price, category) VALUES (?, ?, ?)",
            (service_name.strip(), float(unit_price), category.strip())
        )
        conn.commit()
        return True, "Service added successfully."
    except sqlite3.IntegrityError:
        return False, f"A service named '{service_name}' already exists."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_catalog_item(item_id: int, service_name: str, unit_price: float, category: str):
    """Update an existing catalog item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE catalog SET service_name = ?, unit_price = ?, category = ? WHERE id = ?",
            (service_name.strip(), float(unit_price), category.strip(), item_id)
        )
        conn.commit()
        return True, "Service updated successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_catalog_item(item_id: int):
    """Delete a catalog item by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM catalog WHERE id = ?", (item_id,))
        conn.commit()
        return True, "Service deleted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def reset_catalog():
    """Reset catalog back to default services."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM catalog")
    cursor.executemany(
        "INSERT INTO catalog (service_name, unit_price, category) VALUES (?, ?, ?)",
        DEFAULT_CATALOG
    )
    conn.commit()
    conn.close()

def load_preset_catalog(preset_name: str):
    """Load a specific preset catalog into the SQLite database."""
    items = CATALOG_PRESETS.get(preset_name, DEFAULT_CATALOG)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM catalog")
    cursor.executemany(
        "INSERT INTO catalog (service_name, unit_price, category) VALUES (?, ?, ?)",
        items
    )
    conn.commit()
    conn.close()
    return True, f"Loaded preset '{preset_name}' with {len(items)} items."

# ----------------- INVOICES CRUD ----------------- #

def get_next_invoice_number():
    """Generate the next sequential invoice number."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM invoices ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    next_id = (row["id"] + 1) if row else 1001
    return f"INV-2026-{next_id:04d}"

def save_invoice(customer_name: str, customer_email: str, items: list, subtotal: float, discount_amount: float, tax_amount: float, total_amount: float, status: str = "PAID", notes: str = "", invoice_number: str = None):
    """Save a newly created invoice to the database."""
    if not invoice_number:
        invoice_number = get_next_invoice_number()

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO invoices (invoice_number, customer_name, customer_email, subtotal, discount_amount, tax_amount, total_amount, status, created_at, items_json, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (invoice_number, customer_name, customer_email, subtotal, discount_amount, tax_amount, total_amount, status, created_at, json.dumps(items), notes))
        conn.commit()
        inv_id = cursor.lastrowid
        return True, {
            "id": inv_id,
            "invoice_number": invoice_number,
            "created_at": created_at,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "status": status,
            "items": items,
            "notes": notes
        }
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_invoices():
    """Retrieve all invoices sorted by latest first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices ORDER BY id DESC")
    rows = cursor.fetchall()
    invoices = []
    for r in rows:
        item = dict(r)
        try:
            item["items"] = json.loads(item["items_json"])
        except Exception:
            item["items"] = []
        invoices.append(item)
    conn.close()
    return invoices

def get_invoice_by_number(invoice_number: str):
    """Retrieve a single invoice by its invoice number."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
    row = cursor.fetchone()
    conn.close()
    if row:
        item = dict(row)
        item["items"] = json.loads(item["items_json"])
        return item
    return None

def update_invoice_status(invoice_number: str, new_status: str):
    """Update payment status of an invoice."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE invoices SET status = ? WHERE invoice_number = ?", (new_status, invoice_number))
    conn.commit()
    conn.close()

# ----------------- ANALYTICS AGGREGATIONS ----------------- #

def get_analytics_metrics():
    """Calculate key financial and sales metrics for the analytics dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Summary stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total_invoices,
            COALESCE(SUM(total_amount), 0) as total_revenue,
            COALESCE(AVG(total_amount), 0) as avg_order_value,
            SUM(CASE WHEN status = 'PAID' THEN total_amount ELSE 0 END) as paid_revenue,
            SUM(CASE WHEN status = 'PENDING' THEN total_amount ELSE 0 END) as pending_revenue,
            SUM(CASE WHEN status = 'PAID' THEN 1 ELSE 0 END) as paid_count,
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending_count
        FROM invoices
    """)
    summary = dict(cursor.fetchone())

    # Invoices over time
    cursor.execute("SELECT created_at, total_amount, status FROM invoices ORDER BY created_at ASC")
    timeline = [dict(r) for r in cursor.fetchall()]

    # Service item sales frequency and revenue
    cursor.execute("SELECT items_json FROM invoices")
    all_items_rows = cursor.fetchall()
    
    service_breakdown = {}
    for row in all_items_rows:
        try:
            items = json.loads(row["items_json"])
            for item in items:
                name = item.get("service_name") or item.get("matched_service_name") or "Custom Service"
                qty = float(item.get("quantity", 1))
                subtotal = float(item.get("subtotal", qty * item.get("unit_price", 0)))
                
                if name not in service_breakdown:
                    service_breakdown[name] = {"service_name": name, "total_qty": 0, "total_revenue": 0.0, "orders_count": 0}
                service_breakdown[name]["total_qty"] += qty
                service_breakdown[name]["total_revenue"] += subtotal
                service_breakdown[name]["orders_count"] += 1
        except Exception:
            continue

    services_list = sorted(service_breakdown.values(), key=lambda x: x["total_revenue"], reverse=True)

    conn.close()
    return {
        "summary": summary,
        "timeline": timeline,
        "top_services": services_list
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
    print("Catalog items count:", len(get_all_catalog_items()))
    print("Invoices count:", len(get_all_invoices()))
