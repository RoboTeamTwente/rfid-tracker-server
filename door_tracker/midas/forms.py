from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Assignment, Quota, Subteam


class RegistrationForm(UserCreationForm):
    subteams = forms.ModelMultipleChoiceField(
        queryset=Subteam.objects.all(),
        required=True,
        label='Subteams',
    )

    quota = forms.ModelChoiceField(
        queryset=Quota.objects.all(),
        required=True,
        label='Workload',
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'password1',
            'password2',
            'subteams',
            'quota',
        ]

    def save(self, commit=True):
        user = super().save(commit=commit)
        subteams = self.cleaned_data['subteams']
        quota = self.cleaned_data['quota']

        if commit:
            a = Assignment.objects.create(user=user, quota=quota)
            a.subteams.set(subteams)

        return user
