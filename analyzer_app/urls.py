from django.urls import path
from . import views

app_name = 'analyzer_app'

urlpatterns = [
    path('', views.analyze_document_view, name='analyze_document'),
]

