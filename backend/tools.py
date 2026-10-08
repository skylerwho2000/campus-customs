import json
import sqlite3
from pathlib import Path
from pydantic_ai import RunContext
try:
    from .models import AgentDependencies, ProductCard, ProductInfo, StockLookup, OrderStatus
    from .audit import audit_event
except ImportError:
    from models import AgentDependencies, ProductCard, ProductInfo, StockLookup, OrderStatus
    from audit import audit_event

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "campus_customs.db"

def _connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def _card(row, sizes=None) -> ProductCard:
    return ProductCard(product_id=row["product_id"], name=row["name"], price=row["price"], garment_type=row["garment_type"], description=row["description"], image_file_path=row["image_file_path"], available_sizes=sizes or [])

def register_tools(agent):
    @agent.tool
    def search_products(ctx: RunContext[AgentDependencies], query: str) -> list[ProductCard]:
        """Search the Campus Customs catalogue by product name, garment type, description, color, or tag."""
        terms = [term for term in query.lower().split() if len(term) > 1]
        with _connect() as con:
            rows = con.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
            matches = []
            for row in rows:
                haystack = " ".join([row["name"], row["garment_type"], row["description"], row["colors"], row["search_tags"]]).lower()
                if not terms or any(term in haystack for term in terms): matches.append(_card(row))
            result = matches[:8]
            audit_event("search_products", {"query": query}, f"{len(result)} matches")
            return result

    @agent.tool
    def get_stock_level(ctx: RunContext[AgentDependencies], product_id: str, size: str) -> StockLookup:
        """Look up the real inventory quantity for one product and one requested size."""
        with _connect() as con:
            row = con.execute("SELECT size, quantity FROM inventory WHERE product_id = ? AND lower(size) = lower(?)", (product_id, size)).fetchone()
            result = StockLookup(product_id=product_id, size=size, stock_quantity=row["quantity"] if row else 0)
            audit_event("get_stock_level", {"product_id": product_id, "size": size}, result.model_dump())
            return result

    @agent.tool
    def get_order_status(ctx: RunContext[AgentDependencies], order_id: str) -> OrderStatus:
        """Look up a demonstration order's shipping status by order ID. Never invent a status for an unknown ID."""
        demo_orders = {
            "CC-1001": OrderStatus(order_id="CC-1001", status="In transit", carrier="USPS", tracking_number="9400111899223856921001", estimated_delivery="2026-10-10"),
            "CC-1002": OrderStatus(order_id="CC-1002", status="Delivered", carrier="UPS", tracking_number="1Z999AA10123456784", estimated_delivery="2026-10-04"),
        }
        result = demo_orders.get(order_id.upper(), OrderStatus(order_id=order_id, status="Not found", found=False))
        audit_event("get_order_status", {"order_id": order_id}, result.model_dump())
        return result

    @agent.tool
    def get_product_info(ctx: RunContext[AgentDependencies], product_id: str) -> ProductInfo | None:
        """Fetch one real product's description, price, and complete stock by size from the database."""
        with _connect() as con:
            row = con.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
            if not row:
                return None
            stock = con.execute("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id", (product_id,)).fetchall()
            quantities = {item["size"]: item["quantity"] for item in stock}
            result = ProductInfo(product_id=row["product_id"], name=row["name"], price=row["price"], garment_type=row["garment_type"], description=row["description"], image_file_path=row["image_file_path"], available_sizes=[size for size, quantity in quantities.items() if quantity > 0], stock_by_size=quantities)
            audit_event("get_product_info", {"product_id": product_id}, {"price": result.price, "sizes": list(result.stock_by_size)})
            return result

    return agent
