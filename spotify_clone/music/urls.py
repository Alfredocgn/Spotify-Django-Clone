from django.urls import path
from . import views


urlpatterns = [
  path('',views.index,name='index'),
  path('login',views.login,name='login'),
  path('music',views.music,name='music'),
  path('profile',views.profile,name='profile'),
  path('search',views.search,name='search'),
  path('signup',views.signup,name='signup'),
  path('logout',views.logout,name='logout'),
]