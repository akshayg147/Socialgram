from django.urls import path
from . import views
urlpatterns = [
    path('', views.signin, name='signin'),
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name = 'signup' ),
    path('upload', views.upload, name='upload'),
    path('like-post', views.like_post, name='like-post'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('index', views.index, name='index'),
    path('logout', views.logout, name = 'logout'),
    path('settings', views.settings,name='settings')
]