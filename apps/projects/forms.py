from django import forms

from .models import ProjectRequest
from .spam import detect_project_request_spam


class ProjectRequestForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1", "aria-hidden": "true"}),
    )

    class Meta:
        model = ProjectRequest
        fields = [
            "full_name",
            "email",
            "company",
            "project_type",
            "budget_range",
            "timeline",
            "message",
        ]
        labels = {
            "full_name": "Full name",
            "email": "Work email",
            "company": "Company",
            "project_type": "What do you need help with?",
            "budget_range": "Expected budget range",
            "timeline": "Target timeline",
            "message": "Project context",
        }
        help_texts = {
            "company": "Optional, but useful for B2B requests.",
            "message": "Describe the outcome, current systems, constraints, and what is blocking progress.",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "company": forms.TextInput(attrs={"autocomplete": "organization"}),
            "message": forms.Textarea(attrs={"rows": 7}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["website"].widget.attrs["class"] = "hp-field"
        self.spam_reasons = []

    def clean_full_name(self):
        return self.cleaned_data["full_name"].strip()

    def clean_company(self):
        return self.cleaned_data["company"].strip()

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 40:
            raise forms.ValidationError(
                "Please include at least a few sentences about the business goal, systems involved, or current blocker."
            )
        return message

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data
        self.spam_reasons = detect_project_request_spam(cleaned_data, cleaned_data.get("website", ""))
        if self.spam_reasons:
            raise forms.ValidationError("This request looks like an automated or test submission. Please review the fields and send a real project request.")
        return cleaned_data
