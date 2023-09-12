from .publish_delayed_posts import save_posts
from celery import shared_task


@shared_task
def run_sync_with_api():
    save_posts()
