from django import forms

from apps.accounts.models import CustomUser, Player, Master

# формы для редактирования профиля
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['avatar', 'nickname', 'description']

class MasterForm(forms.ModelForm):
    class Meta:
        model = Master
        fields = ['avatar', 'nickname', 'description']


class UserRegisterForm(forms.ModelForm):
    first_name = forms.CharField(label='First Name', max_length=50)
    last_name = forms.CharField(label='Last Name', max_length=50)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password', 'password_confirm')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data

class UserLoginForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password_confirm')
