from django.urls import path
from rest_framework import routers

from .views import UserViewSet, ManageUserView, CreateUserView

router = routers.DefaultRouter()
router.register("users", UserViewSet)

urlpatterns = [
    path("users/register/", CreateUserView.as_view(), name="user-create"),
    path("users/me/", ManageUserView.as_view(), name="me"),
] + router.urls

app_name = "social_media"
