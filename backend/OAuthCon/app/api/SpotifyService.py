import os
import base64
from dotenv import load_dotenv
from urllib.parse import urlencode
from .models import ArtistData, ListenData, GenreData
from typing import List, Tuple, Optional
import requests

#Service class to handle spotify API logic

load_dotenv()

class SpotifyAPIService:
	
	auth_str = f"{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}"
	b64_encode = base64.b64encode(auth_str.encode()).decode()

	@staticmethod
	def getAuthURL() -> str:
		""" Get authentication URL"""
		url = 'https://accounts.spotify.com/authorize?'
		params = {
			'response_type':'code',
			'client_id' : os.getenv('CLIENT_ID'),
			'redirect_uri': 'http://127.0.0.1:8000/api/callback',
			'scope' : 'user-read-recently-played'
		}
		return url + urlencode(params)
	
	@staticmethod
	def getAccessToken(code: str) -> requests.Response:
		"""Get user access token"""
		redirect_uri = 'http://127.0.0.1:8000/api/callback'	
		data = {
			'grant_type':'authorization_code',
			'code':code,
			'redirect_uri': redirect_uri
		}
		headers = {
			'Authorization': f'Basic {SpotifyAPIService.b64_encode}',
			'Content-Type' : 'application/x-www-form-urlencoded'
		}
		return requests.post('https://accounts.spotify.com/api/token', data = data, headers=headers)

	@staticmethod
	def useRefreshToken(refresh_token : str) -> requests.Response:
		headers = {
			'Authorization' : f"Basic {SpotifyAPIService.b64_encode}",
			'Content-Type' : 'application/x-www-form-urlencoded'
		}
		data = {
			'grant_type' : 'refresh_token',
			'refresh_token' : refresh_token
		}
		return requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)

	@staticmethod
	def getRecentPlays(accessToken : str, limit : int=50) -> requests.Response:
		"""Get user recently played songs"""
		url = 'https://api.spotify.com/v1/me/player/recently-played'
		params = {
			'limit' : limit
		}
		headers = {
			'Authorization' : 'Bearer ' + accessToken
		}
		return requests.get(url=url, params=params, headers=headers)
	
	@staticmethod
	def getArtistGenres(accessToken : str , artist_ids: str) -> requests.Response:
		"""Get genre information about given artist"""
		url = 'https://api.spotify.com/v1/artists'
		#Only works up to 50
		artist_ids = ','.join(artist_ids[0:49])
		params = {
			'ids': artist_ids
		}
		headers = {
			'Authorization' : 'Bearer ' + accessToken
		}
		return requests.get(url=url, params=params, headers=headers)

	@staticmethod
	def parseGenreData(data : dict) -> list:
		dataList = []
		for item in data['artists']:
			genre = item['genres']
			artist_name = item['name']
			dataList.append({
				'artist_name' : artist_name,
				'genre' : genre
			})
		return dataList

	@staticmethod
	def parseSongData(data : dict) -> list:
		dataList = []
		for item in data['items']:
			artist = item['track']['artists'][0]['name']
			artist_id = item['track']['artists'][0]['id']
			song = item['track']['name']
			played_at = item['played_at']
			dataList.append({
				'artist' : artist,
				'artist_id' : artist_id,
				'song' : song,
				'played_at' : played_at
			})
		return dataList

 
class SpotifyDataService:
	@staticmethod
	def writeSongs(data : list) -> Tuple[bool, Optional[str]]:
		try:	
			#Identify all existing artists in db
			artistNames = [item['artist'] for item in data]
			existing_artists = {artist.artist_name : artist for artist in 
						ArtistData.objects.filter(artist_name__in = artistNames)}
		
			artists_to_create = []
			#check not in db or append to list that is going to be bulk inserted
			for item in data:
				if item['artist'] not in existing_artists:
					artists_to_create.append(
						ArtistData(artist_name = item['artist'], artist_id = item['artist_id'])
					)

			if artists_to_create:
				added_artists = ArtistData.objects.bulk_create(
					artists_to_create,
					ignore_conflicts=True
				)
				#update existing inDB? dictionary 
				for artist in added_artists:
					existing_artists[artist.artist_id] = artist
			#add song data, need the artist obejct which we have in inDB? dict
			listen_objects = []
			for item in data:
				artist = existing_artists[item['artist']]
				listen_objects.append(
					ListenData(
						artist_name = artist,
						song_id = item['song'],
						time = item['played_at']
					)
				)

			if listen_objects:
				ListenData.objects.bulk_create(listen_objects)

			return True, None
		except Exception as e:
			return False, str(e)

	@staticmethod
	#does this need a limit? could just take all then call genre api multiple times
	def getArtistIds(limit : int = 50 ) -> list:
		return  [artist.artist_id for artist in ArtistData.objects.order_by('-id')[:limit]]

	@staticmethod
	def writeGenres(data : list):
		try:	
			artist_names = [name['artist_name'] for name in data]
			artist_objs = {artist.artist_name : artist for artist
					in ArtistData.objects.filter(artist_name__in=artist_names)}

			genre_objects = []
			for item in data:
				artist = artist_objs[item["artist_name"]]
				#probably dont write empty genres
				if not item['genre']:
					continue
				genre_objects.append(
						GenreData(
							artist_name = artist,
							genres = item['genre']
						)
					)

			if genre_objects:
				GenreData.objects.bulk_create(genre_objects)

			return True, None
		except Exception as e:
			return False, str(e)

	@staticmethod
	def readSongGenre():		#get artist information
		#get song information
		#get genre information
		#every song and genre has an artist.val
		gm = {g.artist_name.artist_name : g.genres for g in GenreData.objects.select_related('artist_name').all()}
		listen = ListenData.objects.select_related('artist_name').all()
		outList = []
		for val in listen:
			outList.append({
				'song' : val.song_id,
				'artist_name' : val.artist_name.artist_name,
				'genres' : gm.get(val.artist_name.artist_name)

			})
		return outList

	@staticmethod
	def readGenres():
		return [g.genres for g in GenreData.objects.all()]
	
	@staticmethod
	def readArtists():
		return [a.artist_name for a in ArtistData.objects.all()]
	
class WolframAPIService:

	@staticmethod
	def postGenreData(genreData):
		url = "https://www.wolframcloud.com/obj/kitwj/WordCloudAPI"
		return requests.post(url=url, json = genreData)
	
