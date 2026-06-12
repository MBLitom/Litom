from django.shortcuts import redirect, render

from apps.projects.forms import ProjectRequestForm


def homepage(request):
    return render(request, "website/homepage.html")


def services(request):
    return render(request, "website/services.html")


def pricing(request):
    return render(request, "website/pricing.html")


def process(request):
    return render(request, "website/process.html")


def changeharbor_case_study(request):
    return render(request, "website/case_studies/changeharbor.html")


def contact(request):
    if request.method == "POST":
        form = ProjectRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("website:contact_success")
    else:
        form = ProjectRequestForm()

    return render(request, "website/contact.html", {"form": form})


def contact_success(request):
    return render(request, "website/contact_success.html")
