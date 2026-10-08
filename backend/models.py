from pydantic import BaseModel, Field

class ProductCard(BaseModel):
    product_id: str
    name: str
    price: float
    garment_type: str
    description: str
    image_file_path: str
    available_sizes: list[str] = Field(default_factory=list)

class ProductInfo(ProductCard):
    stock_by_size: dict[str, int] = Field(default_factory=dict)

class StockLookup(BaseModel):
    product_id: str
    size: str
    stock_quantity: int

class OrderStatus(BaseModel):
    order_id: str
    status: str
    carrier: str | None = None
    tracking_number: str | None = None
    estimated_delivery: str | None = None
    found: bool = True

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[dict[str, str]] = Field(default_factory=list, max_length=20)
    user_id: int | None = None
    page_context: ProductCard | None = None

class ChatReply(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)

class AgentDependencies(BaseModel):
    user_id: int | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    page_context: ProductCard | None = None
