from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators  import login_required
import requests

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
      for artist in response_data['artists']:
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

  


@login_required(login_url='login')
def index(request):
  artists_info = top_artist()
  print(artists_info)
  context ={
    'artists_info' : artists_info,
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


  



def music(request):
  return render(request,'music.html')

def profile(request):
  return render(request,'profile.html')

def search(request):
  return render(request,'search.html')



