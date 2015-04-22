"""Forms..."""
from core.models import Member
from django import forms


class RegisterForm(forms.Form):

    """Form for registering new users."""

    email = forms.EmailField()
    name = forms.CharField(label='Name', max_length=255)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_repeat = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    def clean(self):
        """Look if given passwords match."""
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_repeat')

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords don't match!")

        return self.cleaned_data

    def clean_email(self):
        """Look if there's already a user with that email address."""
        email = self.cleaned_data['email']
        try:
            if Member.objects.get(user__email=email):
                raise forms.ValidationError('User already exists!')
        except Member.DoesNotExist:
            pass

        return email