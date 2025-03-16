from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from hospital.models import Doctor
# Create your views here.


def view_doctor(request):
    doctors = Doctor.objects.all()  # Fetch all doctors
    context = {"doctors": doctors}  # Use lowercase key
    return render(request, "hospital/view_doctor.html", context)

def add_doctor(request):
    if request.method == "POST":
        name = request.POST.get("name")
        photo = request.FILES.get("photo")
        experience = request.POST.get("experience")
        specialization = request.POST.get("specialization")
        available_days = request.POST.getlist("days")  # Gets selected checkboxes as a list
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        # Convert list of days into a comma-separated string
        available_days_str = ", ".join(available_days)

        # Save doctor to the database
        Doctor.objects.create(
            name=name,
            photo=photo,
            experience=experience,
            specialization=specialization,
            available_days=available_days_str,
            start_time=start_time,
            end_time=end_time
        )

        messages.success(request, "Doctor added successfully!")
        return redirect("view_doctor")  # Redirect to doctor listing page

    return render(request, "hospital/add_doctor.html")


def appointments(request):
    return render(request,'hospital/appointments.html')

@login_required
def dashboard(request):
    return render(request,'hospital/dashboard.html')


# Hardcoded Credentials
PREDEFINED_USERNAME = "admin"
PREDEFINED_PASSWORD = "12345"

def hospital_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username,password)

        # Check if the entered credentials match the hardcoded ones
        if username == PREDEFINED_USERNAME and password == PREDEFINED_PASSWORD:
            # Check if user exists in Django's User model
            user, created = User.objects.get_or_create(username=PREDEFINED_USERNAME)
            if created:
                user.set_password(PREDEFINED_PASSWORD)  # Set password if user was just created
                user.save()

            # Authenticate the user
            user = authenticate(request, username=PREDEFINED_USERNAME, password=PREDEFINED_PASSWORD)

            if user is not None:
                login(request, user)  # Log the user in
                return redirect("dashboard")  # Redirect to dashboard
            else:
                messages.error(request, "Authentication failed. Try again.")
        else:
            messages.error(request, "Invalid username or password")  # Show error message

    return render(request, "hospital/login.html")  # Render login page


def hospital_logout(request):
    logout(request)  # Log the user out
    messages.success(request, "You have been logged out successfully.")  # Show success message
    return redirect("login")  # Redirect to login page