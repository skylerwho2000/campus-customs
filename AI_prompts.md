# AI Prompts

This file records the prompts typed while completing HW4. Keep one section for each problem and update the relevant section as the work develops.

## Project-wide implementation requirement

Use `PORTKEY_API_KEY` for any AI model calls in this project. Do not hardcode the key or use a different environment-variable name.

## Problem 1: Vibe coder prompts

### Prompt(s) I typed

- Initial prompt: “How let's work on a new project and all things we discussing today should go into [HW 4](<HW 4/>) folder. I already put a data.zip in”
- Follow-up prompt: “Similar to HW1,HW2, and HW3 let's create a AI_prompts.md and keep it updated as we work. Put one section for each problem. We have problem 1-13. This step right now is Problem 1: Vibe coder prompts. Each section must include:
  - The problem number and title
  - At least one prompt I typed
  - One follow-up prompt if needed (and one sentence on what was lacking after the first)”
- Follow-up prompt: “Set up a virtual environment in HW 4 folder and give me the commands to start it”
- Follow-up prompt: “unzip the data.zip folder”

### Follow-up prompt, if needed

- The follow-up clarified that the file must contain all 13 problem sections and established the required record format for each section.
- The environment follow-up resulted in a project-local `HW 4/.venv` using Python 3.14.7.
- The data follow-up extracted `data.zip` into `HW 4/data/`, including `campus_customs.db` and 102 product images.

### What was lacking after the first prompt

The first prompt identified the HW4 folder and the data archive but did not specify the 13-problem prompt-log structure, environment setup, or the required follow-up and “what was lacking” documentation.

## Problem 2: Analyze the database

### Prompt(s) I typed

- Initial prompt: “Problem 2: Analyze the database. Look at the database `data/campus_customs.db` and understand the fields of each table. At a minimum you should understand `catalogue`, `inventory`, and `users`. Start the file `output/harness.md`. Write down each table and its fields, and one short line on why each field matters for the shop or the chatbot. We will keep growing the harness.md later”

### Follow-up prompt, if needed

No follow-up prompt needed yet; the database schema and initial harness documentation were clear.

### What was lacking after the first prompt

The first prompt did not explicitly mention the supporting `chat_messages` and SQLite internal `sqlite_sequence` tables, so those were documented as well to make the harness complete.

## Problem 3: Build the Campus Customs website

### Prompt(s) I typed

- Initial prompt: “Problem 3: Build the Campus Customs website. Scaffold a React + Vite + TypeScript front end for Campus Customs with Home, Products, About Us, Log in, and Create account pages; use original Campus Customs-style wording informed by yalebulldogblue.com; show catalogue products and image paths; add single-item pages with stock; add a bottom-right chat stub; and start a simple FastAPI API in `backend/main.py` for products and images.”

### Follow-up prompt, if needed

- Added the React/Vite/TypeScript scaffold, catalogue-backed product browsing and detail pages, responsive styling, auth placeholders, and a floating chat preview. Added FastAPI routes for products, product details, images, and health checks.

### What was lacking after the first prompt

The first prompt did not specify the visual direction, client-side routing approach, API response shape, or how to keep chat clearly stubbed until the later agent backend is built.

## Problem 4: Create account and login

### Prompt(s) I typed

- Initial prompt: “Problem 4: Create account and login. Build a normal create-account/login flow with first name, last name, email, password, and confirm password; store new accounts in `users`; hash passwords securely; use the seeded test user; and confirm both seeded login and a brand-new account.”
- Follow-up prompt: “Let's update `output/harness.md` with how auth works: Authentication & Security. User Data Stored: `id`, `first_name`, `last_name`, `email`, and `password_hash` in the `users` table. Password Protection: Passwords are securely hashed (using bcrypt) before storing. Plain-text passwords are never saved, preventing unauthorized access by users or automated tools.”

### Follow-up prompt, if needed

- Added `/api/auth/register` and `/api/auth/login`, secure salted PBKDF2 password hashing, password confirmation, duplicate-email handling, and working front-end forms. Migrated the supplied test user's known password to the secure hash format and tested both account paths.

### What was lacking after the first prompt

The first prompt did not specify a password-hashing algorithm, session strategy, API response shape, or how the existing seed hash should be migrated, so those implementation choices were defined during the build.

## Problem 5: PydanticAI agent backend

### Prompt(s) I typed

