from django.http import HttpResponse, Http404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

import json
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from myapp.models import Spotify_data, Song

def main_page(request):

    s = Spotify_data.objects.get(name='test_data')
    songs = s.songs.all()

    return render(request, 'base.html', {'songs' : songs})

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
