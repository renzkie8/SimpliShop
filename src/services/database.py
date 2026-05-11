import sqlite3
import os

# Resolve absolute path for database persistence
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'storage')

# Verify persistence directory exists
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

DB_FILE = os.path.join(DB_PATH, "pharmacy.db")

# Initialize SQLite database connection
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Execute database schema migration
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Schema: Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            dob TEXT,
            address TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Legacy schema migration for status column
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'Pending'")
    except sqlite3.OperationalError:
        pass # Column already defined

    # Schema: Medicines
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER,
            expiry_date TEXT,
            supplier TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Schema: Prescriptions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            image_path TEXT,
            status TEXT DEFAULT 'Pending',
            notes TEXT,
            medicine_id INTEGER,
            dosage TEXT,
            frequency TEXT,
            duration INTEGER,
            doctor_name TEXT,
            pharmacist_id INTEGER,
            pharmacist_notes TEXT,
            reviewed_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id)
        )
    ''')

    # Schema: Invoices
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            patient_id INTEGER NOT NULL,
            order_id INTEGER,
            subtotal REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Unpaid',
            payment_method TEXT,
            payment_date TIMESTAMP,
            billing_clerk_id INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id)
        )
    ''')

    # Provision default system accounts
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        users = [
            ('admin', 'admin123', 'Admin', 'System Admin', '', 'Approved'),
            ('pharm', 'pharm123', 'Pharmacist', 'Carl Renz', 'Colico', 'Approved'),
            ('inv', 'inv123', 'Inventory', 'Kenji Nathaniel', 'David', 'Approved'),
            ('bill', 'bill123', 'Billing', 'Francis Gabriel', 'Nonato', 'Approved'),
            ('staff', 'staff123', 'Staff', 'Staff Member', '', 'Approved'),
            ('pat', 'pat123', 'Patient', 'John', 'Doe', 'Approved')
        ]
        cursor.executemany("""
            INSERT INTO users (username, password, role, full_name, last_name, status) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, users)

    # Automatically approve provisioned system accounts
    cursor.execute("UPDATE users SET status = 'Approved' WHERE status IS NULL OR status = 'Pending' AND username IN ('admin', 'pharm', 'inv', 'bill', 'staff', 'pat')")

    conn.commit()
    conn.close()

# Authenticate user credentials
def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user