- Initial prompt: “Problem 5: PydanticAI agent backend. Build the shop chatbot as a PydanticAI agent behind FastAPI, with `backend/prompts/prompt.md`, `backend/agent.py`, `backend/tools.py`, and `backend/models.py`; expose `/chat`; connect the front-end widget; use Campus Customs voice and safety basics; document the integration in `output/harness.md`; and run from `backend/` with `uvicorn main:app --reload --port 8000`.”
- Follow-up prompt: “Let's make sure this step has no problem - QC it please”

### Follow-up prompt, if needed

- Added the four-file PydanticAI agent layer, catalogue search and inventory tools, structured chat models, Portkey/OpenAI-compatible model configuration using `PORTKEY_API_KEY`, the `/chat` route, front-end widget wiring, prompt safety basics, and harness documentation.
- QC passed Python compilation, dependency checks, API health/products/detail routes, `/chat` route registration, missing-key protection, and the React production build. Live model output was not called because no API key was used during QC.

### What was lacking after the first prompt

The first prompt did not define the structured reply schema, initial tool boundaries, Portkey model configuration, or the behavior when `PORTKEY_API_KEY` is unavailable, so those details were specified during implementation.

## Problem 6: Tools: product info and stock

### Prompt(s) I typed

- Initial prompt: “Problem 6: Tools: product info and stock. Give the agent tools that look up real information from `campus_customs.db` for product descriptions, prices, and stock by size. The agent must use the database, not invent prices or quantities, and must clearly say when a size is out of stock.”
- Follow-up prompt: “Expand `prompts/prompt.md` so the agent knows to call these tools for price and stock questions. Add or update return types in `models.py`. In `output/harness.md`, list each tool and explain which model fields you chose for lookup results and why.”

### Follow-up prompt, if needed

- Added structured `ProductInfo` and `StockLookup` return types, aligned the tools to `get_product_info` and `get_stock_level`, and updated the agent prompt and harness with field rationales and explicit out-of-stock behavior.

### What was lacking after the first prompt

The first prompt did not specify whether product information and stock should be returned by one tool or separate tools, so the implementation provides both a complete product lookup and a concise stock-only lookup.

## Problem 7: Chat search that updates the page

### Prompt(s) I typed

- Initial prompt: “Problem 7: Chat search that updates the page. When a customer asks about a type of item, such as hoodies, have the agent search the catalogue and dynamically show matching product cards with image, name, price, and short info. Return structured product matches through the API, and make sure chat-generated cards still open the existing single-item detail page.”
- Follow-up prompt: “Update `prompts/prompt.md` and `output/harness.md` so it is clear how search results reach the page. Document the data flow/API contract, frontend rendering, and navigation integration.”

### Follow-up prompt, if needed

- Connected `ChatReply.products` to React state, added a dynamic matching-products section, and reused the existing product-card navigation for chat results.
- Documented the complete search-to-page flow in the agent prompt and harness: database/tool lookup, structured response, React rendering, and shared detail navigation.

### What was lacking after the first prompt

The first prompt did not specify where the structured product matches should live in the response or how to preserve detail-page navigation, so the existing `products` field and shared `Card` component were used.

## Problem 8: Customer memory

### Prompt(s) I typed

- Initial prompt: “Problem 8: Customer memory. When a shopper is logged in, save and reload their chat history in the database. Pass the customer's name and email to the agent, and pass active product-page context so questions such as ‘do you have this in pink?’ resolve to the item being viewed. Guests can chat without persistence. Document storage, customer fields, and page context in `output/harness.md`.”
- Follow-up prompt: “let's do a QC for stemps so far. let me know if everything runs well”

### Follow-up prompt, if needed

- Added authenticated history loading/saving through `chat_messages`, public user identity in `AgentDependencies`, `page_context` in chat requests and dependencies, browser-session user retention after login, and guest-chat behavior without persistence.
- QC passed the frontend build, backend compilation, dependency check, API route checks, product/database checks, history safeguards, and agent history/customer-dependency wiring.

### What was lacking after the first prompt

The first prompt did not specify the API shape for user identity, how the browser remembers the logged-in user, or how the active product is serialized into agent context, so those contracts were defined in `ChatRequest` and `AgentDependencies`.

## Problem 9: Usability improvements

### Prompt(s) I typed

