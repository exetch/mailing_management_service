from django.urls import path

from . import views
from .views import email_verification, email_not_verified, UserPasswordResetView, UserPasswordResetConfirmView, \
    PasswordResetDoneView, PasswordResetCompleteView

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('email_not_verified/', email_not_verified, name='email_not_verified'),
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='profile'),
    path('edit_profile/<int:pk>/', views.EditProfileView.as_view(), name='edit_profile'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('verify/<uidb64>/<token>/', email_verification, name='email_verification'),
    path('password_reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/password_reset_done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/<uidb64>/set-password/password_reset_complete', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
