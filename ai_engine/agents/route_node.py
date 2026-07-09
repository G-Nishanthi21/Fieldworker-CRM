from .state import AgentState
from .llm import llm


def router_node(state: AgentState):

    prompt = f"""
Classify the user query.

Return only one word.

personal
external

Examples:

What is my status? -> personal
Who is my assigned worker? -> personal
What is my phone number? -> personal
What company am I registered under? -> personal

Pipe is leaking -> external
Fan is not rotating -> external
How to fix switch board? -> external
Safety precautions for electrical work -> external

User Query:
{state['question']}
"""

    route = llm.invoke(prompt).content.strip().lower()

    return {"route": route}