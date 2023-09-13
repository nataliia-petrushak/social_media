import logging
from django.utils import timezone
from .models import Post, ScheduledPost, Hashtag

logger = logging.getLogger(__name__)


def save_posts():
    time_now = timezone.now()
    scheduled_posts = ScheduledPost.objects.filter(created_at__lte=time_now)
    if scheduled_posts:
        for post in scheduled_posts:
            logger.info(f"Creating Post: {post.title}")
            new_post = Post.objects.create(
                title=post.title,
                content=post.content,
                author=post.author,
                image=post.image,
                created_at=post.created_at
            )
            hashtags = Hashtag.objects.filter(scheduled_posts=post)
            new_post.hashtags.set(hashtags)
            logger.info(f"Post Created: {new_post.title}")

            post.delete()
    else:
        logger.info("There is nothing to publish")
