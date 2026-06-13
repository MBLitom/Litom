from django import forms

from .models import ProjectReviewOrder


class ProjectReviewOrderForm(forms.ModelForm):
    class Meta:
        model = ProjectReviewOrder
        fields = ("full_name", "email", "company", "project_type", "short_description")
        labels = {
            "full_name": "Full name",
            "email": "Work email",
            "company": "Company",
            "project_type": "Project type",
            "short_description": "Short project context",
        }
        help_texts = {
            "short_description": "Briefly describe the current situation, risks, systems involved, and what you want reviewed.",
        }
        widgets = {
            "short_description": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        profile = getattr(user, "client_profile", None)
        if user and not self.is_bound:
            self.fields["email"].initial = user.email
            self.fields["full_name"].initial = getattr(profile, "full_name", "") or user.get_full_name()
            self.fields["company"].initial = getattr(profile, "company_name", "")
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_short_description(self):
        value = self.cleaned_data["short_description"].strip()
        if len(value) < 40:
            raise forms.ValidationError("Please include enough context for MB Litom to review the request.")
        return value
