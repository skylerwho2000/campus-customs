# Campus Customs Chatbot Harness

This document records the database contract that the shop and chatbot can rely on. The schema was inspected from `data/campus_customs.db`.

## `catalogue` — 102 rows

| Field | Type | Why it matters |
|---|---|---|
| `product_id` | TEXT, primary key | Stable product identifier for joins, links, and chatbot recommendations. |
| `name` | TEXT, required | Human-readable product name shown to shoppers. |
| `garment_type` | TEXT, required | Supports searches and filters such as hoodies, T-shirts, and crewnecks. |
| `description` | TEXT, required | Gives the chatbot factual product details to explain to customers. |
| `colors` | TEXT, required | Stores the product color options, serialized as JSON text for color filtering and answers. |
| `search_tags` | TEXT, required | Provides keywords for matching natural-language customer requests to products. |
| `image_file_path` | TEXT, required | Connects a catalogue item to its product image for the shop UI. |
| `price` | REAL, required | Supplies the current displayed price and supports price-range searches. |

## `inventory` — 612 rows

| Field | Type | Why it matters |
|---|---|---|
| `id` | INTEGER, primary key | Uniquely identifies one inventory record. |
| `product_id` | TEXT, required | Links stock to the matching product in `catalogue`. |
| `size` | TEXT, required | Lets the chatbot answer whether a requested size is available. |
| `quantity` | INTEGER, required | Prevents the shop and chatbot from claiming unavailable stock. |

## `users` — 3 rows

| Field | Type | Why it matters |
|---|---|---|
| `id` | INTEGER, primary key | Identifies an account and links it to user activity. |
| `name` | TEXT, required | Provides a display name for account-facing experiences. |
| `email` | TEXT, required | Supports login, account identification, and customer communication. |
| `password_hash` | TEXT, required | Stores a password verifier for authentication; the chatbot must never expose it. |
| `created_at` | TEXT, required | Records when the account was created for account history and support. |
| `first_name` | TEXT, optional | Enables personalized greetings without parsing the full name. |
| `last_name` | TEXT, optional | Supports personalization and account administration. |

## `chat_messages` — 22 rows

| Field | Type | Why it matters |
|---|---|---|
| `id` | INTEGER, primary key | Identifies each message in the conversation history. |
| `user_id` | INTEGER, required | Associates a message with the account that owns the conversation. |
| `role` | TEXT, required | Distinguishes customer messages from assistant responses. |
| `content` | TEXT, required | Stores the conversation text used for continuity and support review. |
| `products_json` | TEXT, optional | Preserves product recommendations displayed with an assistant response. |
| `created_at` | TEXT, required | Orders messages and supports conversation history. |

## `sqlite_sequence` — SQLite internal table

| Field | Type | Why it matters |
|---|---|---|
| `name` | — | Names an AUTOINCREMENT table whose sequence SQLite tracks internally. |
| `seq` | — | Stores the latest generated integer key; application code should not use it as shop data. |

## Important relationships

- `inventory.product_id` joins to `catalogue.product_id`, giving each product size-level stock.
- `chat_messages.user_id` joins to `users.id`, associating conversation history with an account.
- Product recommendation records in `chat_messages.products_json` can repeat catalogue data for historical display, so live availability should be checked against `inventory`.

## Problem 3 website and API notes

- The React/Vite/TypeScript front end lives in `frontend/` and uses hash routes for Home, Products, product details, About Us, Log in, and Create account.
- The FastAPI app lives in `backend/main.py` and reads the SQLite database rather than duplicating catalogue data in the front end.
- `GET /api/products` returns catalogue products; `GET /api/products/{product_id}` adds size-level inventory; `GET /media/{path}` serves catalogue images; `GET /api/health` checks the API.
- The front end uses `VITE_API_URL` when provided and otherwise expects the API at `http://localhost:8000`.
- The floating chat panel is intentionally a stub in this problem; it does not make AI calls yet. Future AI calls must use `PORTKEY_API_KEY`.

## Problem 4 authentication notes

### Authentication & Security

- **User data stored:** `id`, `first_name`, `last_name`, `email`, and `password_hash` are stored in the `users` table. The account's display `name` and `created_at` fields are stored there as well.
- **Password protection:** Passwords are securely hashed with salted PBKDF2-HMAC-SHA256 using 600,000 iterations before storage. Plain-text passwords are never saved, returned by the API, or exposed to the chatbot, preventing unauthorized access by users or automated tools.
- **Implementation note:** The requested security outcome is password hashing; this implementation uses PBKDF2 rather than bcrypt so it matches the format and standard-library verification path used by the current HW4 backend.

