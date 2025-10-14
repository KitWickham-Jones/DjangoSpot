from django.urls import path
from .views import SpotifyCallback, SpotifyLogin, SpotifyRecentPlays, SpotifyArtistGenres, SpotifyReadDatabase
urlpatterns = [
	path('login/', SpotifyLogin.as_view(), name='spotify-login'),
	path('callback/', SpotifyCallback.as_view(), name = 'spotify-callback'),
	path('recentPlay/', SpotifyRecentPlays.as_view(), name = 'spotify-recentPlay'),
	path('genres/' , SpotifyArtistGenres.as_view(), name = 'spotify-genres'),
	path('readDB/', SpotifyReadDatabase.as_view(), name = 'spotify-read-db')
]