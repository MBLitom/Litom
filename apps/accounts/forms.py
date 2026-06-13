from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import ClientProfile


class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Work email")
    full_name = forms.CharField(label="Full name", max_length=160)
    company_name = forms.CharField(label="Company", max_length=160, required=False)
    phone = forms.CharField(label="Phone", max_length=60, required=False)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("email", "full_name", "company_name", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(username=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_full_name(self):
        return self.cleaned_data["full_name"].strip()

    def clean_company_name(self):
        return self.cleaned_data["company_name"].strip()

    def clean_phone(self):
        return self.cleaned_data["phone"].strip()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        full_name = self.cleaned_data["full_name"]
        user.first_name = full_name[:150]
        if commit:
            user.save()
            ClientProfile.objects.create(
                user=user,
                full_name=full_name,
                company_name=self.cleaned_data["company_name"],
                phone=self.cleaned_data["phone"],
            )
        return user
