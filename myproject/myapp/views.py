from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
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
from django.utils import timezone

from spotipy.oauth2 import SpotifyClientCredentials
from myapp.models import SpotifyCharts, Song, Comment

def main_page(request, country_code="global"):

    file = open('spotify_countries.json')
    countries = json.load(file)
    comments = Comment.objects.all().order_by("date")

    if country_code == None:
        country_code = "global"

    top_ten = get_top_ten(country_code)

    login_form = AuthenticationForm(request.POST)

    if request.method == 'GET' and request.is_ajax():

        data = dict(request.GET)
        first = next(iter(data.keys()))
        print(first)

        if first == 'Song':
            song = data['Song'][0]
            artist = data['Artist'][0]
            #call get_lyrics scraper
            lyrics = get_lyrics(song, artist)
            return HttpResponse(lyrics, content_type="text")

    if request.method == 'POST' and request.is_ajax():
        json_response = json.loads(request.body)
        if json_response["messageType"] == "comment":
            comment = json_response["comment"]
            user = json_response["user"]
            new_comment = Comment(user=user, comment=comment)
            new_comment.save()
            response = "< " + user + " >: " + comment
            return HttpResponse(response)

    return render(request, 'base.html', {'login_form': login_form,
     'top_tracks': top_ten , 'countries': countries, 'comments': comments})

def charts(request, country_code):
    song_info = []
    country = ""
    streams = []

    song_info_global = []
    streams_global = []

    chart1 = SpotifyCharts.objects.filter(country_code=country_code).order_by('date')[0]
    date, rest = chart1.date.strftime("%Y-%m-%d %H:%M:%S").split(" ")
    if not check_date(date):
        #outdated -> load new
        country = chart1.country
        new_chart = SpotifyCharts(country=country, country_code=country_code)
        new_chart.save()
        new_chart.read_data()
        chart1 = new_chart

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

    chart2 = SpotifyCharts.objects.filter(country_code="global").order_by('date')[0]
    date, rest = chart2.date.strftime("%Y-%m-%d %H:%M:%S").split(" ")
    if not check_date(date):
        #outdated -> load new
        country2 = chart2.country
        new_chart = SpotifyCharts(country=country2, country_code='global')
        new_chart.save()
        new_chart.read_data()
        chart2 = new_chart

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
            user = form.save()
            auth_login(request, user)
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

    #get latest chart from database
    chart = SpotifyCharts.objects.filter(country_code=country_code).order_by('date')[0]

    date, rest = chart.date.strftime("%Y-%m-%d %H:%M:%S").split(" ")

    if not check_date(date):
        #outdated -> load new
        country = chart.country
        new_chart = SpotifyCharts(country=country, country_code=country_code)
        new_chart.save()
        new_chart.read_data()
        chart = new_chart

    #get the top ten
    top_ten = []
    count = 0
    for song in chart.songs.all():
        d = {}
        if count == 10:
            break

        d['Song'] = song.name
        d['Artist'] = song.artist
        d['Streams'] = song.streams
        d['URL'] = song.iframe_url

        top_ten.append(d.copy())
        count += 1

    return top_ten

def get_lyrics(song, artist):
    #Scrape lyrics using genius api

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
    #return max twenty matching songs

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

def check_date(date):
    #return false if date is too old

    year, month, day = date.split("-")

    date2, rest = timezone.now().strftime("%Y-%m-%d %H:%M:%S").split(" ")
    year2, month2, day2 = date2.split("-")

    #this should be the case
    if year == year2:
        if month == month2:
            if int(day2) - int(day) >= 7:
                return False
            else:
                return True
        else:
            days = 30 - int(day) + int(day2)
            if days >= 7:
                return False
            else:
                return True
    else:
        print("how did we end up here")
        if int(month) == 12 and int(month2)==1:
            days = 30 - int(day) + int(day2)
            if days >= 7:
                return False
            else:
                return True
        else:
            return False
