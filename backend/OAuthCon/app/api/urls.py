from django.urls import path
from .views import spotifyCallback, spotifyLogin,spotifyRecentPlays

urlpatterns = [
	path('login/', spotifyLogin.as_view(), name='spotify-login'),
	path('callback/', spotifyCallback.as_view(), name = 'spotify-callback'),
	path('recentPlay/', spotifyRecentPlays.as_view(), name = 'spotify-recentPlay')
]