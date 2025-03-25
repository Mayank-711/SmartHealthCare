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
import speech_recognition as sr
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def diseaseform(request):
    if request.method == "POST":
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Handle voice input request
            try:
                recognizer = sr.Recognizer()
                # Increase sensitivity to pick up speech better
                recognizer.energy_threshold = 300  # Default is 300, lower is more sensitive
                recognizer.dynamic_energy_threshold = True  # Adjust for ambient noise automatically
                
                with sr.Microphone() as source:
                    print("Initializing microphone...")
                    # Increase duration for better ambient noise adjustment
                    recognizer.adjust_for_ambient_noise(source, duration=2)
                    print("Listening for voice input...")
                    
                    # Increase timeout parameters
                    audio = recognizer.listen(
                        source, 
                        timeout=15,  # Increased from 10
                        phrase_time_limit=20  # Increased from 15
                    )
                    
                    print("Audio captured, trying to recognize...")
                    try:
                        # Try multiple recognition engines if one fails
                        try:
                            user_input = recognizer.recognize_google(audio)
                            print(f"Google recognized: {user_input}")
                        except:
                            # Try with a different API if Google fails
                            try:
                                from speech_recognition import Recognizer, AudioFile
                                user_input = recognizer.recognize_sphinx(audio)
                                print(f"Sphinx recognized: {user_input}")
                            except:
                                raise sr.UnknownValueError("Multiple recognition engines failed")
                                
                        return JsonResponse({"transcript": user_input})
                    except sr.UnknownValueError:
                        print("❌ Error: Could not understand audio")
                        return JsonResponse({
                            "error": "Could not understand audio. Please speak louder and clearly."
                        }, status=400)
                    except sr.RequestError as e:
                        print(f"❌ Error: Speech recognition service unavailable: {e}")
                        return JsonResponse({
                            "error": f"Speech recognition service unavailable: {str(e)}"
                        }, status=500)
            except Exception as e:
                import traceback
                traceback.print_exc()  # Print the full exception traceback
                print(f"❌ Unexpected Error during speech recognition: {str(e)}")
                return JsonResponse({
                    "error": f"Microphone access error: {str(e)}"
                }, status=500)
        # Process text input from form
        user_input = request.POST.get("user_input", "").strip()
        if not user_input:
            print("Error: No symptoms provided.")
            return render(request, "patient/diseaseform.html", {"error": "Please enter your symptoms or use voice input."})

        try:
            # Start a chat session with the AI model
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
                        "Physiotherapist\"\n"
                        "- Precautions that should be taken for this condition\n"
                        "- Urgency level on a scale of 0-5, where:\n"
                        "  0 = Self-care only (no doctor visit needed)\n"
                        "  1 = Schedule a routine appointment (within the next few weeks)\n"
                        "  2 = Schedule appointment soon (within a week)\n"
                        "  3 = See a doctor within 1-2 days\n"
                        "  4 = Seek medical attention promptly (within 24 hours)\n"
                        "  5 = Emergency (immediate medical attention required)\n\n"
                        "Return the output in **pure JSON format** without any additional text. The output should be:\n"
                        "{\n"
                        "  \"disease\": [\"\"],\n"
                        "  \"doctor\": [\"\"],\n"
                        "  \"precautions\": [\"\"],\n"
                        "  \"urgency_level\": 0\n"
                        "}\n\n"
                        "- If the symptoms are in Hindi, **translate them to English** before processing.\n"
                        "- Do **not** include '```' or the word 'json' in the response.\n"
                        "- You can suggest multiple diseases, doctors, and precautions."
                    ],
                }]
            )

            # Get response from the AI model
            response = chat_session.send_message(user_input)
            print("\n🔹 AI Model Response:")
            print(response.text)  # Debugging

            # Extract disease, doctor specializations, precautions, and urgency level from AI response
            try:
                # Clean up the response to ensure it's valid JSON
                cleaned_response = response.text.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:-3]  # Remove ```json and ```
                elif cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:-3]  # Remove ``` and ```
                
                response_data = json.loads(cleaned_response)
                diseases = response_data.get("disease", [])
                doctor_specializations = response_data.get("doctor", [])
                precautions = response_data.get("precautions", [])
                urgency_level = response_data.get("urgency_level", 1)  # Default to level 1 if not provided
                
                if not diseases or not doctor_specializations:
                    raise ValueError("Missing disease or doctor information in the response")
                    
            except json.JSONDecodeError as e:
                print(f"\n❌ Error: Unable to parse AI response: {e}")
                print(f"Response was: {response.text}")
                return render(request, "patient/diseaseform.html", {"error": "Unable to process your symptoms. Please try again with more details."})
            except ValueError as e:
                print(f"\n❌ Error: {e}")
                return render(request, "patient/diseaseform.html", {"error": "Unable to determine disease or doctor. Please provide more specific symptoms."})

            
            # Get doctors using KNN
            try:
                recommended_doctors = get_nearest_doctors(doctor_specializations)
                
                if not recommended_doctors:
                    print("No matching doctors found.")
                    return render(request, "patient/diseaseform.html", {"error": "No matching doctors found for your symptoms."})
                    
            except Exception as e:
                print(f"\n❌ Error finding doctors: {e}")
                return render(request, "patient/diseaseform.html", {"error": "Error finding doctors. Please try again later."})

            # Store results in session before redirecting
            request.session["diseases"] = diseases
            request.session["doctors"] = [
                {
                    "name": doctor.name,
                    "specialization": doctor.specialization,
                    "experience": doctor.experience,
                    "photo": doctor.photo.url if doctor.photo else "",
                    "available_days": doctor.available_days,
                    "start_time": doctor.start_time.strftime("%H:%M") if doctor.start_time else "",
                    "end_time": doctor.end_time.strftime("%H:%M") if doctor.end_time else "",
                }
                for doctor in recommended_doctors
            ]
            # Store precautions and urgency level in session
            request.session["precautions"] = precautions
            request.session["urgency_level"] = urgency_level

            # Redirect to 'seedoctors' page
            return redirect(reverse("seedoctors"))
            
        except ImportError as e:
            print(f"\n❌ Import Error: {e}")
            return render(request, "patient/diseaseform.html", {"error": "System configuration error. Please contact support."})
        except Exception as e:
            print(f"\n❌ Unexpected Error: {e}")
            return render(request, "patient/diseaseform.html", {"error": "An unexpected error occurred. Please try again later."})

    # GET request - render the form
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
    doctors = request.session.get("doctors", [])  # List of doctor objects
    precautions = request.session.get("precautions", [])
    urgency_level = request.session.get("urgency_level", 0)  # Default to level 1 if not provided
    
    # Define urgency level descriptions for the template
    urgency_descriptions = {
        0: "Self-care only (no doctor visit needed)",
        1: "Schedule a routine appointment (within the next few weeks)",
        2: "Schedule appointment soon (within a week)",
        3: "See a doctor within 1-2 days",
        4: "Seek medical attention promptly (within 24 hours)",
        5: "Emergency (immediate medical attention required)"
    }
    
    # Get the description for the current urgency level
    urgency_description = urgency_descriptions.get(urgency_level, "Schedule a routine appointment")

    # Clear session data after retrieving
    request.session.pop("diseases", None)
    request.session.pop("doctors", None)
    request.session.pop("precautions", None)
    request.session.pop("urgency_level", None)

    return render(
        request,
        "patient/seedoctors.html",
        {
            "diseases": diseases, 
            "doctors": doctors,
            "precautions": precautions,
            "urgency_level": urgency_level,
            "urgency_description": urgency_description
        },
    )