from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from ai_engine.chatbot import chain, llm
from .tools import get_customer, get_customer_requests
from langchain_core.prompts import ChatPromptTemplate


# ============================================================
# 1. STATE
# ============================================================
class AgentState(TypedDict):
    question: str
    customer_id: Optional[int]
    intent: Optional[str]
    context: Optional[str]
    answer: Optional[str]


# ============================================================
# 2. ROUTER LLM
# ============================================================
router_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a query classifier for a home maintenance app.
Classify the user's question into exactly one word:
- "personal" — if it asks about their own request status, assigned worker, booking history, complaint, or account details
- "general" — if it asks about a technical issue (electrical, plumbing, appliance problem) or general help

Reply with ONLY one word: personal or general. No punctuation, no explanation."""),
    ("human", "{question}")
])
router_chain = router_prompt | llm


# ============================================================
# 3. NODES
# ============================================================

def classify_node(state: AgentState) -> AgentState:
    result = router_chain.invoke({"question": state["question"]})
    intent_raw = result.content.strip().lower()
    print("DEBUG - Router raw output:", repr(intent_raw))   # 👈 debug line, remove later
    state["intent"] = "personal" if "personal" in intent_raw else "general"
    return state


def personal_tool_node(state: AgentState) -> AgentState:
    customer_id = state.get("customer_id")

    if not customer_id:
        state["context"] = "Customer not logged in / ID not available."
        return state

    info = get_customer(customer_id)
    if not info["success"]:
        state["context"] = "No customer record found."
        return state

    result = get_customer_requests(customer_id)

    if not result["requests"]:
        state["context"] = f"Customer Name: {info['customer']['name']}\nNo service requests booked yet."
        return state

    lines = [f"Customer Name: {info['customer']['name']}", "Service Requests:"]
    for r in result["requests"]:
        lines.append(
            f"- Request #{r['id']} | Status: {r['status']} | "
            f"Assigned Worker: {r['worker']} | Date: {r['requested_at']} | "
            f"Site: {r['site_address']}"
        )

    state["context"] = "\n".join(lines)
    return state


def general_node(state: AgentState) -> AgentState:
    state["context"] = None
    return state


def answer_node(state: AgentState) -> AgentState:
    if state.get("context"):
        final_input = f"""
Customer Question:
{state['question']}

Customer Details (use this to answer, list ALL requests if multiple, do not ask for Request ID):
{state['context']}
"""
    else:
        final_input = state["question"]

    response = chain.invoke({"question": final_input})
    state["answer"] = response.content
    return state


# ============================================================
# 4. ROUTING FUNCTION
# ============================================================
def route_after_classify(state: AgentState) -> str:
    return "personal_tool" if state["intent"] == "personal" else "general"


# ============================================================
# 5. GRAPH
# ============================================================
builder = StateGraph(AgentState)

builder.add_node("classify", classify_node)
builder.add_node("personal_tool", personal_tool_node)
builder.add_node("general", general_node)
builder.add_node("answer", answer_node)

builder.set_entry_point("classify")

builder.add_conditional_edges(
    "classify",
    route_after_classify,
    {
        "personal_tool": "personal_tool",
        "general": "general",
    }
)

builder.add_edge("personal_tool", "answer")
builder.add_edge("general", "answer")
builder.add_edge("answer", END)

agent_graph = builder.compile()


# ============================================================
# 6. ENTRY FUNCTION
# ============================================================
def run_agent(question: str, customer_id: int = None) -> str:
    result = agent_graph.invoke({
        "question": question,
        "customer_id": customer_id,
        "intent": None,
        "context": None,
        "answer": None,
    })
    return result["answer"]