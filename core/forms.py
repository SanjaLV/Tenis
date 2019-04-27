from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist

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
