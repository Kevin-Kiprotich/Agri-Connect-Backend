from . import views
from django.urls import path

urlpatterns = [
    path('sums/',views.UploadSums.as_view())
]

