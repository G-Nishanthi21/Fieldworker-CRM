from ai_engine.chatbot import llm
from .tools import get_customer, get_customer_status, get_assigned_worker

from langchain_core.prompts import ChatPromptTemplate

router_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a query classifier. Classify the user's question into exactly one word:
- "personal" — if it asks about their own request status, assigned worker, booking, complaint, or account details
- "general" — if it asks about a technical issue (electrical, plumbing, appliance problem) or general help

Reply with ONLY one word: personal or general"""),
    ("human", "{question}")
])

router_chain = router_prompt | llm


def classify_query(question):
    result = router_chain.invoke({"question": question})
    return result.content.strip().lower()


def build_customer_context(customer_id):
    info = get_customer(customer_id)
    if not info["success"]:
        return "No customer record found for this account."

    status = get_customer_status(customer_id)
    worker = get_assigned_worker(customer_id)
    worker_name = worker.get("worker") if worker.get("assigned") else "Not Assigned"

    return f"""
    Customer Name: {info['customer']['name']}
    Status: {status.get('status', 'N/A')}
    Assigned Worker: {worker_name}
    """


def ask_agent(question, customer_id=None):
    intent = classify_query(question)   # 👈 LLM decides

    if intent == "personal" and customer_id:
        details = build_customer_context(customer_id)
        final_input = f"""
Customer Question:
{question}

Customer Details (use this to answer):
{details}
"""
    else:
        final_input = question

    response = chain.invoke({"question": final_input})
    return response.content