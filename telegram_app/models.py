from django.db import models

# Create your models here.


class BotUser(models.Model):
    user_id = models.CharField(max_length=200)
    is_driver = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=200)
    state = models.CharField(max_length=200, blank=True, null=True)
    lang = models.CharField(max_length=2, blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"User {self.user_id} {'Driver' if self.is_driver else 'Passenger'}"


class TelegramGroup(models.Model):
    title = models.CharField(max_length=200)
    chat_id = models.IntegerField()

    def __str__(self):
        return f"{self.title}"


class Road(models.Model):
    road_name = models.CharField(max_length=200)
    group = models.ForeignKey(TelegramGroup, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.road_name


class RoadTranslation(models.Model):
    road = models.ForeignKey(
        Road, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=2)
    translated_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.road} - {self.language}"


class RidePost(models.Model):
    ordered_by = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    accepted_by = models.ForeignKey(
        BotUser, on_delete=models.CASCADE, null=True, blank=True, related_name="accepted_by")
    description = models.TextField()
    posted_on_group = models.ForeignKey(
        TelegramGroup, on_delete=models.CASCADE, null=True, blank=True, related_name="posted_on_group")
    is_active = models.BooleanField(default=True)

    group_message_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"RidePost {self.id} Ordered by User {self.ordered_by.user_id}"


class SmmPost(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    status = models.BooleanField()
    post_every_minute = models.IntegerField()
    photo = models.ImageField(upload_to="smm/")
    groups = models.ManyToManyField(TelegramGroup)
    date_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class TelegramBot(models.Model):
    username = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.username}"
