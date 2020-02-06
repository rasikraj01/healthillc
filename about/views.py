from django.shortcuts import render
from django.views import View

# Create your views here.
class Index(View):
    def get(self, request):
        return render(request, 'about/index.html')


class About(View):
    def get(self, request):
        return render(request, 'about/about.html')


class TermsAndConditions(View):
    def get(self, request):
        return render(request, 'about/tnc.html')

class Privacy(View):
    def get(self, request):
        return render(request, 'about/privacy.html')

class Refund(View):
    def get(self, request):
        return render(request, 'about/refund.html')