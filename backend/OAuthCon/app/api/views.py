from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
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

			return render(request, 'navigate.html', {'success_message': 'Successfully logged in'})
		except Exception as e:
			return render(request, 'navigate.html', {'error_message' : f"Error in Callback: {str(e)}"}, status=500)
		
class SpotifyRecentPlays(View):
	def get(self, request):
		try:
			#failed on 4am kru, look into this and hallow?
			token = request.session.get('access_token')
			if not token:
				return render(request, 'navigate.html', {'error_message': 'No access token located you need to log in'})	
			#TODO This needs testing and probably needs to move to the service layer
			resp = SpotifyAPIService.getRecentPlays(token)
			if resp.status_code == 401:
				retry_token = request.session.get('refresh_token')
				if not retry_token:
					return render(request, 'navigate.html',{'error_message' : 'No refresh token located you need to log in'} )
				retry_resp = SpotifyAPIService.useRefreshToken(retry_token)
				if retry_resp.status_code == 200:
					data = retry_resp.json()
					request.session['access_token'] = data.get('access_token')
					request.session['refresh_token'] = data.get('refresh_token')
					return redirect('http://127.0.0.1:8000/api/recentPlay/')
			
			if resp.status_code != 200:
				raise Exception("Invalid response from request")
			
			data = SpotifyAPIService.parseSongData(resp.json())
			success, message = SpotifyDataService.writeSongs(data)

			if not success:
				raise Exception(message)

			return render(request, 'navigate.html', {'success_message': 'Successfully added to db'})
		except Exception as e:
			return render(request, 'navigate.html', {'error_message' : f"Error in getting recent plays: {str(e)}"}, status=500)
		
class SpotifyArtistGenres(View):
	def get(self, request):
		try:
			token = request.session.get('access_token')
			if not token:
				raise Exception("No access token in session variables")
			
			data = SpotifyDataService.getArtistIds()
			if not data:
				raise Exception("No data read out of db")
			#could split genres into multiple calls and handle thatrather than just linit to 50 
			resp = SpotifyAPIService.getArtistGenres(token, data)

			data = SpotifyAPIService.parseGenreData(resp.json())

			success, message = SpotifyDataService.writeGenres(data)

			if not success:
				raise Exception(message)
			
			
			return render(request, 'navigate.html', {'success_message': f'Successfully added to db{str(data)}'})

		except Exception as e:
			return render(request, 'navigate.html', {'error_message': f"Error in getting genres: {str(e)}"})

class SpotifyReadDatabase(View):
	def get(self, request):
		try:
			method = request.GET.get('method')
			if not method:
				raise Exception("No database method provided in request")
			match method:
				case "readGenres":
					data = SpotifyDataService.readGenres()
				case "readSongGenres":
					data = SpotifyDataService.readSongGenre()
				case "readArtists":
					data = SpotifyDataService.readArtists()
				case _:
					raise Exception("Unknown method provided")
	
			return JsonResponse({'data' : data})

		except Exception as e:
			return render(request, 'navigate.html', {'error_message': f"Error in getting genres: {str(e)}"}, status=500)
