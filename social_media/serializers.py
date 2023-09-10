from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Post, Hashtag, Comment, Like


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_staff",
            "bio",
            "image",
        )
        read_only_fields = ("is_staff",)
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
            "first_name",
            "last_name",
            "image",
            "posts",
            "followers",
            "followings",
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "content", "created_at")


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

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