"""
URL configuration for SmartHealthCare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import patient.views as pviews
import hospital.views as hviews

urlpatterns = [
    path('admin/', admin.site.urls),
]

patient_Url = [
    path('',pviews.landingpage,name='landingpage'),
    path('diseaseform/',pviews.diseaseform,name='diseaseform'),
]

hospital_url = [
    path('add_doctor/',hviews.add_doctor,name='add_doctor'),
    path('view_doctor/',hviews.view_doctor,name='view_doctor'),
    path('login/',hviews.login,name='login')
]

urlpatterns += patient_Url + hospital_url