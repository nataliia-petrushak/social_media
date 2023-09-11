from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from .views import (
    UserViewSet,
    ManageUserView,
    CreateUserView,
    APILogoutView,
    PostViewSet,
    CommentViewSet,
    HashtagViewSet,
    like_unlike,
    follow_unfollow,
    get_followers,
    get_followings
)

router = routers.DefaultRouter()
router.register("users", UserViewSet)
router.register("posts", PostViewSet)
router.register("hashtags", HashtagViewSet)

comment_list = CommentViewSet.as_view(actions={"get": "list", "post": "create"})

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="user-create"),
    path("login/", TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('login/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path("logout/", APILogoutView.as_view(), name="logout"),
    path("users/me/", ManageUserView.as_view(), name="me"),
    path("users/me/followers/", get_followers, name="user-followers"),
    path("users/me/followings/", get_followings, name="user-followings"),
    path("users/<int:pk>/follow/", follow_unfollow, name="follow-unfollow-user"),
    path("posts/<int:pk>/like/", like_unlike, name="like-unlike-post"),
    path(
            "posts/<int:pk>/comments/",
            comment_list,
            name="comment-post",
        ),
] + router.urls

app_name = "social_media"
