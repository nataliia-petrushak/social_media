from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from rest_framework import generics, mixins, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from models import Post, Hashtag, Like, Comment
from .serializers import (
    UserSerializer,
    UserListSerializer,
    UserDetailSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    HashtagSerializer,
    HashtagListSerializer,
    HashtagDetailSerializer
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve users with filters"""
        username = self.request.query_params.get("username")

        queryset = self.queryset

        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "retrieve":
            return UserDetailSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class APILogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if self.request.data.get('all'):
            token: OutstandingToken
            for token in OutstandingToken.objects.filter(user=request.user):
                _, _ = BlacklistedToken.objects.get_or_create(token=token)
            return Response({"status": "OK, goodbye, all refresh tokens blacklisted"})
        refresh_token = self.request.data.get("refresh_token")
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        return Response({"status": "OK, goodbye"})


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return HashtagListSerializer
        if self.action == "retrieve":
            return HashtagDetailSerializer
        return self.serializer_class


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author").prefetch_related("hashtags")
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        hashtag = self.request.query_params.get("hashtag")
        title = self.request.query_params.get("title")
        liked_posts = self.request.query_params.get("liked")
        authors = self.request.query_params.get("authors")

        if authors:
            if authors == "me":
                queryset = queryset.filter(author=self.request.user)
            if authors == "followings":
                following_users = self.request.user.followings.all()
                queryset = queryset.filter(author__in=following_users)

        if hashtag:
            queryset = queryset.filter(hashtags__name__icontains=hashtag)

        if title:
            queryset = queryset.filter(title__icontains=title)

        if liked_posts:
            queryset = queryset.filter(likes__liker=user)

        return queryset.annotate(
            is_liked=Exists(
                Like.objects.filter(liker=self.request.user, post_id=OuterRef("pk"))
            )
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return self.serializer_class


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def follow_unfollow(request, pk):
    user_to_follow = get_object_or_404(get_user_model(), pk=pk)
    current_user = request.user
    following = user_to_follow.followings.all()

    if current_user in following:
        user_to_follow.followings.remove(current_user.id)
        return Response(
            {"message": f"You are not following {user_to_follow.username} anymore"}
        )

    user_to_follow.followings.add(current_user.id)
    return Response(data={"message": f"You are following {user_to_follow.username}"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def like_unlike(request, pk):
    user = request.user
    post = get_object_or_404(Post, pk=pk)
    like = Like.objects.filter(liker=user, post=post)

    if like:
        like.delete()
        return Response(
            {"message": "You remove like from this post"},
            status=status.HTTP_204_NO_CONTENT,
        )

    Like.objects.create(liker=user, post=post)
    return Response({"message": "You liked this post"}, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("author", "post")
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        return Comment.objects.filter(post=post)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user, post=post)
