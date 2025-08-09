from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class CustomUserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Указанна электронная почта некорректного формата')

    def validate_user(self, first_name, last_name, email, password):
        if not first_name and not last_name:
            raise ValidationError('Заполните необходимые поля')
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValidationError('Укажите действительный адрес электронной почты')

        if not password:
            raise ValidationError('Укажите корректный пароль')

    def create_user(self, first_name, last_name, email, password, **extra_fields):
        self.validate_user(first_name, last_name, email, password)

        user = self.model(
            first_name=first_name, last_name=last_name, email=email, **extra_fields
        )

        user.set_password(password)
        extra_fields.setdefault('is_staff', False)
        user.save()
        return user


    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValidationError('Superuser must have is_staff=True.')

        user = self.create_user(first_name, last_name, email, password, **extra_fields)
        return user

    def get_by_natural_key(self, email):
        return self.get(email=email)
