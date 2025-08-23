from django.urls import path
from django.views.generic import TemplateView

from apps.accounts.views import UserRegisterView, UserLoginView, UserLogoutView, OwnProfileView, PublicProfileView, \
    ProfileUpdateView, ActivateAccountView

app_name = 'accounts'

urlpatterns = [
    path('profile/', OwnProfileView.as_view(), name='profile'),
    path('profile/edit', ProfileUpdateView.as_view(), name='profile_edit'),
    path('users/<uuid:pk>/', PublicProfileView.as_view(), name='public_profile'),

    path('register/', UserRegisterView.as_view(), name='register'),
    path('activation_sent/', TemplateView.as_view(
        template_name='accounts/activation_sent.html'), name='activation_sent'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('activation_success/', TemplateView.as_view(
        template_name='accounts/activation_success.html'), name='activation_success'),
    path('activation_invalid/', TemplateView.as_view(
        template_name='accounts/activation_invalid.html'), name='activation_invalid'),

    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]