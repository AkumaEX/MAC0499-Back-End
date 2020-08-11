from django.urls import path
from . import views

app_name = 'ml'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload, name='upload'),
    path('configure', views.configure, name='configure'),
    path('delete', views.delete, name='delete'),
    path('train', views.train, name='train'),
    path('api', views.api, name='api')
]
