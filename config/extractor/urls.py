from django.urls import path
from .views import upload_file, download_text

urlpatterns = [
    path('', upload_file, name='upload'),
    path('download/', download_text, name='download_text'),
]