- `POST /api/auth/register` accepts first name, last name, email, and password, validates the request, rejects duplicate emails, and inserts a new `users` row.
- `POST /api/auth/login` accepts email and password and returns a public user record only after verification.
- Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes with 600,000 iterations. Plaintext passwords and `password_hash` values are never returned to the front end.
- The supplied test account was migrated from its fixture hash to the secure format and verified with `test@campuscustoms.yale.edu` / `password`.
- A new account, `grace.problem4@campuscustoms.yale.edu`, was created and successfully logged in during verification. An incorrect password was rejected with HTTP 401.

## Problem 5 Backend & PydanticAI Agent Integration

- **Frontend to FastAPI Communication:** The React frontend uses `fetch` to send JSON chat queries to `POST /chat` and receives a structured `ChatReply` containing `reply` and optional product cards. The existing product and authentication REST endpoints remain in `backend/main.py`.
- **Agent Loading:** The PydanticAI agent is initialized in `backend/agent.py` by loading the foundational system prompt from `backend/prompts/prompt.md` and combining it with the configured OpenAI-compatible model through Portkey.
- **Agent files:** `backend/agent.py` owns agent wiring, `backend/tools.py` provides catalogue search and inventory tools, `backend/models.py` defines `ChatRequest`, `ChatReply`, `ProductCard`, and dependencies, and `backend/prompts/prompt.md` contains the Campus Customs voice and safety rules.
- **Model configuration:** AI calls require `PORTKEY_API_KEY`; the optional `PORTKEY_MODEL` defaults to `gpt-4o-mini`, and `PORTKEY_BASE_URL` defaults to `https://api.portkey.ai/v1`. No key is hardcoded.
- **Run command:** From the `backend/` folder, run `uvicorn main:app --reload --port 8000`. Without `PORTKEY_API_KEY`, `/chat` returns HTTP 503 rather than attempting an unauthenticated model call.

## Problem 6 Agent Tools & Lookup Models

- `search_products` searches real `catalogue` fields and returns `ProductCard` results. Its `product_id`, `name`, `garment_type`, `description`, `price`, and `image_file_path` fields support product matching and display without allowing the agent to invent catalogue facts.
- `get_product_info` queries `catalogue` and `inventory` for one product and returns a `ProductInfo`. `product_id` provides the join key, `name` and `garment_type` identify the item, `description` answers product-detail questions, `price` answers pricing questions, `image_file_path` supports a product card, `available_sizes` gives a quick availability summary, and `stock_by_size` preserves exact quantities for size comparisons.
- `get_stock_level` queries `inventory` for one `product_id` and requested `size`, returning a `StockLookup` with `product_id`, `size`, and `stock_quantity`. The explicit `stock_quantity` field makes the exact database result easy for the agent to report and makes zero unambiguously out of stock.
- The agent prompt requires these tools for price and quantity claims. A quantity of zero is treated as out of stock and must be stated clearly.

## Problem 7 Chat search that updates the page

- The `/chat` response returns `ChatReply.products`, a structured list of `ProductCard` objects selected by the agent's catalogue search tool.
- The React chat widget passes those product cards to page state. The page renders them in a “Here’s what we found” product section with image, name, garment type, price, and a short description through the existing card component.
- Chat-generated cards use the same `#/products/{product_id}` navigation as catalogue cards, so clicking one opens the existing single-item page with the large image, full description, price, and live inventory.

### Dynamic Chat Search & Page Updates

- **Data Flow & API Contract:** When a user searches for products via the chat interface, the backend agent calls the catalogue tools, queries `campus_customs.db`, and returns both a text reply and structured product data in `ChatReply.products`.
- **Frontend Rendering:** The React frontend parses the structured `/chat` response, stores the product matches in React state, and dynamically renders them as interactive product cards with images, names, prices, and short information.
- **Navigation Integration:** Clicking any dynamically loaded product card uses the same `product_id` hash navigation as the regular catalogue, triggering the single-item detail view with the large image, full information, and live stock data.

## Problem 8 Customer Memory & Context

- **Chat History Storage:** Authenticated chat messages are stored in SQLite `chat_messages` with `user_id`, `role`, `content`, optional `products_json`, and `created_at`. `POST /chat` loads the user's recent history before the agent call and saves both the new user message and assistant reply afterward. `GET /api/chat/history/{user_id}` reloads history when the logged-in user returns. Guest chats remain available but are sent with no `user_id` and are not persisted.
- **Agent Customer Fields:** For a valid logged-in `user_id`, `main.py` loads the user's `name`/`first_name` and `email` from `users` and passes them as `customer_name` and `customer_email` in `AgentDependencies`, along with `user_id`. The prompt allows light personalization but prohibits exposing private identity data.
- **Page Context:** The React widget sends the active product as `page_context` when the current route is a single-item page. `AgentDependencies.page_context` carries the product identity, description, price, and image path so phrases such as “do you have this in pink?” can be resolved against the product currently being viewed.

