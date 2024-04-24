from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path('login/',views.LoginView.as_view(),name='login'),
    path('signup/',views.SignUpView.as_view(),name='signup')
]