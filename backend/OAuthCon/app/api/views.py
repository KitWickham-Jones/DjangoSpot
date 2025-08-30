from django.shortcuts import redirect
from django.http import HttpResponse , JsonResponse
from django.views import View
import os
import base64
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode

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
			return HttpResponse(data.get('access_token'))
		except Exception as e:
			return HttpResponse(f"Error in Callback: {str(e)}", status=500)
	
class spotifyRecentPlays(View):
	def get(self,request):
		try:	
			url = 'https://api.spotify.com/v1/me/player/recently-played'
			headers = {
				'Authorization' : 'Bearer ' + request.session['access_token']
			}
			resp = requests.get(url=url, headers=headers)
			data = resp.json()
			songArtist = []
			for i in range(0, len(data['items'])):
				artist = data['items'][i]['track']['artists'][0]['name']
				song = data['items'][i]['track']['name']
				songArtist.append({
					'Artist' : artist,
					'Song' : song
				})
			return JsonResponse({'songs': songArtist})
		except Exception as e:
			return HttpResponse(f"Error in getting recently played: {str(e)}",status=500)