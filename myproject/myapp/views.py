from django.http import HttpResponse, Http404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect

import io
import json
import requests
import spotipy
import csv
import pandas as pd
from bs4 import BeautifulSoup

from spotipy.oauth2 import SpotifyClientCredentials
from myapp.models import Spotify_data, Song

def main_page(request):

    #koska spotify apissa on puutteita, pitää hakea csv-tiedosto erikseen
    result = requests.get('https://spotifycharts.com/regional/fi/daily/latest/download')
    #result = requests.get('https://spotifycharts.com/viral/global/daily/latest/download', verify=False)

    decoded_content = result.content.decode('utf-8')

    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    top_list = list(cr)
    top_list.remove(top_list[0])
    top_ten = []

    count = 0

    for row in top_list:
        if count == 10:
            break
        inner_count = 0
        d = {}

        for i in row:
            if inner_count == 1:
                d['Song'] = i
            elif inner_count == 2:
                d['Artist'] = i
            elif inner_count == 3:
                d['Streams'] = i
            elif inner_count == 4:
                d['URL'] = 'https://open.spotify.com/embed?uri=' + i

            inner_count +=1

        top_ten.append(d.copy())
        count +=1

    s = Spotify_data.objects.get(name='test_data')
    songs = s.songs.all()
    login_form = AuthenticationForm(request.POST)

    #for genius api----------
    #client_id = p02kVfs2YI-67OpOf29arN85zlcefNmOJqjBBUt8GJEIDqpDqW9ySP5826GvN9mZ
    #clien_secret = NeIcXb8HwY8uwLY0mgRGMRZLmx6TKAaiGX0jWLQAI99aMtHl85JJDTyyipNnOH82NbqLRWEyOsS1VCyYipRwMA
    #TOKEN = 'K3wQde3GVmf0rJ4owosGyEAOJnCqo4e2hslPlNld-w8dQBxg9NZj8AXYZXipapwv'

    headers = {'Authorization': 'Bearer K3wQde3GVmf0rJ4owosGyEAOJnCqo4e2hslPlNld-w8dQBxg9NZj8AXYZXipapwv'}
    base_url = "http://api.genius.com"

    song_title = None
    artist_name = None
    #song_title = top_ten[0]['Song']
    #artist_name = top_ten[0]['Artist']

    def lyrics_from_song_api_path(song_api_path):
        song_url = base_url + song_api_path
        response = requests.get(song_url, headers=headers)
        json = response.json()
        path = json["response"]["song"]["path"]
        #gotta go regular html scraping... come on Genius
        page_url = "http://genius.com" + path
        page = requests.get(page_url)
        html = BeautifulSoup(page.text, "html.parser")
        #remove script tags that they put in the middle of the lyrics
        [h.extract() for h in html('script')]
        #at least Genius is nice and has a tag called 'lyrics'!
        lyrics = html.find('div', class_='lyrics').get_text() #updated css where the lyrics are based in HTML
        return lyrics

    for song in top_ten:

        song_title = song['Song']
        artist_name = song['Artist']

        search_url = base_url + "/search"
        data = {'q': song_title}
        response = requests.get(search_url, params=data, headers=headers)
        json = response.json()
        song_info = None
        for hit in json["response"]["hits"]:
            if hit["result"]["primary_artist"]["name"] == artist_name:
                song_info = hit
                break
        if song_info:
            song_api_path = song_info["result"]["api_path"]
            lyrics = lyrics_from_song_api_path(song_api_path)
            print(lyrics)


    client_id = '2e68207dbeb34b78a1daad0e399afd98'
    client_secret = 'a3649535f746487fa955afb2fbad4cce'

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    '''
    result = sp.categories(country='FI', locale=None, limit=20, offset=0)

    for count,i in enumerate(result['categories']['items']):
        print(count)
        for j in i:
            print(j, ' : ',i[j])
        #print(result['categories']['items'][i])
        print()
    '''


    result = sp.category_playlists(category_id='toplists', country='FI', limit=20, offset=0)

    #print(result)

    '''for count,i in enumerate(result['playlists']['items']):
        print(count)
        for j in i:
            print(j, ' : ',i[j])
        #print(result['categories']['items'][i])
        print()'''

    return render(request, 'base.html', {'songs' : songs, 'login_form': login_form, 'top_tracks': top_ten})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login(request):
    return render(request, 'registration/login.html', {})

def logout(request):
    return render(request, 'registration/logout.html', {})
