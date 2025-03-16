from django.shortcuts import render,redirect
import os
import google.generativeai as genai
from django.shortcuts import render
from django.http import HttpResponse
from dotenv import load_dotenv


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
            history=[
                {
                    "role": "user",
                    "parts": [
                        "You will receive an input like this:\n"
                        f"{user_input}\n"
                        "From this input, extract:\n"
                        "- Disease name\n"
                        "- The doctor specialization from this list:\n"
                        "\"General Physician, Cardiologist, Dermatologist, Endocrinologist, Gastroenterologist, Neurologist, "
                        "Orthopedic Surgeon, Ophthalmologist, ENT Specialist, Pulmonologist, Nephrologist, Urologist, Gynecologist, "
                        "Pediatrician, Oncologist, Psychiatrist, Rheumatologist, Hematologist, Plastic Surgeon, Radiologist, "
                        "Geriatrician, Sports Medicine Specialist, Immunologist, Infectious Disease Specialist, Dentist, "
                        "PhysioTherapist\"\n\n"
                        "Output in JSON format:\n"
                        "{\n"
                        "\"disease\": [],\n"
                        "\"doctor\": []\n"
                        "} (You can suggest multiple options)"
                    ],
                }
            ]
        )

        # Get response from Gemini
        response = chat_session.send_message(user_input)

        # Print response to terminal (for debugging)
        print(response.text)

        return redirect(diseaseform)  # No content (prevents duplicate output)

    return render(request, "patient/diseaseform.html")