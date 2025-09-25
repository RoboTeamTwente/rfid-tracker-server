from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Job, Membership, SubTeam


class RegistrationForm(UserCreationForm):
    subteam = forms.ModelChoiceField(
        queryset=SubTeam.objects.all(), required=True, label='Subteam'
    )

    job = forms.ModelChoiceField(
        queryset=Job.objects.all(), required=True, label='Job type'
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
            'subteam',
            'job',
        ]

    def save(self, commit=True):
        user = super().save(commit=commit)
        subteam = self.cleaned_data['subteam']
        job = self.cleaned_data['job']
        if commit:
            Membership.objects.create(person=user, subteam=subteam, job=job)
        return user
