from .chatbot import chain


def ask_chatbot(question, request_details=None):
    if request_details:
        user_input = f"""
Customer Question:
{question}

Request Details:
{request_details}
"""
    else:
        user_input = question

    response = chain.invoke({"question": user_input})
    return response.content