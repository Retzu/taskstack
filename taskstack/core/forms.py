from core.models import Member
from django import forms


class RegisterForm(forms.Form):
    email = forms.EmailField()
    name = forms.CharField(label='Name', max_length=255)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_repeat = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    def clean(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_repeat')

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords don't match!")

        return self.cleaned_data

    def clean_email(self):
        if Member.objects.get(user__email=self.cleaned_data['email']):
            raise forms.ValidationError('User already exists!')