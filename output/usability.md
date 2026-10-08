# Problem 9: Usability improvements

This plan records the four usability improvements selected for Campus Customs before implementation.

## Front-end improvements

### 1. Quick-prompt suggestion chips

**What to add:** Add clickable chat chips for common requests such as “Show me hoodies,” “What’s in stock?”, and “Check prices.” Clicking a chip submits that text through the existing chat flow.

**Why it helps:** Shoppers can discover the chatbot’s capabilities and start useful product searches without guessing what to type, reducing friction on mobile and for first-time visitors.

### 2. Loading spinner / typing indicator

**What to add:** Show an animated three-dot typing indicator in the chat panel while the FastAPI agent is responding.

**Why it helps:** Model responses take longer than a local UI action. The indicator confirms that the request was received and prevents the chat from feeling frozen.

## Agent / backend improvements

### 3. Order tracking / shipping status tool

**What to add:** Add a safe mock `get_order_status` tool that looks up a small set of demonstration order IDs and returns structured status, carrier, tracking number, and estimated delivery fields. Unknown IDs return an explicit not-found result.

**Why it helps:** It gives the agent a realistic support ability without inventing shipment facts or connecting to a real fulfillment system before one exists.

### 4. Guardrail / off-topic safety filter

**What to add:** Expand the system prompt with a clear scope rule: politely decline homework, coding, weather, politics, and other unrelated requests, then redirect the shopper to Campus Customs products, prices, stock, orders, or account help.

**Why it helps:** The agent stays useful and on-brand, reduces wasted model calls, and avoids confidently answering questions outside the shop’s verified data.
