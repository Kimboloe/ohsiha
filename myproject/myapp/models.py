from django.db import models

import json
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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
