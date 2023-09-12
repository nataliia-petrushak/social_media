from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Post, Hashtag, Comment, ScheduledPost


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "bio",
            "image"
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserListSerializer(UserSerializer):
    followers = serializers.IntegerField(source="followers.count", read_only=True)
    followings = serializers.IntegerField(source="followings.count", read_only=True)
    posts = serializers.IntegerField(source="posts.count", read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "image",
            "posts",
            "followers",
            "followings",
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "content", "created_at")


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name")


class HashtagListSerializer(HashtagSerializer):
    posts = serializers.IntegerField(source="posts.count", read_only=True)

    class Meta:
        model = Hashtag
        fields = ("id", "name", "posts")


class ScheduledPostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    hashtags = HashtagSerializer(many=True, required=False)

    class Meta:
        model = ScheduledPost
        fields = (
            "id",
            "title",
            "author",
            "content",
            "created_at",
            "image",
            "hashtags",
        )
        read_only_fields = ("id", "author")


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    hashtags = HashtagSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "content",
            "created_at",
            "image",
            "hashtags",
        )
        read_only_fields = ("id", "author")


class PostListSerializer(PostSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    hashtags = serializers.SlugRelatedField(
        many=True, slug_field="name", read_only=True
    )
    likes = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.BooleanField(read_only=True)
    comments = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "image",
            "hashtags",
            "likes",
            "comments",
            "is_liked",
        )


class ScheduledPostListSerializer(ScheduledPostSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    hashtags = serializers.SlugRelatedField(
        many=True, slug_field="name", read_only=True
    )

    class Meta:
        model = ScheduledPost
        fields = (
            "id",
            "title",
            "author",
            "image",
            "hashtags",
        )


class HashtagDetailSerializer(HashtagSerializer):
    posts = PostListSerializer(read_only=True, many=True)

    class Meta:
        model = Hashtag
        fields = ("id", "name", "posts")


class UserDetailSerializer(UserSerializer):
    followers = UserListSerializer(many=True, read_only=True)
    followings = UserListSerializer(many=True, read_only=True)
    posts = PostListSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "bio",
            "image",
            "posts",
            "followers",
            "followings",
        )
        read_only_fields = ("is_staff",)


class PostDetailSerializer(PostSerializer):
    author = UserListSerializer(many=False, read_only=True)
    hashtags = serializers.SlugRelatedField(
        slug_field="name", many=True, read_only=True
    )
    comments = CommentSerializer(many=True, read_only=True)
    likes = serializers.IntegerField(source="likes.count", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "author",
            "image",
            "hashtags",
            "created_at",
            "likes",
            "comments",
        )


class ScheduledPostDetailSerializer(ScheduledPostSerializer):
    author = UserListSerializer(many=False, read_only=True)
    hashtags = serializers.SlugRelatedField(
        slug_field="name", many=True, read_only=True
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "author",
            "image",
            "hashtags",
            "created_at",
        )
