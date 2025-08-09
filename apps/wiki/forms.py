from django import forms

from apps.wiki.models import Post


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image']


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image']