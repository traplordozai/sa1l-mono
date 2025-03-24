from rest_framework.views import APIView
from rest_framework.response import Response
from forms.models import DynamicForm
from rest_framework.permissions import IsAuthenticated

class DynamicFormDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, form_id):
        form = DynamicForm.objects.get(id=form_id)
        return Response({
            "id": form.id,
            "name": form.name,
            "schema": form.schema
        })
