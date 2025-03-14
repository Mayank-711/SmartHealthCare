from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request,'hospital/login.html')

def view_doctor(request):
    return render(request,'hospital/view_doctor.html')

def add_doctor(request):
    return render(request,'hospital/add_doctor.html')

