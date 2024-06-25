
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('login/', views.login_view, name="login"),
    path('register/', views.register_user, name="register"),
    path("logout/",views.user_logout , name="logout")
]