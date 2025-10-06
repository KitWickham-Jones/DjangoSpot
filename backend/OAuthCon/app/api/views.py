from django.shortcuts import redirect, render
from django.http import HttpResponse 
from django.views import View

from .SpotifyService import SpotifyAPIService,SpotifyDataService

# Create your views here.
class SpotifyLogin(View):
	def get(self,request):
		try:
			url = SpotifyAPIService.getAuthURL()
			return redirect(url)
		except Exception as e:
			return HttpResponse(f"Error in getting url: {str(e)}", status = 500 ) 
		
class SpotifyCallback(View):
	def get(self, request):
		try:
			code = request.GET.get('code')
			if not code:
				raise Exception("Missing code from callback URL")
			
			resp = SpotifyAPIService.getAccessToken(code)

			if resp.status_code != 200:
				raise Exception("error during getting access token")
			
			data = resp.json()
			request.session['access_token'] = data.get('access_token')
			request.session['refresh_token'] = data.get('refresh_token')

			return render(request, 'navigate.html')
		except Exception as e:
			return render(request, 'navigate.html', {'error_message' : f"Error in Callback: {str(e)}"}, status=500)
		
class SpotifyRecentPlays(View):
	def get(self, request):
		try:
			token = request.session['access_token'] 
			if not token:
				raise Exception("No access token in session variables")
			
			resp = SpotifyAPIService.getRecentPlays(token)

			#TODO handle refreshing, if code is like out of time
			if resp.status_code != 200:
				raise Exception("Invalid response from request")
			
			data = SpotifyAPIService.parseSongData(resp.json())
			success, message = SpotifyDataService.writeSongs(data)

			if not success:
				raise Exception(message)

			return HttpResponse(str(success))

		except Exception as e:
			return render(request, 'navigate.html', {'error_message' : f"Error in getting recent plays: {str(e)}"})