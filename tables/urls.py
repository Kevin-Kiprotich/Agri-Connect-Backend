from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('sums/',views.UploadSums.as_view()),
    path('getsums/',views.getSUMS.as_view()),
    path('at/',views.computeTotals.as_view()),
    path('getat/',views.getAT.as_view()), 
    path('getct/',views.getCT.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)