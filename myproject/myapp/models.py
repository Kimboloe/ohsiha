from django.db import models

import io
import json
import requests
import spotipy
import csv
import pandas as pd
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials

class Top_ten(models.Model):
    location = models.CharField(max_length=255)

    def read_data(self):

        result = requests.get('https://spotifycharts.com/regional/fi/daily/latest/download')
        decoded_content = result.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        top_list = list(cr)
        top_list.remove(top_list[0]) #poistaa csv-tiedoston alusta turhan rivin
        count = 0

        song_name = None
        artist_name = None
        streams = None
        URL = None

        for row in top_list:
            if count == 10:
                break
            inner_count = 0

            for i in row:
                if inner_count == 1:
                    song_name = i
                elif inner_count == 2:
                    artist_name = i
                elif inner_count == 3:
                     streams = i
                elif inner_count == 4:
                    URL = 'https://open.spotify.com/embed?uri=' + i

                inner_count +=1


            headers = {'Authorization': 'Bearer TOKEN'}
            base_url = "http://api.genius.com"

            song_title = song_name
            artist_name = artist_name

            def lyrics_from_song_api_path(song_api_path):
                song_url = base_url + song_api_path
                response = requests.get(song_url, headers=headers)
                json = response.json()
                path = json["response"]["song"]["path"]
                page_url = "http://genius.com" + path
                page = requests.get(page_url)
                html = BeautifulSoup(page.text, "html.parser")
                #remove script tags
                [h.extract() for h in html('script')]
                #luckily there is a tag called lyrics
                lyrics = html.find('div', class_='lyrics').get_text()
                return lyrics

            search_url = base_url + "/search"
            data = {'q': song_title}
            response = requests.get(search_url, params=data, headers=headers)
            json = response.json()
            song_info = None
            lyrics = None
            for hit in json["response"]["hits"]:
                if hit["result"]["primary_artist"]["name"] == artist_name:
                    song_info = hit
                    break
            if song_info:
                song_api_path = song_info["result"]["api_path"]
                lyrics = lyrics_from_song_api_path(song_api_path)

            song = Top_Song(name=song_name, artist=artist_name, streams=streams, iframe_url=URL, lyrics=lyrics, top_ten=self)
            song.save()
            count +=1


class Top_Song(models.Model):
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    streams = models.PositiveIntegerField()
    iframe_url = models.URLField()
    lyrics = models.TextField(null=True)
    top_ten = models.ForeignKey("Top_ten", on_delete=models.CASCADE, related_name="top_songs", null=True)

class Spotify_data(models.Model):

    name = models.CharField(max_length=255)

    def read_data(self):
            client_id = 'CLIENT_ID'
            client_secret = 'CLIENT_SECRET'

            client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

            sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

            result = sp.search(q='Radiohead', limit=10)
            response = []
            for i in result['tracks']['items']:
                name = i['name']
                uri = ''
                iframe_url = 'https://open.spotify.com/embed?uri='

                for k in i:
                    if k == 'uri':
                        uri = i[k]
                        iframe_url = iframe_url + uri
                song = Song(name=name, uri=uri, iframe_url=iframe_url, spotify_data=self)
                song.save()

class Song(models.Model):

    name = models.CharField(max_length=255)
    uri = models.URLField()
    iframe_url = models.URLField()
    spotify_data = models.ForeignKey("Spotify_data", on_delete=models.CASCADE, related_name="songs", null=True)


class Artist(models.Model):
    pass
