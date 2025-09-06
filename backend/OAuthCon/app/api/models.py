from django.db import models

# Create your models here.
class listenData(models.Model):
	artist_id = models.CharField(max_length=50)
	song_id = models.CharField(max_length=50)