from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordChangeView, PasswordResetConfirmView, PasswordResetCompleteView
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView

from apps.accounts.forms import UserRegisterForm, UserProfileForm, PlayerForm, MasterForm
from apps.accounts.models import CustomUser, Player, Master
from apps.accounts.tokens import activation_token



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
    success_url = reverse_lazy('accounts:activation_sent') # страница проверки почты

    def form_valid(self, form):
        with transaction.atomic():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
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

            # формируем ссылку активации
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = activation_token.make_token(user)
            activate_url = reverse('accounts:activate', kwargs={'uidb64': uidb64, 'token': token})

            # отсылаем письмо
            context = {'user': user, 'activate_url': activate_url}
            subject = "Подтверждение регистрации на Karniway"
            html_body = render_to_string('accounts/email/activation_email.html', context)
            text_body = render_to_string('accounts/email/activation_email.txt', context)

            message = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            message.attach_alternative(html_body, "text/html")
            message.send()

            # не логиним, а ждем подтверждение
            return redirect(self.success_url)


class ActivateAccountView(View):
    success_url = reverse_lazy('accounts:activation_success')
    invalid_url = reverse_lazy('accounts:activation_invalid')

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except Exception:
            messages.error(request, "Неверная ссылка активации")

        if activation_token.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=['is_active']) # оптимизируем запрос
            # логин после активации
            login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
            messages.success(request, "Аккаунт подтвержден. Добро пожаловать в Karniway :)")
            return redirect(self.success_url)
        else:
            messages.error(request, "Ссылка просрочена или недействиетельна.")
            return redirect(self.invalid_url)


class UserLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('wiki:home_page')
    extra_context = {'title': 'Авторизация'}

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('wiki:home_page')


class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/email/password_reset_email.txt'
    subject_template_name = 'accounts/email/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    extra_context = {'title': 'Восстановление пароля'}

class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
