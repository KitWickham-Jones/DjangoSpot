from django.shortcuts import redirect
from django.http import HttpResponse , JsonResponse
from django.views import View
from django.db import IntegrityError
import os
import base64
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode
from .models import listenData, Artist,genreData

# Create your views here.

load_dotenv()

class spotifyLogin(View):
	def get(self, request):
		try:	
			url = 'https://accounts.spotify.com/authorize?'
			params = {
				'response_type':'code',
				'client_id' : os.getenv('CLIENT_ID'),
				'redirect_uri': 'http://127.0.0.1:8000/api/callback',
				'scope' : 'user-read-recently-played'
			}
			return redirect(url + urlencode(params))
		except Exception as e:
			return HttpResponse(f"Error:  {str(e)}", status=500)

class spotifyCallback(View):
	def get(self,request):
		try:	
			code = request.GET.get('code')
			if not code:
				return HttpResponse("Missing Auth Code during callback")
			redirect_uri = 'http://127.0.0.1:8000/api/callback'
			auth_str = f'{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}'
			b64_encode = base64.b64encode(auth_str.encode()).decode()
			data = {
				'grant_type':'authorization_code',
				'code':code,
				'redirect_uri': redirect_uri
			}
			headers = {
				'Authorization': f'Basic {b64_encode}',
				'Content-Type' : 'application/x-www-form-urlencoded'
			}
			resp = requests.post('https://accounts.spotify.com/api/token', data = data, headers=headers)
			if resp.status_code != 200:
				return HttpResponse('Error generating access token')
			data = resp.json()
			request.session['access_token'] = data.get('access_token')
			return HttpResponse(resp)
		except Exception as e:
			return HttpResponse(f"Error in Callback: {str(e)}", status=500)
	
class spotifyRecentPlays(View):
	def get(self,request):
		try:	
			url = 'https://api.spotify.com/v1/me/player/recently-played'
			params = {
				'limit' : 50
			}
			
			headers = {
				'Authorization' : 'Bearer ' + request.session['access_token']
			}
			resp = requests.get(url=url ,params=params, headers=headers)
			if resp.status_code != 200:
				return HttpResponse('check access token!')
			data = resp.json()
			songArtist = []
			for item in data['items']:
				artist = item['track']['artists'][0]['name']
				artist_id = item['track']['artists'][0]['id']
				song = item['track']['name']
				played_at = item['played_at']
				try:
					key , _ = Artist.objects.get_or_create(
						artist_name = artist,
						artist_id = artist_id
						)
					listenData.objects.create(
						artist_name=key,
						song_id=song,
						time = played_at
					)
				except IntegrityError as ie:
					return HttpResponse(f"Error during insertion into database: {str(ie)}", status =500)			
				songArtist.append({
					'Artist' : artist,
					'Artist_id': artist_id,
					'Song' : song,
					'Played' : played_at
				})
			return JsonResponse({'songs': songArtist})
		except Exception as e:
			return HttpResponse(f"Error in getting recently played: {str(e)}",status=500)
		
# class spotifySongGenres(View):
# 	def get(self, request):
# 		try: