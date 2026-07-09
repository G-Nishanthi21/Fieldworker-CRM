import markdown
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .chat_service import ask_chatbot
from visits.models import Visit


@login_required
def chatbot_page(request):
    answer = None
    question = None

    if request.method == "POST":
        question = request.POST.get("question")
        request_id = request.POST.get("request_id")

        details = None
        if request_id:
            try:
                req = Visit.objects.get(id=request_id)
                details = f"""
                Request ID: {req.id}
                Status: {req.status}
                Assigned Worker: {req.worker.get_full_name() if req.worker else 'Not Assigned'}
                """
            except Visit.DoesNotExist:
                details = "No request found with this ID."

        if question:
            try:
                raw_answer = ask_chatbot(question, details)
                answer = markdown.markdown(raw_answer)
            except Exception as e:
                answer = f"<p>Error: {str(e)}</p>"

    return render(request, "dashboard/chatbot.html", {
        "answer": answer,
        "question": question,
    })