from django.urls import path
from tracker import views

urlpatterns = [
    path('', views.home, name='home'), # type: ignore
    path('picker/', views.stock_picker, name='picker'), # type: ignore
    path('tracker/', views.stock_tracker, name='tracker'), # type: ignore
    path('signup', views.handleSignup, name='signup'),
    path('login', views.handleLogin, name='handleLogin'),
    path('logout', views.handleLogout, name='handleLogout'),
]
