from django.db import models
from django.contrib.postgres.fields import ArrayField
# Create your models here.
class Artist(models.Model):
	artist_name = models.CharField(max_length=50, unique=True)
	artist_id = models.CharField(max_length=50, unique=True)

class listenData(models.Model):
	artist_name = models.ForeignKey(Artist, on_delete=models.CASCADE)
	song_id = models.CharField(max_length=50)
	time = models.DateTimeField()

class genreData(models.Model):
	artist_name = models.ForeignKey(Artist, on_delete=models.CASCADE),
	genres = ArrayField(models.CharField(max_length=50))