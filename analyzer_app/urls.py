from django.urls import path
from . import views

app_name = 'analyzer_app'

urlpatterns = [
    path('', views.welcome_page, name='welcome'),
    path('login/', views.login_page, name="login"),
    path('brainboost/', views.brain_boost_page, name="brainboost"),
    path('home/', views.analyze_document_view, name='analyze_document'),
]

