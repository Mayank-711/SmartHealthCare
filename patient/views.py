from django.shortcuts import render

# Create your views here.
def landingpage(request):
    return render(request,'landingpage.html')


def diseaseform(request):
    return render(request,'patient/diseaseform.html')