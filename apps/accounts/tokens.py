from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # включаем user.is_active, чтобы токен инвалидировался после активации пользователя.
        return f"{user.pk}{user.is_active}{timestamp}"

activation_token = EmailActivationTokenGenerator()