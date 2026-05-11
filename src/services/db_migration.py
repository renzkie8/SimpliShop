"""
Complete Database Migration & Seeding Script.
Run this ONCE to update your existing database with all missing tables AND populate it with medicines.
Includes: Pharmacist features + Staff/Patient features + Billing features + 54 Medicines + Sample Transactions.
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta
import random

# --- FIX: Add the parent directory to system path so we can import 'services' ---
# This is needed because we are running this script directly from the services folder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
# -------------------------------------------------------------------------------

from services.database import init_db

def run_migration_and_seed():
    """Add all necessary fields, tables, AND seed data to existing database."""
    
    # 1. Ensure base tables exist first
    print("🔄 Initializing base database structures...")
    init_db()
    
    # Get the correct path to your database
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, 'storage')
    DB_FILE = os.path.join(DB_PATH, "pharmacy.db")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        print("🔄 Starting complete database migration & seeding...\n")
        
        # ============================================
        # PART 0: ADD DOB AND ADDRESS TO USERS TABLE
        # ============================================
        print("📋 Part 0: User Profile Fields")
        print("-" * 50)
        
        # Check existing columns in users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [col[1] for col in cursor.fetchall()]
        
        # Add dob column if it doesn't exist
        if 'dob' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN dob TEXT")
            print("✅ Added 'dob' (Date of Birth) column to users table")
        else:
            print("✅ 'dob' column already exists in users table")
        
        # Add address column if it doesn't exist
        if 'address' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
            print("✅ Added 'address' column to users table")
        else:
            print("✅ 'address' column already exists in users table")
        
        # ============================================
        # PART 1: PHARMACIST FEATURES
        # ============================================
        print("📋 Part 1: Pharmacist Features")
        print("-" * 50)
        
        # 1. Create activity_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("✅ Activity log table created")
        
        # 2. Add missing fields to prescriptions table
        cursor.execute("PRAGMA table_info(prescriptions)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Add new columns if they are missing
        if 'medicine_id' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN medicine_id INTEGER")
            print("✅ Added medicine_id column to prescriptions")
        
        if 'dosage' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN dosage TEXT")
            print("✅ Added dosage column to prescriptions")
        
        if 'frequency' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN frequency TEXT")
            print("✅ Added frequency column to prescriptions")
        
        if 'duration' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN duration INTEGER")
            print("✅ Added duration column to prescriptions")
        
        if 'doctor_name' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN doctor_name TEXT")
            print("✅ Added doctor_name column to prescriptions")
        
        if 'pharmacist_id' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN pharmacist_id INTEGER")
            print("✅ Added pharmacist_id column to prescriptions")
        
        if 'pharmacist_notes' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN pharmacist_notes TEXT")
            print("✅ Added pharmacist_notes column to prescriptions")
        
        if 'reviewed_date' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN reviewed_date TIMESTAMP")
            print("✅ Added reviewed_date column to prescriptions")
        
        # ============================================
        # PART 2: STAFF/PATIENT FEATURES (ORDERS)
        # ============================================
        print("\n📋 Part 2: Orders & Shopping Features")
        print("-" * 50)
        
        # 3. Create orders table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'Pending',
                    total_amount REAL NOT NULL,
                    payment_method TEXT,
                    payment_status TEXT DEFAULT 'Unpaid',
                    staff_id INTEGER,
                    pharmacy_notes TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    discount_request TEXT,
                    discount_verified INTEGER DEFAULT 0,
                    FOREIGN KEY (patient_id) REFERENCES users(id),
                    FOREIGN KEY (staff_id) REFERENCES users(id)
                )
            """)
            print("✅ Orders table created")
        else:
            print("✅ Orders table already exists")
            # Add new columns for Staff Order Tracking if missing
            cursor.execute("PRAGMA table_info(orders)")
            orders_columns = [col[1] for col in cursor.fetchall()]
            
            if 'staff_id' not in orders_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN staff_id INTEGER")
                print("✅ Added staff_id column to orders")
            
            if 'pharmacy_notes' not in orders_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN pharmacy_notes TEXT")
                print("✅ Added pharmacy_notes column to orders")
            
            if 'updated_at' not in orders_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN updated_at TIMESTAMP")
                # Set default value for existing records
                cursor.execute("UPDATE orders SET updated_at = order_date WHERE updated_at IS NULL")
                print("✅ Added updated_at column to orders")
            
            if 'discount_request' not in orders_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN discount_request TEXT")
                print("✅ Added discount_request column to orders")
            
            if 'discount_verified' not in orders_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN discount_verified INTEGER DEFAULT 0")
                print("✅ Added discount_verified column to orders")
        
        # 4. Create order_items table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order_items'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    medicine_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    pharmacist_approved INTEGER DEFAULT 0,
                    pharmacist_id INTEGER,
                    approval_notes TEXT,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (medicine_id) REFERENCES medicines(id),
                    FOREIGN KEY (pharmacist_id) REFERENCES users(id)
                )
            """)
            print("✅ Order_items table created")
        else:
            print("✅ Order_items table already exists")
            # Add new columns for Pharmacist Approval Tracking if missing
            cursor.execute("PRAGMA table_info(order_items)")
            order_items_columns = [col[1] for col in cursor.fetchall()]
            
            if 'pharmacist_approved' not in order_items_columns:
                cursor.execute("ALTER TABLE order_items ADD COLUMN pharmacist_approved INTEGER DEFAULT 0")
                print("✅ Added pharmacist_approved column to order_items")
            
            if 'pharmacist_id' not in order_items_columns:
                cursor.execute("ALTER TABLE order_items ADD COLUMN pharmacist_id INTEGER")
                print("✅ Added pharmacist_id column to order_items")
            
            if 'approval_notes' not in order_items_columns:
                cursor.execute("ALTER TABLE order_items ADD COLUMN approval_notes TEXT")
                print("✅ Added approval_notes column to order_items")
        
        # ============================================
        # PART 3: BILLING FEATURES (Enhanced)
        # ============================================
        print("\n📋 Part 3: Billing Features")
        print("-" * 50)
        
        # 5. Check if invoices table needs updates
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invoices'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    patient_id INTEGER NOT NULL,
                    order_id INTEGER,
                    subtotal REAL NOT NULL,
                    tax REAL DEFAULT 0,
                    discount REAL DEFAULT 0,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'Unpaid',
                    payment_method TEXT,
                    payment_date TIMESTAMP,
                    billing_clerk_id INTEGER,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES users(id),
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (billing_clerk_id) REFERENCES users(id)
                )
            """)
            print("✅ Invoices table created with full billing features")
        else:
            # Add missing columns to existing invoices table
            cursor.execute("PRAGMA table_info(invoices)")
            invoice_columns = [col[1] for col in cursor.fetchall()]
            
            if 'order_id' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN order_id INTEGER")
                print("✅ Added order_id to invoices")
            
            if 'subtotal' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN subtotal REAL DEFAULT 0")
                print("✅ Added subtotal to invoices")
            
            if 'tax' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN tax REAL DEFAULT 0")
                print("✅ Added tax to invoices")
            
            if 'discount' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN discount REAL DEFAULT 0")
                print("✅ Added discount to invoices")
            
            if 'payment_method' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN payment_method TEXT")
                print("✅ Added payment_method to invoices")
            
            if 'payment_date' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN payment_date TIMESTAMP")
                print("✅ Added payment_date to invoices")
            
            if 'billing_clerk_id' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN billing_clerk_id INTEGER")
                print("✅ Added billing_clerk_id to invoices")
            
            if 'notes' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN notes TEXT")
                print("✅ Added notes to invoices")
        
        # 6. Create payments tracking table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payments'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    transaction_id TEXT,
                    processed_by INTEGER,
                    notes TEXT,
                    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
                    FOREIGN KEY (processed_by) REFERENCES users(id)
                )
            """)
            print("✅ Payments table created")
        else:
            print("✅ Payments table already exists")
        
        # ============================================
        # PART 4: SEEDING MEDICINES (54 Items)
        # ============================================
        print("\n📋 Part 4: Seeding Medicines (54 Items)")
        print("-" * 50)

        # Check if medicines already exist to avoid duplicates
        cursor.execute("SELECT COUNT(*) FROM medicines")
        med_count = cursor.fetchone()[0]

        if med_count > 0:
            print(f"⚠️ Database already contains {med_count} medicines. Skipping seed.")
        else:
            print("💊 Adding 54 medicines with varied stock levels...")
            
            # Format: Name, Category, Price (PHP), Stock, Expiry, Supplier
            meds = [
                # --- PAIN RELIEF (Varied Stock) ---
                ('Biogesic 500mg', 'Pain Relief', 5.00, 500, '2027-12-31', 'Unilab'), # Good
                ('Alaxan FR', 'Pain Relief', 11.00, 5, '2026-05-20', 'Unilab'),       # Low Stock
                ('Advil 200mg', 'Pain Relief', 13.50, 0, '2025-11-15', 'Pfizer'),     # Out of Stock
                ('RiteMED Paracetamol 500mg', 'Pain Relief', 3.50, 1000, '2027-01-01', 'RiteMED'),
                ('Medicol Advance 400mg', 'Pain Relief', 8.50, 8, '2026-08-10', 'Unilab'), # Low Stock
                ('Dolfenal 500mg', 'Pain Relief', 16.00, 150, '2025-12-05', 'Unilab'),
                ('Ponstan 500mg', 'Pain Relief', 29.00, 100, '2026-03-30', 'Pfizer'),
                ('Flanax 275mg', 'Pain Relief', 19.00, 0, '2026-07-22', 'Bayer'),     # Out of Stock
                ('Tempra Forte Tablet', 'Pain Relief', 6.50, 400, '2026-09-15', 'Taisho'),
                ('Calpol 500mg Tablet', 'Pain Relief', 7.00, 3, '2026-10-01', 'GSK'), # Low Stock
                ('Rexidol 500mg', 'Pain Relief', 5.00, 200, '2026-02-14', 'Unilab'),
                ('Saridon', 'Pain Relief', 6.00, 150, '2026-06-20', 'Bayer'),

                # --- COUGH & COLD (Varied Stock) ---
                ('Neozep Forte', 'Cough & Cold', 6.00, 600, '2026-02-28', 'Unilab'),
                ('Bioflu', 'Cough & Cold', 8.00, 500, '2026-04-15', 'Unilab'),
                ('Solmux 500mg', 'Cough & Cold', 13.00, 9, '2025-12-12', 'Unilab'),   # Low Stock
                ('Decolgen Forte', 'Cough & Cold', 7.50, 400, '2026-01-20', 'Unilab'),
                ('Tuseran Forte', 'Cough & Cold', 10.00, 0, '2026-06-30', 'Unilab'),  # Out of Stock
                ('Robitussin Capsule', 'Cough & Cold', 18.00, 150, '2025-10-10', 'Pfizer'),
                ('Ascof Lagundi 600mg', 'Cough & Cold', 12.00, 200, '2026-03-15', 'Pascual Lab'),
                ('Symdex-D', 'Cough & Cold', 6.00, 500, '2026-11-20', 'Unilab'),
                ('Sinutab High Potency', 'Cough & Cold', 11.50, 150, '2025-09-05', 'J&J'),
                ('RiteMED Ambroxol', 'Cough & Cold', 4.50, 4, '2027-02-14', 'RiteMED'), # Low Stock
                ('Allerkapt (Cetirizine)', 'Cough & Cold', 15.00, 200, '2026-08-20', 'Unilab'),
                ('Virlix 10mg', 'Cough & Cold', 35.00, 100, '2026-09-30', 'GSK'),

                # --- ANTIBIOTICS (Mostly Good Stock) ---
                ('Amoxil 500mg', 'Antibiotics', 28.00, 100, '2025-08-30', 'GSK'),
                ('Augmentin 625mg', 'Antibiotics', 85.00, 50, '2025-07-15', 'GSK'),
                ('RiteMED Amoxicillin', 'Antibiotics', 9.00, 500, '2026-05-01', 'RiteMED'),
                ('Zithromax (Azithromycin)', 'Antibiotics', 120.00, 2, '2025-12-31', 'Pfizer'), # Low Stock
                ('RiteMED Cephalexin', 'Antibiotics', 18.00, 200, '2026-01-10', 'RiteMED'),
                ('Ciprobay 500mg', 'Antibiotics', 65.00, 150, '2026-04-20', 'Bayer'),
                
                # --- MAINTENANCE (Varied) ---
                ('Norvasc 5mg', 'Maintenance', 33.00, 200, '2026-11-11', 'Pfizer'),
                ('Lipitor 10mg', 'Maintenance', 45.00, 0, '2026-10-25', 'Pfizer'),    # Out of Stock
                ('RiteMED Losartan 50mg', 'Maintenance', 12.00, 500, '2027-01-05', 'RiteMED'),
                ('RiteMED Amlodipine 10mg', 'Maintenance', 9.00, 600, '2027-03-15', 'RiteMED'),
                ('Glucophage 500mg', 'Diabetes', 19.50, 300, '2026-02-20', 'Merck'),
                ('RiteMED Metformin 500mg', 'Diabetes', 6.00, 7, '2027-05-10', 'RiteMED'), # Low Stock
                ('Euglucon 5mg', 'Diabetes', 18.00, 400, '2026-09-09', 'Pfizer'),
                ('Plavix 75mg', 'Heart Health', 90.00, 50, '2025-12-01', 'Sanofi'),

                # --- VITAMINS (Varied) ---
                ('Enervon C', 'Vitamins', 8.00, 500, '2027-01-01', 'Unilab'),
                ('Centrum Advance', 'Vitamins', 14.00, 200, '2026-08-15', 'Pfizer'),
                ('Poten-Cee 500mg', 'Vitamins', 7.50, 0, '2026-12-10', 'Pascual Lab'), # Out of Stock
                ('Stresstabs', 'Vitamins', 12.00, 150, '2026-05-30', 'Pfizer'),
                ('Myra E 400IU', 'Vitamins', 15.00, 200, '2026-02-14', 'Unilab'),
                ('Fern-C', 'Vitamins', 9.00, 5, '2026-07-20', 'Fern'), # Low Stock
                ('Immunpro', 'Vitamins', 17.00, 100, '2026-04-05', 'Unilab'),
                ('Neurogen-E', 'Vitamins', 24.00, 150, '2026-06-15', 'Unilab'),

                # --- GASTRO (Varied) ---
                ('Kremil-S', 'Antacid', 6.00, 500, '2027-02-28', 'Unilab'),
                ('Gaviscon Double Action', 'Antacid', 32.00, 6, '2026-01-20', 'Reckitt'), # Low Stock
                ('Imodium 2mg', 'Antidiarrheal', 22.00, 200, '2026-11-30', 'J&J'),
                ('Diatabs', 'Antidiarrheal', 9.00, 300, '2027-03-10', 'Unilab'),
                ('Buscopan 10mg', 'Antispasmodic', 25.00, 150, '2026-08-05', 'Sanofi'),
                ('Erceflora 2B', 'Probiotics', 55.00, 0, '2025-10-15', 'Sanofi'),      # Out of Stock
                ('RiteMED Omeprazole 20mg', 'Antacid', 15.00, 400, '2026-12-05', 'RiteMED'),
                ('Motilium 10mg', 'Antinausea', 35.00, 50, '2025-09-20', 'J&J'),
            ]
            
            # Insert into database
            cursor.executemany("""
                INSERT INTO medicines (name, category, price, stock, expiry_date, supplier) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, meds)
            
            print("✅ Success! 54 Medicines added.")

        # ============================================
        # PART 5: DATABASE INDEXES (Performance)
        # ============================================
        print("\n📋 Part 5: Database Indexes")
        print("-" * 50)
        
        # Activity log indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp)")
        
        # Prescription indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prescriptions_status ON prescriptions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id)")
        
        # Order indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_patient ON orders(patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)")
        
        # Billing indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_patient ON invoices(patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices(invoice_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_id)")
        
        print("✅ All database indexes created")

        # ============================================
        # PART 6: SAMPLE TRANSACTIONS (Prescriptions/Orders)
        # ============================================
        print("\n📋 Part 6: Sample Transactions")
        print("-" * 50)
        
        # Add sample prescriptions if they don't exist
        cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE medicine_id IS NOT NULL")
        if cursor.fetchone()[0] == 0:
            print("📝 Adding sample prescriptions...")
            
            # Get patient ID
            cursor.execute("SELECT id FROM users WHERE username = 'pat'")
            patient = cursor.fetchone()
            patient_id = patient[0] if patient else 1
            
            # Get some medicine IDs
            cursor.execute("SELECT id FROM medicines LIMIT 4")
            medicine_ids = [row[0] for row in cursor.fetchall()]
            
            if medicine_ids:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Format: patient_id, medicine_id, status, dosage, frequency, duration, doctor_name, notes, created_at
                sample_prescriptions = [
                    (patient_id, medicine_ids[0], 'Pending', '500mg', '3 times daily', 7, 'Dr. Smith', 'Patient has penicillin allergy', now),
                    (patient_id, medicine_ids[1] if len(medicine_ids) > 1 else medicine_ids[0], 'Pending', '250mg', '2 times daily', 5, 'Dr. Johnson', 'Take with food', now),
                    (patient_id, medicine_ids[2] if len(medicine_ids) > 2 else medicine_ids[0], 'Approved', '400mg', 'Every 8 hours', 10, 'Dr. Williams', 'Approved for dispensing', now),
                    (patient_id, medicine_ids[3] if len(medicine_ids) > 3 else medicine_ids[0], 'Pending', '10mg', 'Once daily', 14, 'Dr. Brown', 'Monitor for side effects', now),
                ]
                
                cursor.executemany("""
                    INSERT INTO prescriptions 
                    (patient_id, medicine_id, status, dosage, frequency, duration, doctor_name, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, sample_prescriptions)
                print(f"✅ Added {len(sample_prescriptions)} sample prescriptions")
        else:
            print("✅ Prescriptions table already has data")
        
        # Add sample orders if they don't exist
        cursor.execute("SELECT COUNT(*) FROM orders")
        if cursor.fetchone()[0] == 0:
            print("📝 Adding sample orders...")
            
            cursor.execute("SELECT id FROM users WHERE username = 'pat'")
            patient = cursor.fetchone()
            patient_id = patient[0] if patient else 1
            
            cursor.execute("SELECT id, price FROM medicines LIMIT 3")
            medicines = cursor.fetchall()
            
            if medicines:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Create sample order header
                cursor.execute("""
                    INSERT INTO orders (patient_id, order_date, status, total_amount, payment_method, payment_status, notes)
                    VALUES (?, ?, 'Completed', 150.00, 'Cash', 'Paid', 'Sample order')
                """, (patient_id, now))
                
                order_id = cursor.lastrowid
                
                # Add order items (2 items from the first 2 medicines found)
                for med in medicines[:2]:
                    cursor.execute("""
                        INSERT INTO order_items (order_id, medicine_id, quantity, unit_price, subtotal)
                        VALUES (?, ?, 2, ?, ?)
                    """, (order_id, med[0], med[1], med[1] * 2))
                
                print("✅ Added 1 sample order with 2 items")
        else:
            print("✅ Orders table already has data")
        
        # ============================================
        # PART 7: ENHANCED SAMPLE DATA FOR PRESENTATION
        # ============================================
        print("\n📋 Part 7: Enhanced Sample Data for Presentation")
        print("-" * 50)
        
        # Get user IDs for different roles
        cursor.execute("SELECT id, role FROM users")
        users = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Get patient ID
        cursor.execute("SELECT id FROM users WHERE username = 'pat' OR role = 'Patient' LIMIT 1")
        patient_result = cursor.fetchone()
        patient_id = patient_result[0] if patient_result else users.get('Patient', 1)
        
        # Get pharmacist ID
        pharmacist_id = users.get('Pharmacist', users.get('Admin', 1))
        
        # Get billing clerk ID
        billing_clerk_id = users.get('Admin', 1)
        
        # 7.1: Add Activity Log Entries
        cursor.execute("SELECT COUNT(*) FROM activity_log")
        if cursor.fetchone()[0] < 5:
            print("📝 Adding activity log entries...")
            
            now = datetime.now()
            activities = [
                (pharmacist_id, 'Prescription Review', 'Reviewed and approved prescription #3 for Biogesic', 
                 (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")),
                (pharmacist_id, 'Stock Alert', 'Low stock alert for Alaxan FR (5 units remaining)', 
                 (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")),
                (patient_id, 'Order Placed', 'Placed order #1 for 2 medicine items', 
                 (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")),
                (billing_clerk_id, 'Invoice Generated', 'Generated invoice INV-001 for ₱150.00', 
                 (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")),
                (billing_clerk_id, 'Payment Received', 'Received cash payment for invoice INV-001', 
                 (now - timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")),
                (pharmacist_id, 'Medicine Dispensed', 'Dispensed prescription #3 to patient', 
                 (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")),
                (pharmacist_id, 'Stock Update', 'Updated stock for 3 medicines after dispensing', 
                 (now - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S")),
            ]
            
            cursor.executemany("""
                INSERT INTO activity_log (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            """, activities)
            print(f"✅ Added {len(activities)} activity log entries")
        else:
            print("✅ Activity log already has sufficient data")
        
        # 7.2: Add More Diverse Prescriptions
        cursor.execute("SELECT COUNT(*) FROM prescriptions")
        if cursor.fetchone()[0] < 8:
            print("📝 Adding diverse prescription samples...")
            
            cursor.execute("SELECT id, name FROM medicines WHERE stock > 10 LIMIT 10")
            available_meds = cursor.fetchall()
            
            if available_meds:
                now = datetime.now()
                doctors = ['Dr. Smith', 'Dr. Johnson', 'Dr. Williams', 'Dr. Brown', 'Dr. Garcia', 'Dr. Martinez']
                statuses = ['Pending', 'Approved', 'Rejected', 'Completed']
                
                prescriptions = [
                    # Pending prescriptions (need review)
                    (patient_id, available_meds[0][0], 'Pending', '500mg', 'Twice daily', 7, 
                     random.choice(doctors), 'Take after meals', 
                     (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")),
                    (patient_id, available_meds[1][0] if len(available_meds) > 1 else available_meds[0][0], 
                     'Pending', '10mg', 'Once daily at bedtime', 30, 
                     random.choice(doctors), 'For hypertension maintenance', 
                     (now - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")),
                    
                    # Approved prescriptions (ready to dispense)
                    (patient_id, available_meds[2][0] if len(available_meds) > 2 else available_meds[0][0], 
                     'Approved', '250mg', 'Three times daily', 5, 
                     random.choice(doctors), 'Approved by pharmacist - ready for pickup', 
                     (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
                    
                    # Completed prescriptions
                    (patient_id, available_meds[3][0] if len(available_meds) > 3 else available_meds[0][0], 
                     'Completed', '400mg', 'Every 6 hours as needed', 3, 
                     random.choice(doctors), 'Dispensed and completed', 
                     (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")),
                ]
                
                cursor.executemany("""
                    INSERT INTO prescriptions 
                    (patient_id, medicine_id, status, dosage, frequency, duration, doctor_name, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, prescriptions)
                print(f"✅ Added {len(prescriptions)} diverse prescriptions")
        else:
            print("✅ Prescriptions already have sufficient variety")
        
        # 7.3: Add Multiple Orders with Different Statuses
        cursor.execute("SELECT COUNT(*) FROM orders")
        if cursor.fetchone()[0] < 5:
            print("📝 Adding multiple orders with various statuses...")
            
            cursor.execute("SELECT id, price FROM medicines WHERE stock > 0 LIMIT 8")
            available_meds = cursor.fetchall()
            
            if available_meds:
                now = datetime.now()
                
                # Order 1: Pending order (just placed)
                cursor.execute("""
                    INSERT INTO orders (patient_id, order_date, status, total_amount, payment_method, payment_status, notes)
                    VALUES (?, ?, 'Pending', 85.50, NULL, 'Unpaid', 'Awaiting processing')
                """, (patient_id, (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")))
                order1_id = cursor.lastrowid
                
                # Items for pending order
                cursor.execute("""
                    INSERT INTO order_items (order_id, medicine_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, 3, ?, ?)
                """, (order1_id, available_meds[0][0], available_meds[0][1], available_meds[0][1] * 3))
                cursor.execute("""
                    INSERT INTO order_items (order_id, medicine_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, 2, ?, ?)
                """, (order1_id, available_meds[1][0], available_meds[1][1], available_meds[1][1] * 2))
                
                # Order 2: Processing order
                cursor.execute("""
                    INSERT INTO orders (patient_id, order_date, status, total_amount, payment_method, payment_status, notes)
                    VALUES (?, ?, 'Processing', 245.00, 'GCash', 'Paid', 'Being prepared for pickup')
                """, (patient_id, (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")))
                order2_id = cursor.lastrowid
                
                # Items for processing order
                cursor.execute("""
                    INSERT INTO order_items (order_id, medicine_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, 5, ?, ?)
                """, (order2_id, available_meds[2][0], available_meds[2][1], available_meds[2][1] * 5))
                
                # Order 3: Completed order (yesterday)
                cursor.execute("""
                    INSERT INTO orders (patient_id, order_date, status, total_amount, payment_method, payment_status, notes)
                    VALUES (?, ?, 'Completed', 420.00, 'Cash', 'Paid', 'Picked up by patient')
                """, (patient_id, (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")))
                order3_id = cursor.lastrowid
                
                # Items for completed order
                cursor.execute("""
                    INSERT INTO order_items (order_id, medicine_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, 4, ?, ?)
                """, (order3_id, available_meds[3][0], available_meds[3][1], available_meds[3][1] * 4))
                cursor.execute("""
                    INSERT INTO order_items (order_id, medicine_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, 6, ?, ?)
                """, (order3_id, available_meds[4][0], available_meds[4][1], available_meds[4][1] * 6))
                
                # Order 4: Cancelled order
                cursor.execute("""
                    INSERT INTO orders (patient_id, order_date, status, total_amount, payment_method, payment_status, notes)
                    VALUES (?, ?, 'Cancelled', 155.00, NULL, 'Unpaid', 'Cancelled by patient')
                """, (patient_id, (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")))
                order4_id = cursor.lastrowid
                
                # Items for cancelled order
                cursor.execute("""
                    INSERT INTO order_items (order_id, medicine_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, 2, ?, ?)
                """, (order4_id, available_meds[5][0], available_meds[5][1], available_meds[5][1] * 2))
                
                print("✅ Added 4 orders with different statuses")
        else:
            print("✅ Orders already have sufficient variety")
        
        # 7.4: Add Sample Invoices with Different Payment Statuses
        cursor.execute("SELECT COUNT(*) FROM invoices")
        if cursor.fetchone()[0] < 4:
            print("📝 Adding sample invoices with various payment statuses...")
            
            # Get completed orders for invoice generation
            cursor.execute("SELECT id, patient_id, total_amount FROM orders WHERE status IN ('Completed', 'Processing') LIMIT 3")
            completed_orders = cursor.fetchall()
            
            now = datetime.now()
            invoice_counter = 1001
            
            for order in completed_orders:
                order_id, order_patient_id, total = order
                invoice_number = f'INV-{invoice_counter}'
                
                # Check if this invoice already exists
                cursor.execute("SELECT id FROM invoices WHERE invoice_number = ?", (invoice_number,))
                if cursor.fetchone():
                    invoice_counter += 1
                    continue  # Skip if already exists
                
                # Calculate invoice details
                subtotal = total
                tax = round(subtotal * 0.12, 2)  # 12% VAT
                discount = 0 if invoice_counter > 1001 else round(subtotal * 0.10, 2)  # 10% discount for first invoice
                final_total = round(subtotal + tax - discount, 2)
                
                # Determine payment status
                if invoice_counter == 1001:
                    status = 'Paid'
                    payment_date = (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
                    payment_method = 'Cash'
                elif invoice_counter == 1002:
                    status = 'Partially Paid'
                    payment_date = (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
                    payment_method = 'GCash'
                else:
                    status = 'Unpaid'
                    payment_date = None
                    payment_method = None
                
                cursor.execute("""
                    INSERT INTO invoices 
                    (invoice_number, patient_id, order_id, subtotal, tax, discount, total_amount, 
                     status, payment_method, payment_date, billing_clerk_id, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    invoice_number, 
                    order_patient_id, 
                    order_id, 
                    subtotal, 
                    tax, 
                    discount, 
                    final_total,
                    status, 
                    payment_method, 
                    payment_date, 
                    billing_clerk_id,
                    f'Generated for order #{order_id}',
                    (now - timedelta(days=(3-invoice_counter+1000))).strftime("%Y-%m-%d %H:%M:%S")
                ))
                
                invoice_id = cursor.lastrowid
                
                # Add payment record if paid
                if status in ['Paid', 'Partially Paid']:
                    payment_amount = final_total if status == 'Paid' else round(final_total * 0.5, 2)
                    cursor.execute("""
                        INSERT INTO payments 
                        (invoice_id, amount, payment_method, payment_date, processed_by, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        invoice_id, 
                        payment_amount, 
                        payment_method, 
                        payment_date, 
                        billing_clerk_id,
                        f'{status} via {payment_method}'
                    ))
                
                invoice_counter += 1  # Increment after successful insert
            
            print(f"✅ Added {len(completed_orders)} invoices with payment records")
        else:
            print("✅ Invoices already have sufficient data")
        
        # 7.5: Add Low Stock Alerts Activity
        print("📝 Adding low stock alerts to activity log...")
        cursor.execute("""
            SELECT name, stock FROM medicines 
            WHERE stock < 10 AND stock > 0
        """)
        low_stock_meds = cursor.fetchall()
        
        if low_stock_meds:
            now = datetime.now()
            for med_name, stock_count in low_stock_meds[:5]:  # Add alerts for first 5 low stock items
                cursor.execute("""
                    INSERT INTO activity_log (user_id, action, details, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (
                    pharmacist_id,
                    'Stock Alert',
                    f'⚠️ Low stock alert: {med_name} has only {stock_count} units remaining',
                    (now - timedelta(hours=random.randint(1, 48))).strftime("%Y-%m-%d %H:%M:%S")
                ))
            print(f"✅ Added {len(low_stock_meds[:5])} low stock alerts")
        
        # 7.6: Add Out of Stock Alerts
        cursor.execute("""
            SELECT name FROM medicines WHERE stock = 0
        """)
        out_of_stock_meds = cursor.fetchall()
        
        if out_of_stock_meds:
            now = datetime.now()
            for (med_name,) in out_of_stock_meds[:3]:  # Add alerts for first 3 out of stock items
                cursor.execute("""
                    INSERT INTO activity_log (user_id, action, details, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (
                    pharmacist_id,
                    'Stock Critical',
                    f'🚨 OUT OF STOCK: {med_name} needs immediate restocking',
                    (now - timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M:%S")
                ))
            print(f"✅ Added {len(out_of_stock_meds[:3])} out of stock alerts")
        
        # ============================================
        # FINAL COMMIT
        # ============================================
        conn.commit()
        print("\n" + "=" * 50)
        print("✅ MIGRATION & SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("\n💡 All user roles now have DOB and Address fields!")
        print("   You can now update profiles for all roles.\n")
        print("\n📊 Database Summary:")
        
        # Count statistics
        cursor.execute("SELECT COUNT(*) FROM medicines")
        med_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock < 10")
        low_stock_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock = 0")
        out_stock_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM prescriptions")
        rx_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoice_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM activity_log")
        activity_count = cursor.fetchone()[0]
        
        print(f"  💊 Medicines: {med_count} total")
        print(f"     ⚠️  Low Stock: {low_stock_count}")
        print(f"     🚨 Out of Stock: {out_stock_count}")
        print(f"  📋 Prescriptions: {rx_count}")
        print(f"  🛒 Orders: {order_count}")
        print(f"  🧾 Invoices: {invoice_count}")
        print(f"  📝 Activity Logs: {activity_count}")
        print("\n🎉 Your database is ready for presentation!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 70)
    print("  PHARMACY MANAGEMENT SYSTEM - DATABASE MIGRATION & SEEDING")
    print("=" * 70)
    print("\n⚠️  WARNING: This will modify your existing database!")
    print("    Make sure you have a backup if needed.\n")
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response == 'yes':
        run_migration_and_seed()
    else:
        print("❌ Migration cancelled.")        