- Initial prompt: “Problem 9: Usability improvements. Choose two front-end and two agent/backend improvements. Implement quick-prompt suggestion chips, a loading typing indicator, an order tracking/shipping status tool, and an off-topic safety filter. Write `output/usability.md` describing what each adds and why it helps.”

### Follow-up prompt, if needed

- Created `output/usability.md` first, then added chat chips, a typing indicator, the structured mock `get_order_status` tool, and an expanded off-topic guardrail in `prompts/prompt.md`.

### What was lacking after the first prompt

The first prompt specified the four desired improvements but did not define the mock order IDs, structured order-status fields, or the exact scope and redirect behavior for off-topic requests.

## Problem 10: Style the website

### Prompt(s) I typed

- Initial prompt: “Problem 10: Style the website. Add creative storefront design with fonts, color, hierarchy, motion, product presentation, and chat feel. Write `output/design.md` explaining what changed and why it helps customers stay and buy.”
- Follow-up prompt: “Update the website color to Yale Blue `#00356b` and White `#ffffff`; silver or gold may be added if needed.”
- Follow-up prompt: “Overwrite `output/app_check.html` to document the three screenshots, add item categories such as T-shirt, sweatshirt, and jacket, and add scrolling so long chat text does not cover the website.”
- Follow-up prompt: “Put the screenshot image files in `output/app_check_images/` and link them from `app_check.html` with relative paths.”

### Follow-up prompt, if needed

- Created `output/design.md` and refined the storefront with typography and palette documentation, product-card hover lift and shadows, fade-in motion, focus states, responsive polish, and the styled chat launcher, header, bubbles, chips, and typing indicator.
- Updated the storefront to Yale Blue and White with Silver surfaces and a restrained Yale gold accent.
- Added Products-page category filters, made the chat panel independently scrollable, and rewrote `output/app_check.html` with the three screenshot captions.

### What was lacking after the first prompt

The first prompt provided the desired design categories but did not specify a visual system or accessibility details, so a navy/warm-neutral/coral system and visible keyboard focus states were added.

## Problem 11: Site testing (app check)

### Prompt(s) I typed

- Initial prompt: “Problem 11: Site testing (app check). Test the live site and document screenshots in `output/app_check.html` for an inventory check, dynamic category search cards, and one Problem 9 usability feature. Store screenshots in `output/app_check_images/` and link them with relative paths.”

### Follow-up prompt, if needed

- Created the grade-friendly `output/app_check.html`, relative screenshot links, and `output/app_check_images/`. Captured the live chat usability-chip state. Inventory and dynamic-search captures are labeled pending because the live Portkey request currently returns a connection error.

### What was lacking after the first prompt

The first prompt assumed the external model endpoint would be reachable; it did not specify how to document an honest partial run when the UI works but the AI dependency is unavailable.

## Problem 12: Audit trail, safety, finish harness

### Prompt(s) I typed

- Initial prompt: “Problem 12: Audit trail, safety, finish harness. Keep an append-only `output/audit_trail.json` of agent-loop activity with time, tool name, short arguments/result, and stop reason. Add safety rules to `prompts/prompt.md` and finish `output/harness.md` so the architecture, models/database, tools/memory, safety/audit, limits, and run commands are clear.”

### Follow-up prompt, if needed

- Added append-only JSONL audit records with redaction and truncation, expanded prompt safety rules, and completed the system architecture section in `output/harness.md`.

### What was lacking after the first prompt

The first prompt did not specify whether the JSON audit should be rewritten as an array or appended as records, what sensitive fields to redact, or which execution limits belong in the harness, so the implementation uses append-only one-object-per-line JSON with bounded redacted fields.

## Problem 13: Push to GitHub and submit the URL

### Prompt(s) I typed

- Initial prompt: “Problem 13: Push to GitHub and submit the URL. Put the code in a folder named `hw4`, push it to a public GitHub repository, exclude `.env`, `campus_customs.db`, and product images with `.gitignore`, and include `.env.example` with placeholders.”

### Follow-up prompt, if needed

- Prepared a sanitized `hw4` repository with `.gitignore`, `.env.example`, README, application code, documentation, screenshots, and a local commit. A public GitHub URL still requires the user's repository destination and GitHub authentication.

### What was lacking after the first prompt

The first prompt did not provide a GitHub repository URL, account, or authentication method, so the local submission repository was prepared but cannot be pushed publicly yet.
