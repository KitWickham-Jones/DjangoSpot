from django.shortcuts import redirect, render
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

auth_str = f'{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}'
b64_encode = base64.b64encode(auth_str.encode()).decode()

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
				render({'error_message' : f"Error generating access token: {str(e)}"}, status=500)
			data = resp.json()
			request.session['access_token'] = data.get('access_token')
			request.session['refresh_token'] = data.get('refresh_token')
			return render(request, 'navigate.html' )
		except Exception as e:
			# return HttpResponse(f"Error in Callback: {str(e)}", status=500)
			return render(request, 'navigate.html',{'error_message' : f"Error in Callback: {str(e)}"}, status=500 )
	
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
				try:
					headers = {
						'Authorization': f'Basic {b64_encode}',
						'Content-Type' : 'application/x-www-form-urlencoded'
					}
					data = {
						'grant_type':'refresh_token',
						'refresh_token':request.session['refresh_token']
					}
					refresh  = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
					if refresh.status_code == 200:
						refresh = refresh.json()
						request.session['access_token'] = refresh.get('access_token')
						request.session['refresh_token'] = refresh.get('refresh_token')
						return redirect('http://127.0.0.1:8000/api/recentPlay/')
				except Exception as e:
					return render(request, 'navigate.html',{'error_message' : f"Error whilst using refresh token! : {str(e)}"}, status=500 )
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
			return render(request, 'navigate.html',{'error_message' : f"Error in getting recently played : {str(e)}"}, status=500 )

		
class spotifySongGenres(View):
	def get(self, request):
		try:
			url = 'https://api.spotify.com/v1/artists'
			artists = Artist.objects.all()
			# data = [{'artist_name': a.artist_name, 'artist_id': a.artist_id} for a in artists]
			ids = [f",{a.artist_id}" for a in artists]
			ids = ''.join(ids)
			ids = ids[1:]
			params = {
				'ids': ids
			}
			headers = {
				'Authorization' : 'Bearer ' + request.session['access_token']
			}
			resp = requests.get(url, params=params, headers=headers)
			resp = resp.json()
			artGenre = []
			for item in resp['artists']:
				artGenre.append({
					'Artist' : item['name'],
					'Genres': item['genres']
					})	
			return JsonResponse({'Genre info: ': artGenre })
		except Exception as e:
			return HttpResponse(f'error :{str(e)}')