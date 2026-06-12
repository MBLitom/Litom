from django.shortcuts import render


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
    return render(request, "website/contact.html")
