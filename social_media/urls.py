from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from .views import UserViewSet, ManageUserView, CreateUserView, APILogoutView

router = routers.DefaultRouter()
router.register("users", UserViewSet)

urlpatterns = [
    path("users/register/", CreateUserView.as_view(), name="user-create"),
    path("users/me/", ManageUserView.as_view(), name="me"),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("logout/", APILogoutView.as_view(), name="logout")
] + router.urls

app_name = "social_media"
