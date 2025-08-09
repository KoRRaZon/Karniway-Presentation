from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.contrib.auth import login
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView

from apps.accounts.forms import UserRegisterForm
from apps.accounts.models import CustomUser, Player, Master

class UserRegisterView(CreateView):
    model = CustomUser
    template_name = 'accounts/register.html'
    form_class = UserRegisterForm
    extra_context = {'title': 'Регистрация'}
    success_url = '/'

    def form_valid(self, form):
        with transaction.atomic():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()

            if user.account_type == "player":
                Player.objects.create(
                    user=user,
                    nickname='Лысый гоблин',
                    description=""
                )
            elif user.account_type == "master":
                Master.objects.create(
                    user=user,
                    description="",
                )

            login(self.request, user)

        return super().form_valid(form)


class UserLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'
    success_url = '/'
    extra_context = {'title': 'Авторизация'}

class UserLogoutView(View):
    next_page = '/'

