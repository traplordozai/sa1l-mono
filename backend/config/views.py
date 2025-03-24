from rest_framework.decorators import api_view
from rest_framework.response import Response
import openai

openai.api_key = os.getenv("OPENROUTER_API_KEY")

@api_view(["POST"])
def deepseek_chat(request):
    messages = request.data.get("messages", [])
    res = openai.ChatCompletion.create(
        model="deepseek-coder",
        messages=messages
    )
    return Response({"reply": res["choices"][0]["message"]["content"]})

@api_view(["POST"])
def semantic_filter_parse(request):
    query = request.data.get("query", "")
    # MOCK - replace with DeepSeek in prod
    if "not submitted" in query.lower():
        return Response({"filters": [{"field": "submitted", "op": "=", "value": "false"}]})
    return Response({"filters": [{"field": "status", "op": "contains", "value": query}]})
