from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pyodbc
import os

app = FastAPI()

# --- AZURE SQL CONNECTION ---
# Using the credentials you provided
DB_SERVER = 'simpliadmin-renz-gab.database.windows.net'
DB_NAME = 'SimpliShopDB'
DB_USER = 'simpliadmin'
DB_PASS = 'Simpli12345678'
DB_DRIVER = '{ODBC Driver 18 for SQL Server}'

connection_string = f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASS};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

def get_db_conn():
    return pyodbc.connect(connection_string)

# Create table if not exists
try:
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
        BEGIN
            CREATE TABLE Users (
                id INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(100),
                email NVARCHAR(100) UNIQUE,
                password NVARCHAR(100)
            )
        END
    """)
    conn.commit()
    conn.close()
    print("Database connection successful and table verified!")
except Exception as e:
    print(f"Database Error: {e}")

# --- DATA MODELS ---
class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# --- API ENDPOINTS ---

@app.post("/api/signup")
async def signup(user: UserSignup):
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (name, email, password) VALUES (?, ?, ?)", 
                       (user.name, user.email, user.password))
        conn.commit()
        conn.close()
        return {"message": "User created successfully"}
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
async def login(user: UserLogin):
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Users WHERE email = ? AND password = ?", (user.email, user.password))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"name": row[0]}
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- SERVE STATIC FILES ---
# This must be LAST so it doesn't override the API routes
app.mount("/", StaticFiles(directory=".", html=True), name="static")
