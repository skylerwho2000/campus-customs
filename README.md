# Campus Customs — HW4

Campus Customs is a React/Vite/TypeScript storefront with a FastAPI and PydanticAI shop concierge.

The agent itself is four files under `backend/`:

- `backend/prompts/prompt.md` — system prompt, voice, and safety rules
- `backend/agent.py` — PydanticAI agent loading and execution
- `backend/tools.py` — catalogue, inventory, and order-status tools
- `backend/models.py` — structured request, response, product, stock, and dependency types

## Place the local data pack

The public repository excludes the course data. After cloning, place the local data pack so the paths are:

```text
hw4/data/campus_customs.db
hw4/data/products/
```

The database and product images must remain local and must not be committed.

## Run locally

From `backend/`, start the FastAPI backend:

```powershell
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

From `frontend/` in a second terminal, start the React/Vite front end:

```powershell
npm install
npm run dev
```

Copy `.env.example` to `.env` and set `PORTKEY_API_KEY` before using the AI chat. The public submission intentionally excludes the SQLite database and product images; the application expects those local data files at `data/campus_customs.db` and `data/products/`.

See `output/harness.md` for the architecture, safety rules, tools, memory, audit trail, and execution notes.
