from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators  import login_required
import requests
from bs4 import BeautifulSoup as bs
import re

# Create your views here.
def top_artist():

  url = "https://spotify-scraper.p.rapidapi.com/v1/chart/artists/top"

  headers = {
    "X-RapidAPI-Key": "4b32350c31msh3283e91ec63afe3p1a7c4djsn0219f3a63597",
    "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
  }
  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response_data = response.json()

    artists_info = []

    if 'artists' in response_data:
      shortened_data = response_data['artists'][:10]
      for artist in shortened_data['artists']:
        name = artist.get('name','No Name')
        artist_id = artist.get('id',"No ID")
        avatar_url = artist.get('visuals',{}).get('avatar',[{}])[0].get('url','No url')

        artists_info.append((name,avatar_url,artist_id))
    else:
      print('No Artists data')
      artists_info=[]
  except requests.exceptions.RequestException as e:
    print('Error fetching data:',e)
    artists_info=[]
  return artists_info

  
def top_tracks():
  url = "https://spotify-scraper.p.rapidapi.com/v1/chart/tracks/top"

  headers = {
	"X-RapidAPI-Key": "4b32350c31msh3283e91ec63afe3p1a7c4djsn0219f3a63597",
	"X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
}
  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response_data = response.json()

    tracks_info = []

    if 'tracks' in response_data:
      shortened_data = response_data['tracks'][:18]
      for track in shortened_data:
        track_name = track['name']
        track_id = track['id']
        artist_name = track['artists'][0]['name'] if track['artists'] else None
        cover_url = track['album']['cover'][0]['url'] if track['album']['cover'] else None 

        tracks_info.append({
          'id':track_id,
          'name':track_name,
          'artist': artist_name,
          'cover_url': cover_url
        })

    else:
      print('No tracks data')
      tracks_info=[]
  except requests.exceptions.RequestException as e:
    print('Error fetching data:', e)
    tracks_info =[]
  return tracks_info

def get_audio_details(query):
  url = "https://spotify-scraper.p.rapidapi.com/v1/track/download"

  querystring = {"track": query}

  headers = {
    "X-RapidAPI-Key": "4b32350c31msh3283e91ec63afe3p1a7c4djsn0219f3a63597",
    "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
  }

  try:
    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()

    audio_details = []

    if response.status_code == 200:
      response_data = response.json()
      if 'youtubeVideo' in response_data and 'audio' in response_data['youtubeVideo']:
        audio_list = response_data['youtubeVideo']['audio']

        if audio_list:
          first_audio_url = audio_list[0]['url']
          duration_text = audio_list[0]['durationText']

          audio_details.append(first_audio_url)
          audio_details.append(duration_text)
        else:
          print('No audio data available')
      else:
        print('No youtubeVideo found')
    else:
      print('Failed to fetch data')
  except requests.exceptions.RequestException as e :
    print('Error fetching data:', e)
    audio_details = []
  return audio_details

def get_track_image(track_id,track_name):
  url = 'https://open.spotify.com/track/'+ track_id;
  r = requests.get(url)
  soup = bs(r.content,features='html.parser')
  image_links_html = soup.find('img',{'alt': track_name})
  if image_links_html:
    image_links = image_links_html['srcset']
    match = re.search(r'https:\/\/i\.scdn\.co\/image\/[a-zA-Z0-9]+ 640w',image_links) 
    if match:
      url_640w = match.group().rstrip(' 640w')
    else:
      url_640w = ''
  else: 
    url_640w =''

  return url_640w


@login_required(login_url='login')
def index(request):
  artists_info = top_artist()
  top_track_list = top_tracks()

  first_six_tracks = top_track_list[:6]
  second_six_tracks = top_track_list[6:12]
  third_six_tracks = top_track_list[12:18]

  context ={
    'artists_info' : artists_info,
    'first_six_tracks' :first_six_tracks,
    'second_six_tracks':second_six_tracks,
    'third_six_tracks': third_six_tracks

    
  }
  return render(request,'index.html',context)


def login(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username,password=password)

    if user is not None:
      auth.login(request,user)
      return redirect('/')
    else:
      messages.info(request,'Invalid credentials')
      return redirect('/login')


  return render(request,'login.html')

