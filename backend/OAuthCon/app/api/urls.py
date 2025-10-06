from django.urls import path
from .views import SpotifyCallback, SpotifyLogin, SpotifyRecentPlays
urlpatterns = [
	path('login/', SpotifyLogin.as_view(), name='spotify-login'),
	path('callback/', SpotifyCallback.as_view(), name = 'spotify-callback'),
	path('recentPlay/', SpotifyRecentPlays.as_view(), name = 'spotify-recentPlay'),
	# path('genres' , SpotifySongGenres.as_view(), name = 'spotify-genres')
]