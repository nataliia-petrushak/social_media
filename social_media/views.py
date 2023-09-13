from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, mixins, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .permissions import IsAuthorOrReadOnly
from .models import Post, Hashtag, Like, Comment, ScheduledPost
from .serializers import (
    CreateUserSerializer,
    UserSerializer,
    UserListSerializer,
    UserDetailSerializer,
    ScheduledPostSerializer,
    ScheduledPostListSerializer,
    ScheduledPostDetailSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    HashtagSerializer,
    HashtagListSerializer,
    HashtagDetailSerializer
)


class CreateUserView(generics.CreateAPIView):
    """Users can register their account"""
    serializer_class = CreateUserSerializer


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        username = self.request.query_params.get("username")

        if username:
            self.queryset = self.queryset.filter(username__icontains=username)

        return self.queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "retrieve":
            return UserDetailSerializer

    @extend_schema(
        # extra parameters added to the schema
        parameters=[
            OpenApiParameter(
                name="username",
                type=OpenApiTypes.STR,
                description="Filter users by username (ex. ?username=user1)"
            )
        ],
        description="Users can retrieve information about other users,"
                    " and see the whole list of users."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Users can manage their page and add bio, images, and details.
    They can also delete their account"""
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def followers(request):
    """The user can see all the users that follow him"""
    user = request.user
    user_followers = user.followers.all()
    serializer = UserListSerializer(user_followers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def followings(request):
    """The user can see the list of people he is following"""
    user = request.user
    user_followings = user.followings.all()
    serializer = UserListSerializer(user_followings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class APILogoutView(APIView):
    """The user can log out from his account"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if self.request.data.get("all"):
            for token in OutstandingToken.objects.filter(user=request.user):
                _, _ = BlacklistedToken.objects.get_or_create(token=token)
            return Response(
                {"status": "All refresh tokens blacklisted. "
                           "Logout successful"}
            )
        refresh_token = self.request.data.get("refresh_token")
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        return Response({"status": "Logout successful"})


class HashtagViewSet(
    generics.ListCreateAPIView,
    generics.RetrieveAPIView,
    viewsets.GenericViewSet
):
    """Users can create hashtags, see the list of hashtags,
    and see how many posts with this hashtag"""
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return HashtagListSerializer
        if self.action == "retrieve":
            return HashtagDetailSerializer
        return self.serializer_class


class PostViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Users can see all their posts and posts of the
    users they are following.They can retrieve details about posts,
    including details about the author. Users can also see if they liked
    the post, how many people liked it, and comments."""
    queryset = Post.objects.select_related(
        "author"
    ).prefetch_related("hashtags")
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user
        user_followings = user.followings.all()
        queryset = self.queryset.filter(
            Q(author=user) | Q(author__in=user_followings)
        )

        hashtag = self.request.query_params.get("hashtag")
        title = self.request.query_params.get("title")

        if hashtag:
            queryset = queryset.filter(hashtags__name__icontains=hashtag)

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.annotate(
            is_liked=Exists(
                Like.objects.filter(
                    liker=self.request.user, post_id=OuterRef("pk")
                )
            )
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return self.serializer_class

    @extend_schema(
        # extra parameters added to the schema
        parameters=[
            OpenApiParameter(
                name="hashtag",
                type=OpenApiTypes.STR,
                description="Filter posts by "
                            "hashtag (ex. ?hashtag=interesting)"
            ),
            OpenApiParameter(
                name="title",
                type=OpenApiTypes.STR,
                description="Filter posts by "
                            "title (ex. ?title=Improve your life)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ScheduledPostViewSet(
    viewsets.ModelViewSet
):
    """Users can choose the time to create a post.
    They also can see the list of all their scheduled posts,
    and details, make changes, and delete."""
    queryset = ScheduledPost.objects.select_related(
        "author"
    ).prefetch_related("hashtags")
    serializer_class = ScheduledPostSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ScheduledPostListSerializer
        if self.action == "retrieve":
            return ScheduledPostDetailSerializer
        return self.serializer_class


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def liked_posts(request):
    """Users can see the lists of posts they have liked"""
    user = request.user
    posts = Post.objects.filter(likes__liker=user)
    serializer = PostListSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def follow_unfollow(request, pk):
    """Users can follow & unfollow other users"""
    user_to_follow = get_object_or_404(get_user_model(), pk=pk)
    current_user = request.user
    user_followers = user_to_follow.followers.all()

    if current_user in user_followers:
        user_to_follow.followers.remove(current_user.id)
        current_user.followings.remove(user_to_follow)
        return Response(
            {"message": f"You are not following "
                        f"{user_to_follow.username} anymore"}
        )

    user_to_follow.followers.add(current_user.id)
    current_user.followings.add(user_to_follow.id)
    return Response(data={"message": f"You are following "
                                     f"{user_to_follow.username}"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_unlike(request, pk):
    """Users can like & unlike posts"""
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
    return Response(
        {"message": "You liked this post"},
        status=status.HTTP_201_CREATED
    )


class CommentViewSet(viewsets.ModelViewSet):
    """Users can create comments and see all other comments on the post"""
    queryset = Comment.objects.select_related("author", "post")
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        return self.queryset.filter(post=post)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        serializer.save(author=self.request.user, post=post)
