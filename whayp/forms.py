from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

from .models import Post, Photo
from django.forms import formset_factory

MAX_PHOTOS = 10


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['description']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']
