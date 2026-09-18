from django.urls import path
from .views import ProfileView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView


urlpatterns =[ 
    path('profile/', ProfileView.as_view()),
    path('login/', LoginView.as_view() , name='login'),
    path('logout/', LogoutView.as_view()),
]