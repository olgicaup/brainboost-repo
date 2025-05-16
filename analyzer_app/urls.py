from django.urls import path
from . import views

app_name = 'analyzer_app'

urlpatterns = [
    path('', views.welcome_page, name='welcome'),
    path('login/', views.login_page, name="login"),
    path('signup/', views.signup_page, name='signup'),
    path('brainboost/', views.brain_boost_page, name="brainboost"),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.analyze_document_view, name='analyze_document'),
    path('favorites/', views.favorites_page, name='favorites'),
    path('download/<str:file_name>/', views.download_processed_file, name='download_processed_file'),
    path('favorites/delete/<int:file_id>/', views.delete_favorite, name='delete_favorite'),



]