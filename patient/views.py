from django.shortcuts import render,redirect
import os
from django.urls import reverse
import google.generativeai as genai
from django.shortcuts import render
from django.http import HttpResponse
from dotenv import load_dotenv
from sklearn.neighbors import NearestNeighbors
import numpy as np
import json
from hospital.models import Doctor

load_dotenv()

# Create your views here.
def landingpage(request):
    return render(request,'landingpage.html')



# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API"))

# Define model parameters
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Load the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

def diseaseform(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input", "").strip()

        if not user_input:
            print("Error: No symptoms provided.")
            return HttpResponse(status=204)  # No content

        # Start a chat session with Gemini
        chat_session = model.start_chat(
            history=[{
                "role": "user",
                "parts": [
                    f"You will receive an input like this:\n{user_input}\n\n"
                    "From this input, extract:\n"
                    "- Disease name\n"
                    "- The doctor specialization from this list:\n"
                    "\"General Physician, Cardiologist, Dermatologist, Endocrinologist, Gastroenterologist, Neurologist, "
                    "Orthopedic Surgeon, Ophthalmologist, ENT Specialist, Pulmonologist, Nephrologist, Urologist, Gynecologist, "
                    "Pediatrician, Oncologist, Psychiatrist, Rheumatologist, Hematologist, Plastic Surgeon, Radiologist, "
                    "Geriatrician, Sports Medicine Specialist, Immunologist, Infectious Disease Specialist, Dentist, "
                    "Physiotherapist\"\n\n"
                    "Return the output in **pure JSON format** without any additional text. The output should be:\n"
                    "{\n"
                    "  \"disease\": [\"\"],\n"
                    "  \"doctor\": [\"\"]\n"
                    "}\n\n"
                    "- If the symptoms are in Hindi, **translate them to English** before processing.\n"
                    "- Do **not** include '```' or the word 'json' in the response.\n"
                    "- You can suggest multiple diseases and doctors."
                ],
            }]
        )

        # Get response from Gemini
        response = chat_session.send_message(user_input)
        print("\n🔹 Gemini Response:")
        print(response.text)  # Debugging

        # Extract disease and doctor specializations from Gemini response
        try:
            response_data = json.loads(response.text)
            diseases = response_data.get("disease", [])
            doctor_specializations = response_data.get("doctor", [])
        except json.JSONDecodeError:
            print("\n❌ Error: Unable to parse Gemini response.")
            return HttpResponse(status=500)  # Internal Server Error

        # Get doctors using KNN (No Hallucination)
        recommended_doctors = get_nearest_doctors(doctor_specializations)

        # ✅ Store results in session before redirecting
        request.session["diseases"] = diseases
        request.session["doctors"] = [
    {
        "name": doctor.name,
        "specialization": doctor.specialization,
        "experience": doctor.experience,
        "photo": doctor.photo.url if doctor.photo else "",  # ✅ Include photo URL
        "available_days": doctor.available_days,
        "start_time": doctor.start_time.strftime("%H:%M"),  # ✅ Convert time to string
        "end_time": doctor.end_time.strftime("%H:%M"),
    }
    for doctor in recommended_doctors
]


        # 🔄 Redirect to 'seedoctors' page
        return redirect(reverse("seedoctors"))

    return render(request, "patient/diseaseform.html")


def get_nearest_doctors(specializations):
    """
    Finds the best matching doctors strictly based on specialization using KNN.
    """
    if not specializations:
        print("\n❌ No specializations provided.")
        return []

    # Fetch only relevant doctors matching the given specializations
    doctors = list(Doctor.objects.filter(specialization__in=specializations))
    if not doctors:
        print("\n❌ No matching doctors found in the database.")
        return []

    # Create a mapping of specialization to doctors
    specialization_to_doctors = {spec: [] for spec in specializations}
    for doctor in doctors:
        specialization_to_doctors[doctor.specialization].append(doctor)

    # Use KNN to find the top 3 closest matches for each specialization
    selected_doctors = set()  # ✅ Use a **set** to avoid duplicates
    for spec in specializations:
        doctor_list = specialization_to_doctors.get(spec, [])
        if not doctor_list:
            print(f"\n⚠️ No doctors found for specialization: {spec}")
            continue  # Skip if no doctors available

        # Convert specializations to numerical format for KNN
        specialization_array = np.arange(len(doctor_list)).reshape(-1, 1)
        knn = NearestNeighbors(n_neighbors=min(3, len(doctor_list)), metric="euclidean")
        knn.fit(specialization_array)

        # Find nearest doctors
        distances, indices = knn.kneighbors([[0]])  # Compare to first doctor
        for idx in indices[0]:
            selected_doctors.add(doctor_list[int(idx)])  # ✅ Ensures no duplicates

    return list(selected_doctors)  # Convert back to list for Django compatibility


def seedoctors(request):
    diseases = request.session.get("diseases", [])
    doctors = request.session.get("doctors", [])  # List of doctor IDs


    # Clear session data after rendering
    request.session.pop("diseases", None)
    request.session.pop("doctors", None)

    return render(
        request,
        "patient/seedoctors.html",
        {"diseases": diseases, "doctors": doctors},
    )