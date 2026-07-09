# from langchain_core.messages import HumanMessage
# from .tools import get_customer, get_customer_status, get_assigned_worker


# def crm_node(state):

#     question = state["question"].lower()

#     if "status" in question:
#         result = get_customer_status.invoke(
#             {"customer_id": state["customer_id"]}
#         )

#     elif "worker" in question or "assigned" in question:
#         result = get_assigned_worker.invoke(
#             {"customer_id": state["customer_id"]}
#         )

#     else:
#         result = get_customer.invoke(
#             {"customer_id": state["customer_id"]}
#         )

#     return {
#         "response": str(result)
#     }


from langchain_core.messages import HumanMessage
from .tools import get_customer, get_customer_status, get_assigned_worker


def crm_node(state):

    question = state["question"].lower()

    if "status" in question:
        result = get_customer_status.invoke(
            {"customer_id": state["customer_id"]}
        )

    elif "worker" in question or "assigned" in question:
        result = get_assigned_worker.invoke(
            {"customer_id": state["customer_id"]}
        )

    else:
        result = get_customer.invoke(
            {"customer_id": state["customer_id"]}
        )

    return {
        "response": str(result)
    }


from .state import AgentState
from ai_engine.agents.node import chain


def external_node(state: AgentState):
    """
    Handles all non-personal queries using the existing FixMate AI chain.
    """

    question = state["question"]

    response = chain.invoke(
        {
            "question": question
        }
    )

    return {
        "question": question,
        "customer_id": state["customer_id"],
        "route": "external",
        "response": response.content,
    }