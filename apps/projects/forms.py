from django import forms

from .models import ProjectRequest


class ProjectRequestForm(forms.ModelForm):
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
