from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView

from apps.accounts.forms import UserRegisterForm, UserProfileForm, PlayerForm, MasterForm
from apps.accounts.models import CustomUser, Player, Master


class OwnProfileView(DetailView, LoginRequiredMixin):
    template_name = 'accounts/own_profile.html'
    context_object_name = 'user_obj'

    def get_object(self):
        queryset = CustomUser.objects.select_related('player', 'master')
        return queryset.get(pk=self.request.user.pk)


class PublicProfileView(DetailView, LoginRequiredMixin):
    model = CustomUser
    template_name = 'accounts/public_profile.html'
    context_object_name = 'user_obj'

    def get_queryset(self):
        # фильтруем только активных
        return CustomUser.objects.select_related('player', 'master').filter(is_active=True)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get(self, request, *args, **kwargs):
        user = request.user
        user_form = UserProfileForm(instance=user)
        role_form = PlayerForm(instance=user.player) if user.account_type == 'player' else MasterForm(instance=user.master)
        return render(request, self.template_name, {'user_form': user_form, 'role_form': role_form})

    def post(self, request, *args, **kwargs):
        user = request.user
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        role_form = PlayerForm(request.POST, instance=user.player) if user.account_type == 'player' else MasterForm(request.POST, instance=user.master)

        if user_form.is_valid() and role_form.is_valid():
            with transaction.atomic():
                self.object = user_form.save()
                role_form.save()
            return redirect(self.get_success_url())

        return render(request, self.template_name, {'user_form': user_form, 'role_form': role_form})



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
                    avatar='accounts/avatars/default.png',
                    nickname='Лысый гоблин',
                    description=""
                )
            elif user.account_type == "master":
                Master.objects.create(
                    user=user,
                    avatar='accounts/avatars/default.png',
                    nickname='Крутой лысый гоблин',
                    description="",
                )

            login(self.request, user)

        self.object = user # для возможного обращения внутри шаблона
        return redirect(self.get_success_url())


class UserLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('wiki:home_page')
    extra_context = {'title': 'Авторизация'}

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('wiki:home_page')

