from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from matching.views import ImportJobViewSet, detect_user_conflicts
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r'imports', ImportJobViewSet, basename='importjob')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('matching.urls_app')),
    path('', include(router.urls)),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += [
    path("conflicts/", detect_user_conflicts)
]
