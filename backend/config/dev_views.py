from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from faker import Faker
from users.models import User

fake = Faker()

@api_view(["POST"])
@permission_classes([IsAdminUser])
def populate_fake_data(request):
    for _ in range(5):
        User.objects.create_user(
            username=fake.user_name(),
            email=fake.email(),
            password="password",
            role="student"
        )
    return Response({"status": "ok", "message": "Users seeded"})
