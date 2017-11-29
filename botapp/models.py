from django.db import models


# Create your models here.
class WorkSpace(models.Model):
    team_id = models.CharField(max_length=15)
    team_name = models.CharField(max_length=150)
    bot_user_id = models.CharField(max_length=15)
    bot_access_token = models.CharField(max_length=150)

    def __str__(self):
        return self.team_name
