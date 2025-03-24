from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import openai
import os
from django.conf import settings

@api_view(["POST"])
def deepseek_chat(request):
    try:
        messages = request.data.get("messages", [])
        if not messages:
            return Response({"error": "Messages are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        res = openai.ChatCompletion.create(
            model="deepseek-coder",
            messages=messages,
            api_key=settings.OPENROUTER_API_KEY
        )
        return Response({"reply": res["choices"][0]["message"]["content"]})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def semantic_filter_parse(request):
    try:
        query = request.data.get("query", "")
        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        # TODO: Replace with DeepSeek in prod
        if "not submitted" in query.lower():
            return Response({"filters": [{"field": "submitted", "op": "=", "value": "false"}]})
        return Response({"filters": [{"field": "status", "op": "contains", "value": query}]})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
