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
import pycountry

from spotipy.oauth2 import SpotifyClientCredentials
from myapp.models import SpotifyCharts, Song

def main_page(request):

    file = open('spotify_countries.json')
    countries = json.load(file)

    top_ten = get_top_ten("global")

    #s = Spotify_data.objects.get(name='test_data')
    #songs = s.songs.all()
    login_form = AuthenticationForm(request.POST)


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

    if request.method == 'GET' and request.is_ajax():

        data = dict(request.GET)
        first = next(iter(data.keys()))
        print(first)

        if first == 'Song':
            song = data['Song'][0]
            artist = data['Artist'][0]

            lyrics = get_lyrics(song, artist)
            print(song, " : ",artist)
            print(lyrics)

            return HttpResponse(lyrics, content_type="text")

        top_ten = get_top_ten(country_code)
        print(top_ten[0])
        asd = {"this is": "json"}
        response = json.dumps(top_ten)
        return HttpResponse(response, content_type="application/json")

    return render(request, 'base.html', {'login_form': login_form,
     'top_tracks': top_ten , 'countries': countries})

def charts(request, country_code):
    song_info = []
    country = ""
    streams = []

    song_info_global = []
    streams_global = []

    chart1 = SpotifyCharts.objects.get(country_code=country_code)

    country = chart1.country

    songs1 = chart1.songs.all()

    count = 0
    for i in songs1:
        if(count == 10):
            break
        song_name = i.name
        artist = i.artist
        song_streams = i.streams
        info = song_name + " by " + artist

        song_info.append(info)
        streams.append(song_streams)
        count +=1

    chart2 = SpotifyCharts.objects.get(country_code="global")

    songs2 = chart2.songs.all()

    count = 0
    for i in songs2:
        if(count == 10):
            break
        song_name = i.name
        artist = i.artist
        song_streams = i.streams
        info = song_name + " by " + artist

        song_info_global.append(info)
        streams_global.append(song_streams)
        count +=1

    matches = get_matching_songs(chart1, chart2)

    return render(request, 'charts.html', {'country_code': country_code, 'song_info': song_info,
     'streams': streams, 'country': country, 'song_info_global': song_info_global,
     'streams_global': streams_global, 'matches': matches})

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

# helper functions

def get_top_ten(country_code):

    url_begin = 'https://spotifycharts.com/regional/'
    url_end = '/daily/latest/download'
    url = url_begin + country_code + url_end
    #koska spotify apissa on puutteita, pitää hakea csv-tiedosto erikseen
    result = requests.get(url)
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
    return top_ten

def get_lyrics(song, artist):

    #for genius api----------
    #client_id = p02kVfs2YI-67OpOf29arN85zlcefNmOJqjBBUt8GJEIDqpDqW9ySP5826GvN9mZ
    #clien_secret = NeIcXb8HwY8uwLY0mgRGMRZLmx6TKAaiGX0jWLQAI99aMtHl85JJDTyyipNnOH82NbqLRWEyOsS1VCyYipRwMA
    #TOKEN = 'K3wQde3GVmf0rJ4owosGyEAOJnCqo4e2hslPlNld-w8dQBxg9NZj8AXYZXipapwv'

    headers = {'Authorization': 'Bearer K3wQde3GVmf0rJ4owosGyEAOJnCqo4e2hslPlNld-w8dQBxg9NZj8AXYZXipapwv'}
    base_url = "http://api.genius.com"

    song_title = song
    artist_name = artist

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
        return lyrics
    return lyrics

def get_matching_songs(chart1, chart2):

    songs1 = chart1.songs.all()
    songs2 = chart2.songs.all()

    return_list = []

    matching_songs = []
    streams_country = []
    streams_global = []

    count = 0

    for i in songs1:
        if count == 20:
            break
        song_name = i.name
        artist = i.artist
        song_streams = i.streams
        song_streams_global = 0
        for j in songs2:
            if j.name == song_name and j.artist == artist:
                song_streams_global = j.streams
                info = song_name + "by" + artist
                matching_songs.append(info)
                streams_country.append(song_streams)
                streams_global.append(song_streams_global)
                count += 1
                break


    return_list.append(matching_songs)
    return_list.append(streams_country)
    return_list.append(streams_global)

    return return_list
