from celery import shared_task

from .models import SmmPost, TelegramGroup
from .utils import BotService


@shared_task
def send_smm_posts():
    botService = BotService()
    active_posts = SmmPost.objects.filter(status=True)

    for post in active_posts:
        groups = post.groups.all()
        photo_url = "https://b3a8-84-54-120-76.ngrok-free.app" + post.photo.url
        caption = f"{post.title}\n\n{post.body}"

        for group in groups:
            payload = {
                "chat_id": group.chat_id,
                "photo": photo_url,
                "caption": caption
            }
            response = botService.send_photo(payload)
