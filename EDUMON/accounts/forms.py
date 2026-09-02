from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser, StatusUpdate


class RegistrationForm(UserCreationForm):
    """Registration form covering both roles (R1a, R2b)."""

    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'real_name', 'role', 'bio', 'photo')

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email


class ProfileForm(forms.ModelForm):
    """Lets a user edit their own profile fields."""

    class Meta:
        model = CustomUser
        fields = ('real_name', 'email', 'bio', 'photo')


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': "What's on your mind?"}),
        }
