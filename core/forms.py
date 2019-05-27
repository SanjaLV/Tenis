from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.forms import UserCreationForm

from core.models import Player


class PlayerCreation(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('name',)

    name = forms.CharField(max_length=30)

    def clean_name(self):
        name = self.cleaned_data['name']

        if len(name) == 0:
            raise ValidationError("Name cannot not be empty")

        try:
            player = Player.objects.get(name=name)
            raise ValidationError("This name is already taken.")
        except ObjectDoesNotExist:
            pass

        return name


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=False, help_text="Optional.")
    last_name = forms.CharField(max_length=150, required=False, help_text="Optional.")
    email = forms.EmailField(max_length=254, help_text="Required.")

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )
