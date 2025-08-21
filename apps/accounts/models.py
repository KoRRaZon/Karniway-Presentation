from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from apps.accounts.managers import CustomUserManager
from apps.common.models import IsDeletedModel


ACCOUNT_TYPE_CHOICES = (
    ('player', 'Player'),
    ('master', 'Master'),
)

class CustomUser(AbstractBaseUser, IsDeletedModel, PermissionsMixin):
    '''
    Кастомная модель пользователя, расширяющая AbstractBaseUser.
    '''

    first_name = models.CharField('Имя', max_length=30)
    last_name = models.CharField('Фамилия', max_length=30)
    email = models.EmailField(unique=True)
    account_type = models.CharField(choices=ACCOUNT_TYPE_CHOICES)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Player(IsDeletedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='accounts/avatars/', null=True, blank=True)
    nickname = models.CharField('Псевдоним игрока', max_length=30)
    description = models.TextField('Расскажите о себе', max_length=500)


class Master(IsDeletedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='accounts/avatars/', null=True, blank=True)
    nickname = models.CharField('Псевдоним мастера', max_length=30)
    description = models.TextField('Расскажите о себе', max_length=500)
