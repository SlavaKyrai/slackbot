from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class WorkSpace(models.Model):
    team_id = models.CharField(max_length=15, unique=True)
    team_name = models.CharField(max_length=150)
    bot_user_id = models.CharField(max_length=15)
    bot_access_token = models.CharField(max_length=150)
    user_admin = models.ForeignKey(User)
    moderators = models.ManyToManyField(User, blank=True, related_name='moders')
    announcing_channel_name = models.CharField(max_length=100, null=True)  # канал, в который будут слаться сообщения

    def __str__(self):
        return self.team_name


class LeaveMessageAsk(models.Model):
    user_name = models.CharField(max_length=100)
    user_id = models.CharField(max_length=20)
    ts = models.CharField(max_length=50)
    channel_id = models.CharField(max_length=40)
    message_text = models.TextField()
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE)

    def __str__(self):
        return self.user_name + ": " + self.message_text[:20]


class LeaveMessageResponse(models.Model):
    user_id = models.CharField(max_length=100)
    ts = models.CharField(max_length=50)
    message_text = models.TextField()
    leave_messake_ask = models.ForeignKey(LeaveMessageAsk, on_delete=models.CASCADE)

    def __str__(self):
        return self.user_id + ": " + self.message_text[:20]
