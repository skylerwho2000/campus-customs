from pathlib import Path
import json
import hashlib
import hmac
import secrets
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
try:
    from .agent import run_chat
    from .models import ChatRequest, ChatReply
    from .audit import audit_event
except ImportError:
    from agent import run_chat
    from models import ChatRequest, ChatReply
    from audit import audit_event

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "campus_customs.db"
PRODUCTS = ROOT / "data" / "products"
app = FastAPI(title="Campus Customs API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"] , allow_headers=["*"])
HASH_ITERATIONS = 600_000

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

class CreateAccountRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), HASH_ITERATIONS).hex()
    return f"pbkdf2_sha256${HASH_ITERATIONS}${salt}${digest}"

def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt, expected = stored.split("$")
        if algorithm != "pbkdf2_sha256": return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations)).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def public_user(row):
    return {"id": row["id"], "first_name": row["first_name"], "last_name": row["last_name"], "name": row["name"], "email": row["email"]}

def product(row, inventory=None):
    item = dict(row)
    for field in ("colors", "search_tags"):
        try: item[field] = json.loads(item[field])
        except (TypeError, json.JSONDecodeError): item[field] = []
    if inventory is not None: item["inventory"] = inventory
    return item

@app.get("/api/health")
def health(): return {"status": "ok"}

@app.post("/chat", response_model=ChatReply)
async def chat(payload: ChatRequest):
    try:
        audit_event("agent_loop", {"message": payload.message, "user_id": payload.user_id}, None, "started")
        customer_name = customer_email = None
        history = payload.history
        with connect() as con:
            user = con.execute("SELECT id, name, first_name, email FROM users WHERE id = ?", (payload.user_id,)).fetchone() if payload.user_id else None
            if payload.user_id and not user:
                raise HTTPException(401, "Please log in again")
            if user:
                customer_name = user["name"] or f"{user['first_name']}"
                customer_email = user["email"]
                stored = con.execute("SELECT role, content FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 20", (payload.user_id,)).fetchall()
                history = [{"role": row["role"], "content": row["content"]} for row in reversed(stored)]
        reply = await run_chat(payload.message, history, payload.user_id, customer_name, customer_email, payload.page_context)
        if payload.user_id:
            with connect() as con:
                con.executemany("INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)", [(payload.user_id, "user", payload.message, None), (payload.user_id, "assistant", reply.reply, json.dumps([item.model_dump() for item in reply.products]))])
                con.commit()
        audit_event("agent_loop", {"user_id": payload.user_id}, {"products": len(reply.products)}, "completed")
        return reply
    except HTTPException:
        raise
    except RuntimeError as exc:
        audit_event("agent_loop", {}, str(exc), "runtime_error")
        raise HTTPException(503, str(exc))
    except Exception as exc:
        audit_event("agent_loop", {}, str(exc), "error")
        raise HTTPException(502, f"The shop assistant is temporarily unavailable: {exc}")

@app.get("/api/chat/history/{user_id}")
def chat_history(user_id: int):
    with connect() as con:
        rows = con.execute("SELECT role, content FROM chat_messages WHERE user_id = ? ORDER BY created_at, id", (user_id,)).fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in rows]

@app.post("/api/auth/register")
def register(payload: CreateAccountRequest):
    email = str(payload.email).lower()
    with connect() as con:
        if con.execute("SELECT 1 FROM users WHERE lower(email) = ?", (email,)).fetchone():
            raise HTTPException(409, "An account with that email already exists")
        cursor = con.execute("INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)", (f"{payload.first_name} {payload.last_name}", email, hash_password(payload.password), payload.first_name, payload.last_name))
        con.commit()
        row = con.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return {"message": "Account created", "user": public_user(row)}

@app.post("/api/auth/login")
def login(payload: LoginRequest):
    with connect() as con:
        row = con.execute("SELECT * FROM users WHERE lower(email) = ?", (str(payload.email).lower(),)).fetchone()
        if not row or not verify_password(payload.password, row["password_hash"]):
            raise HTTPException(401, "Invalid email or password")
        return {"message": "Logged in", "user": public_user(row)}

@app.get("/api/products")
def products():
    with connect() as con:
        rows = con.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        return [product(row) for row in rows]

@app.get("/api/products/{product_id}")
def product_detail(product_id: str):
    with connect() as con:
        row = con.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if not row: raise HTTPException(404, "Product not found")
        stock = con.execute("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id", (product_id,)).fetchall()
        return product(row, [dict(x) for x in stock])

@app.get("/media/{path:path}")
def media(path: str):
    target = (ROOT / "data" / path).resolve()
    if PRODUCTS not in target.parents or not target.is_file(): raise HTTPException(404, "Image not found")
    return FileResponse(target)
