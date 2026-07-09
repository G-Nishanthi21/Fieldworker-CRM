from typing import TypedDict


class AgentState(TypedDict):
    question: str
    customer_id: int
    route: str
    response: str