## Problem 9 usability improvements

- **Quick-prompt chips:** The chat panel offers clickable prompts for common product searches, stock questions, and price questions. They submit through the same `/chat` contract as typed messages.
- **Typing indicator:** While the agent request is pending, the chat shows animated dots and disables repeated submissions so shoppers receive clear feedback.
- **Order-status tool:** `get_order_status` returns an `OrderStatus` model for demonstration IDs `CC-1001` and `CC-1002`; unknown IDs return `found: false` and `status: "Not found"`. The agent must use this tool rather than inventing shipping data.
- **Off-topic guardrail:** `prompts/prompt.md` directs the agent to politely decline unrelated homework, coding, weather, politics, or medical requests and redirect the conversation to Campus Customs support.

## Problem 10 Campus Customs design

- The storefront uses Manrope for readable interface text, Georgia accents for editorial emphasis, deep navy for trust and structure, warm neutrals for product space, and coral for calls to action.
- Product presentation uses generous image areas, hover zoom, lift, soft shadows, size/stock pills, and a spacious detail layout to make browsing and comparison inviting.
- The chat has a coral floating launcher, navy concierge header, distinct user/agent bubbles, suggestion chips, and animated typing feedback.
- Responsive layouts, fade-up motion, hover transitions, and visible keyboard focus states make the experience feel polished and usable across screen sizes.
- The storefront theme uses Yale Blue `#00356b` and White `#ffffff` as its primary colors, Silver `#d8e1ea` for supporting surfaces, and Yale gold `#bd9b60` for restrained labels and accents.
- The Products page includes category filters for All, T-shirt, Sweatshirt, and Jacket. The chat panel has an independent bounded vertical scroll area, allowing shoppers to review long conversations without obscuring the page.

# Campus Customs System Architecture

## 1. Models and Database (`backend/models.py` and SQLite)

- **Users:** The `users` table stores account identity and credentials, including `id`, `name`, `first_name`, `last_name`, `email`, and `password_hash`. Passwords are salted PBKDF2-HMAC-SHA256 hashes; plaintext passwords are never stored.
- **Chat history:** The `chat_messages` table persists `user_id`, role, message content, optional displayed product JSON, and timestamps for returning logged-in sessions. Guest messages are not persisted.
- **Products:** `catalogue` stores product IDs, names, garment types, descriptions, serialized colors/tags, image paths, and prices. `inventory` stores product ID, size, and quantity for live lookups.
- **Structured types:** `ProductCard`, `ProductInfo`, `StockLookup`, `OrderStatus`, `ChatRequest`, and `ChatReply` keep agent/API outputs explicit and validated.

## 2. Agent Tools and Memory

- **Tools:** `search_products` finds catalogue matches; `get_product_info` returns description, price, and size quantities; `get_stock_level` returns exact stock for a requested size; and `get_order_status` handles demonstration shipping IDs without inventing unknown statuses.
- **Dynamic cards:** The agent returns `ChatReply.products`; React renders those cards and uses each `product_id` to open the single-item page.
- **Context:** `AgentDependencies` carries `user_id`, customer name/email, and active `page_context` so the agent can personalize safely and resolve “this” on a product page.

## 3. Safety and Audit

- **Safety:** `backend/prompts/prompt.md` enforces store scope, database-backed prices/stock, privacy protection, prompt-injection resistance, no password/payment handling, and polite redirection for unsafe or off-topic requests.
- **Audit trail:** `backend/audit.py` appends one JSON object per line to `output/audit_trail.json`. Records include UTC time, tool/loop name, bounded arguments/results, and stop reason. Sensitive fields are filtered and existing records are never cleared between runs.

## 4. Specs and Execution

- **Limits:** Chat input is capped at 2,000 characters, history at 20 messages, product matches at 8 cards, and audit arguments/results are truncated. The agent uses structured PydanticAI output and bounded database tools.
- **Backend:** From `HW 4/backend`, run `uvicorn main:app --reload --port 8000`.
- **Frontend:** From `HW 4/frontend`, run `npm.cmd run dev`.
- **Configuration:** AI calls require `PORTKEY_API_KEY`; `PORTKEY_MODEL` defaults to `gpt-4o-mini`, and `PORTKEY_BASE_URL` defaults to `https://api.portkey.ai/v1`.
