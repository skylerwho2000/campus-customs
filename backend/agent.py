import os
from functools import lru_cache
from pathlib import Path
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart
try:
    from .models import AgentDependencies, ChatReply
    from .tools import register_tools
except ImportError:
    from models import AgentDependencies, ChatReply
    from tools import register_tools

PROMPT_PATH = Path(__file__).parent / "prompts" / "prompt.md"

@lru_cache(maxsize=1)
def get_agent() -> Agent[AgentDependencies, ChatReply]:
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is not configured")
    provider = OpenAIProvider(api_key=api_key, base_url=os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1"))
    model = OpenAIChatModel(os.getenv("PORTKEY_MODEL", "gpt-4o-mini"), provider=provider)
    agent = Agent(model, deps_type=AgentDependencies, output_type=ChatReply, system_prompt=PROMPT_PATH.read_text(encoding="utf-8"))
    return register_tools(agent)

async def run_chat(message: str, history: list[dict[str, str]] | None = None, user_id: int | None = None, customer_name: str | None = None, customer_email: str | None = None, page_context=None) -> ChatReply:
    agent = get_agent()
    model_history = []
    for item in history or []:
        if item.get("role") == "user" and item.get("content"):
            model_history.append(ModelRequest(parts=[UserPromptPart(content=item["content"])]) )
        elif item.get("role") == "assistant" and item.get("content"):
            model_history.append(ModelResponse(parts=[TextPart(content=item["content"])]) )
    result = await agent.run(message, message_history=model_history, deps=AgentDependencies(user_id=user_id, customer_name=customer_name, customer_email=customer_email, page_context=page_context))
    return result.output
