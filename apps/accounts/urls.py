from django.urls import path

from apps.accounts.views import UserRegisterView, UserLoginView, UserLogoutView, OwnProfileView, PublicProfileView, \
    ProfileUpdateView

app_name = 'accounts'

urlpatterns = [
    path('profile/', OwnProfileView.as_view(), name='profile'),
    path('profile/edit', ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile_detail/<uuid:pk>/', PublicProfileView.as_view(), name='profile_detail'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]