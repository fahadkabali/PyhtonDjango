
from django.urls import path
from . import views

urlpatterns = [
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('login/', views.login_view, name="login"),
    path('register/', views.register_user, name="register"),
    path("logout/",views.user_logout , name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path('delete_account/', views.delete_account_view, name='delete_account'),

]