def signup(request):
  if request.method == "POST":
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password2 = request.POST['password2']

    if password == password2:
      if User.objects.filter(email = email).exists():
        messages.info(request, 'Email already exist')
        return redirect('signup')
      elif User.objects.filter(username=username).exists():
        messages.info(request,'Username already exists')
        return redirect('signup')
      else:
        user = User.objects.create_user(username=username,email=email,password=password)
        user.save()

        user_login = auth.authenticate(username=username,password=password)
        auth.login(request,user_login)
        return redirect('/')
      
    else:
      messages.info(request,'Password not matching')
      return redirect('signup')


  else:
    return render(request,'signup.html')

@login_required(login_url='login')
def logout(request):
  auth.logout(request)
  return redirect('login')


def music(request,pk):

  track_id = pk

  url = "https://spotify-scraper.p.rapidapi.com/v1/track/metadata"

  querystring = {"trackId":track_id}

  headers = {
    "X-RapidAPI-Key": "4b32350c31msh3283e91ec63afe3p1a7c4djsn0219f3a63597",
    "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
  }

  response = requests.get(url, headers=headers, params=querystring)

  if response.status_code == 200:
    response_data = response.json()
    
    track_name = response_data.get('name')
    artist_list = response_data.get('artists',[])
    first_artist_name = artist_list[0].get('name') if artist_list else 'No artist found'
    
    audio_details_query = track_name + first_artist_name
    audio_details = get_audio_details(audio_details_query)
    audio_url = audio_details[0]
    duration_text = audio_details[1]
    track_image = get_track_image(track_id,track_name)



    context ={
      'track_name':track_name,
      'artist_name':first_artist_name,
      'audio_url': audio_url,
      'duration_text':duration_text,
      'track_image':track_image,
    }

  return render(request,'music.html',context)

def profile(request,pk):

  artist_id =pk


  url = "https://spotify-scraper.p.rapidapi.com/v1/artist/overview"

  querystring = {"artistId":artist_id}

  headers = {
    "X-RapidAPI-Key": "4b32350c31msh3283e91ec63afe3p1a7c4djsn0219f3a63597",
    "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
  }

  try:
    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()

    if response.status_code == 200:
      response_data = response.json()

      name = response_data.get('name','No name')
      monthly_listeners = response_data['stats'].get('monthlyListeners','No listeners')
      header_url = response_data['visuals']['header'][0].get('url')

      top_tracks =[]

      for track in response_data['discography']['topTracks']:
        trackid = str(track['id'])
        trackname = str(track['name'])
        if get_track_image(trackid,trackname):
          track_image = get_track_image(trackid,trackname)
        else:
          track_image =''
      
        track_info ={
          "id": track['id'],
          'name':track['name'],
          'durationText': track['durationText'],
          'playCount':track['playCount'],
          'track_image' :track_image
        }

      top_tracks.append(track_info)




      artist_data = {
        'name':name,
        'monthly_listeners' : monthly_listeners,
        'header_url': header_url,
        'topTracks':top_tracks,
      }
    
    else:
      artist_data = {}
  except requests.exceptions.RequestException as e :
    print('Error Fetching Data: ', e)
    artist_data = {}

  return render(request,'profile.html',artist_data)

def search(request):
  if request.method == "POST":
    search_query = request.POST['search_query']

    url = "https://spotify-scraper.p.rapidapi.com/v1/search"

    querystring = {"term":search_query,"type":"track"}

    headers = {
      "X-RapidAPI-Key": "4b32350c31msh3283e91ec63afe3p1a7c4djsn0219f3a63597",
      "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
    }


  try:

    response = requests.get(url, headers=headers, params=querystring)
    track_list =[]

    if response.status_code == 200:
      response_data = response.json()

      search_results_count = response_data['tracks']['totalCount']
      tracks = response_data['tracks']['items']

      for track in tracks:
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        duration = track['durationText']
        trackid = track['id']
        if get_track_image(trackid,track_name):
          track_image = get_track_image(trackid,track_name)
        else:
          track_image = ''
        
        track_list.append({
          'track_name':track_name,
          'artist_name':artist_name,
          'duration':duration,
          'trackid':trackid,
          'track_image':track_image
        })
      context ={
        'search_results_count': search_results_count,
        'track_list':track_list,
      }

      return render(request,'search.html',context)

  except requests.exceptions.RequestException as e :
    print('Error fetching data:', e)


  else:
    return render(request,'search.html')



