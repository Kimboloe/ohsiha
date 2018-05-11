from django.db import models
from django.utils import timezone

import io
import json
import requests
import spotipy
import csv
import pandas as pd
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyCharts(models.Model):
    country = models.CharField(max_length=255)
    #this can be set to 'global'
    country_code = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)

    def read_data(self):

        url_begin = 'https://spotifycharts.com/regional/'
        url_end = '/weekly/latest/download'
        url = url_begin + self.country_code + url_end

        result = requests.get(url)
        decoded_content = result.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        top_list = list(cr)
        top_list.remove(top_list[0]) #poistaa csv-tiedoston alusta turhan rivin
        count = 0

        song_name = "None"
        artist_name = "None"
        streams = 0
        URL = "None"

        for row in top_list:

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

            song = Song(name=song_name, artist=artist_name, streams=streams, iframe_url=URL, spotify_charts=self)
            song.save()
            count +=1

class Song(models.Model):
    name = models.CharField(max_length=255, null=True)
    artist = models.CharField(max_length=255, null=True)
    streams = models.PositiveIntegerField(null=True)
    iframe_url = models.URLField(null=True)
    lyrics = models.TextField(null=True)
    spotify_charts = models.ForeignKey("SpotifyCharts", on_delete=models.CASCADE, related_name="songs", null=True)

    def get_lyrics(self):
        headers = {'Authorization': 'Bearer K3wQde3GVmf0rJ4owosGyEAOJnCqo4e2hslPlNld-w8dQBxg9NZj8AXYZXipapwv'}
        base_url = "http://api.genius.com"

        song_title = self.name
        artist_name = self.artist

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
            self.lyrics = lyrics
            self.save()

class Comment(models.Model):
    #username or anonymous
    user = models.CharField(max_length=255, null=True)
    comment = models.TextField(null=True)
    date = models.DateTimeField(default=timezone.now)
