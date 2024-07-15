
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'authentication'
urlpatterns = [
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('login/', views.login_view, name="login"),
    path('register/', views.register_user, name="register"),
    path("logout/",views.user_logout , name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path('delete_account/', views.delete_account_view, name='delete_account'),
    path('password_reset/', views.reset_password_view, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
    path('password-change/', views.ChangePasswordView.as_view(), name='password_change'),
    path('contact/', views.contact_view, name='contact'),

]