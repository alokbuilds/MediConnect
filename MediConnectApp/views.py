from datetime import timedelta, datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from MediConnectApp.models import PatientProfile, DoctorProfile, HospitalAdminProfile, Speciality, Appointment, MedicalRecord, Prescription, DoctorAvailability
from django.utils import timezone
from .utils import get_user_role


#---------------Home Page-----------------------------------
def home(request):
    return render(request,"home.html")
#---------------Service Page--------------------------------
def services_View(request):
    return render(request,"services.html")
#---------------Help Page-----------------------------------
def help_View(request):
    return render(request,"help.html")
#---------------About Us Page-------------------------------
def about_View(request):
    return render(request,"about.html")
#---------------Contact Us Page-----------------------------
def contact_View(request):
    return render(request, "contact.html")



# -------------------------------
# REGISTER (PATIENT/DOCTOR/ADMIN)
# -------------------------------
def register_view(request):

    specialities = Speciality.objects.all()
    context = {
        "specialities": specialities
    }
    if request.method == "POST":

        # Common fields
        user_type = request.POST.get("user_type")  # patient / doctor / hospital_admin
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Password validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/register.html" , context)

        # Username check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "accounts/register.html" , context)

        # Email check
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "accounts/register.html" , context)

        # Create Django User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()


        #patient profile creation
        if user_type == "patient":

            PatientProfile.objects.create(
                user=user,
                phone=phone
            )

            messages.success(request,"Patient registered successfully. Please login to continue.")
            return redirect("login")

        #doctor profile creation
        elif user_type == "doctor":
            qualification = request.POST.get("qualification")
            specialization_id = request.POST.get("specialization")

            # Convert ID to Speciality object
            try:
                specialization_obj = Speciality.objects.get(id=specialization_id) #fetching foreign key object
            except Speciality.DoesNotExist:
                messages.error(request, "Invalid specialization selected.")
                user.delete()
                return render(request, "accounts/register.html" , context)


            experience = request.POST.get("experience")


            DoctorProfile.objects.create(
                user=user,
                phone=phone,
                specialization=specialization_obj,  # ✅ ForeignKey object
                experience=experience,
                qualification=qualification
            )

            messages.success(
                request,
                "Doctor registered successfully. Your account will be activated after admin approval."
            )
            return redirect("login")
        

        #hospital admin profile creation
        elif user_type == "hospital_admin":
            user.is_staff = True     # Hospital admin = staff user
            user.save()

            hospital_name=request.POST.get("hospital_name")
            hospital_code=request.POST.get("hospital_code")
            hospital_address=request.POST.get("hospital_address")

            # Full name creation
            full_name = f"{first_name} {last_name}"

            # HospitalAdminProfile create
            HospitalAdminProfile.objects.create(
                user=user,
                full_name=full_name,
                phone_number=phone,
                hospital_name=hospital_name,
                hospital_code=hospital_code,
                hospital_address=hospital_address
            )

            messages.success(request, "Hospital Admin registered successfully")
            return redirect("login")

        else:
            messages.error(request, "Invalid user type selected.")
            return redirect("register")
    
    return render(request, "accounts/register.html" , context)


# ----------------------------
# LOGIN (PATIENT/DOCTOR/ADMIN)
# ----------------------------
#Role-based Login
def login_view(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        # 1️⃣ Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect("login")

        # 2️⃣ Active check
        if not user.is_active:
            messages.error(request, "Your account is deactivated")
            return redirect("login")

        # 3️⃣ Login (session create)
        login(request, user)

        # 4️⃣ ROLE AUTO-DETECTION FROM DB
        role = get_user_role(user)


        # 5️⃣ Role-based redirect

        # 🔹 Hospital Admin (Sub Admin)
        if role == "django_admin":
            return redirect("/admin/")

        # 🔹 Hospital Admin (Sub Admin)
        elif role == "hospital_admin":
            if not user.hospitaladminprofile.is_approved:
                messages.error(request, "Hospital admin account not approved yet. Please wait for Super Admin approval.")
                return redirect("login")
            
            elif not user.hospitaladminprofile.is_active:
                messages.error(
                    request, 
                    "Hospital admin account is blocked. Contact to Super Admin."
                )
                return redirect("login")
            return redirect("hospital_admin_dashboard")

        # 🔹 Doctor
        elif role == "doctor":
            if not user.doctorprofile.is_approved:
                messages.error(
                    request,
                    "Doctor account not approved yet. Please wait for Hospital Admin or Super Admin approval."
                )
                return redirect("login")
            elif not user.doctorprofile.is_active:
                messages.error(
                    request,
                    "Doctor account is blocked. Contact to Hospital Admin or Super Admin."
                )
                return redirect("login")
            return redirect("doctor_dashboard")

        # 🔹 Patient
        elif role == "patient":
            return redirect("patient_dashboard")

        else:
            messages.error(request, "No role assigned to this account")
            return redirect("login")

    return render(request, "accounts/login.html")


#----------------------------# # # # # # # # # # # # #----------------------------#
#----------------------------#  START PATIENT MODULE #----------------------------#
#----------------------------# # # # # # # # # # # # #----------------------------#


# -------------------------
# PATIENT DASHBOARD
# -------------------------
@login_required(login_url='login')
def patient_dashboard_view(request):
    user = request.user

    # Check if logged-in user has PatientProfile
    if not hasattr(user, 'patientprofile'):
        messages.error(request, "You are not authorized to access Patient Dashboard.")
        return redirect('login')

    patient = user.patientprofile
    today = timezone.now().date()

    # ---------------- COUNTS ----------------

    # Total appointments
    total_appointments = Appointment.objects.filter(
        patient=patient
    ).count()

    # Upcoming appointments (approved & future date)
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        status="approved",
        appointment_date__gte=today
    ).count()

    # Completed appointments
    completed_appointments = Appointment.objects.filter(
        patient=patient,
        status="completed"
    ).count()

    # Pending prescriptions
    # (Assumption: prescription field future me add hoga)
    pending_prescriptions = Appointment.objects.filter(
        patient=patient,
        status="completed",
    ).count()

    # Recent appointments (last 5)
    recent_appointments = Appointment.objects.filter(
        patient=patient
    ).order_by('-created_at')[:5]

    context = {
        "patient": patient,
        "total_appointments": total_appointments,
        "upcoming_appointments": upcoming_appointments,
        "completed_appointments": completed_appointments,
        "pending_prescriptions": pending_prescriptions,
        "recent_appointments": recent_appointments,
    }

    return render(request, 'users/patient/p_dashboard.html', context)

#-------------------------
# BASE CHECK FUNCTION FOR PATIENT (REUSE LOGIC)
#-------------------------
def get_patient(request):
    if not hasattr(request.user, "patientprofile"):
        messages.error(request, "Unauthorized access")
        return None
    return request.user.patientprofile

# -------------------------
# BOOK APPOINTMENT
# -------------------------
@login_required(login_url="login")
def patient_book_appointment_view(request):

    if not hasattr(request.user, "patientprofile"):
        messages.error(request, "Please login as patient.")
        return redirect("login")

    patient = request.user.patientprofile
    doctors = DoctorProfile.objects.filter(is_approved=True, is_active=True)

    today = date.today()
    max_date = today + timedelta(days=7)

    if request.method == "POST":
        doctor_id = request.POST.get("doctor")
        appointment_date = request.POST.get("appointment_date")
        appointment_time = request.POST.get("appointment_time")

        doctor = get_object_or_404(DoctorProfile, id=doctor_id)

        # Convert date & time
        appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        appointment_time = datetime.strptime(appointment_time, "%H:%M").time()

        # Date Validation
        if appointment_date < today:
            messages.error(request, "Back date selection is not allowed.")
            return redirect("patient_book_appointment")

        if appointment_date > max_date:
            messages.error(request, "You can only book appointment within 7 days.")
            return redirect("patient_book_appointment")

        # Day Name Check
        day_name = appointment_date.strftime("%A").lower()

        availability = DoctorAvailability.objects.filter(
            doctor=doctor,
            day=day_name,
            start_time__lte=appointment_time,
            end_time__gte=appointment_time,
            is_active=True
        ).exists()

        if not availability:
            messages.error(request, "Doctor is not available at selected time.")
            return redirect("patient_book_appointment")

        # Prevent Double Booking
        already_booked = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).exists()

        if already_booked:
            messages.error(request, "This time slot is already booked.")
            return redirect("patient_book_appointment")

        # Create Appointment
        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status="pending"
        )

        messages.success(request, "Appointment booked successfully.")
        return redirect("patient_my_appointments")

    context = {
        "doctors": doctors,
        "today_date": today,
        "max_date": max_date,
    }

    return render(
        request,
        "users/patient/p_book_appointment.html",
        context
    )

# -------------------------
# MY APPOINTMENTS
# -------------------------
@login_required(login_url="login")
def my_appointments_view(request):
    patient = get_patient(request)      # BASE CHECK FUNCTION (REUSE LOGIC)
    if not patient:
        return redirect("login")

    appointments = Appointment.objects.filter(patient=patient).order_by("-created_at")

    return render(request, "users/patient/p_my_appointments.html", {
        "appointments": appointments
    })

# -------------------------
# DOCTORS LIST FOR PATIENT
# -------------------------
@login_required(login_url="login")
def doctors_list_view(request):
    patient = get_patient(request)      # BASE CHECK FUNCTION (REUSE LOGIC)
    if not patient:
        return redirect("login")

    doctors = DoctorProfile.objects.filter(is_approved=True).order_by("-created_at")

    return render(request, "users/patient/p_doctors_list.html", {
        "doctors": doctors
    })





# -------------------------
# MEDICAL RECORDS
# -------------------------
@login_required(login_url="login")
def medical_records_view(request):
    patient = get_patient(request)      # BASE CHECK FUNCTION (REUSE LOGIC)
    if not patient:
        return redirect("login")

    records = MedicalRecord.objects.filter(patient=patient)

    return render(request, "users/patient/p_medical_records.html", {
        "records": records
    })


# -------------------------
# PRESCRIPTIONS VIEW
# -------------------------
@login_required(login_url="login")
def prescriptions_view(request):
    patient = get_patient(request)      # BASE CHECK FUNCTION (REUSE LOGIC)
    if not patient:
        return redirect("login")

    prescriptions = Prescription.objects.filter(patient=patient)

    return render(request, "users/patient/p_prescriptions.html", {
        "prescriptions": prescriptions
    })



@login_required(login_url="login")
def patient_prescriptions_view(request):
    """
    Display all prescriptions of the logged-in patient.
    """

    user = request.user

    # Ensure user is a patient
    if not hasattr(user, "patientprofile"):
        messages.error(request, "You are not authorized to access this page.")
        return redirect("login")

    patient_profile = user.patientprofile

    # Fetch patient's prescriptions
    prescriptions = Prescription.objects.filter(
        patient=patient_profile
    ).order_by("-created_at")

    context = {
        "prescriptions": prescriptions
    }

    return render(
        request,
        "users/patient/p_prescriptions.html",
        context
    )

# -------------------------
# PATIENT PROFILE
# -------------------------
@login_required(login_url="login")
def patient_profile_view(request):
    patient = get_patient(request)      # BASE CHECK FUNCTION (REUSE LOGIC)
    if not patient:
        return redirect("login")

    return render(request, "users/patient/p_profile.html", {
        "patient": patient
    })


# -------------------------
# CANCEL APPOINTMENT
# -------------------------
@login_required(login_url="login")
def cancel_appointment(request, appointment_id):
    """
    Allow patient to cancel their own appointment.
    """

    user = request.user

    # Ensure the logged-in user is a patient
    if not hasattr(user, "patientprofile"):
        messages.error(request, "You are not authorized to perform this action.")
        return redirect("login")

    patient_profile = user.patientprofile

    # Fetch the appointment belonging to this patient
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=patient_profile
    )

    # Only pending appointments can be cancelled
    if appointment.status != "pending":
        messages.warning(
            request,
            "This appointment cannot be cancelled."
        )
        return redirect("patient_my_appointments")

    # Soft cancel (do not delete record)
    appointment.status = "cancelled"
    appointment.save()

    messages.success(
        request,
        "Appointment cancelled successfully."
    )

    return redirect("patient_my_appointments")


@login_required(login_url="login")
def update_patient_profile_view(request):
    """
    Allow patient to view and update their own profile.
    """

    user = request.user

    # Ensure logged-in user is a patient
    if not hasattr(user, "patientprofile"):
        messages.error(request, "You are not authorized to access this page.")
        return redirect("login")

    patient_profile = user.patientprofile

    if request.method == "POST":
        # Update User fields
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.save()

        # Update PatientProfile fields
        patient_profile.phone = request.POST.get("phone")
        patient_profile.gender = request.POST.get("gender")
        patient_profile.age = request.POST.get("age") or None
        patient_profile.address = request.POST.get("address")
        patient_profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("update_patient_profile")

    context = {
        "patient": patient_profile
    }

    return render(
        request,
        "users/patient/p_profile.html",
        context
    )


#----------------------------# # # # # # # # # # # #----------------------------#
#----------------------------#  END PATIENT MODULE #----------------------------#
#----------------------------# # # # # # # # # # # #----------------------------#






#----------------------------# # # # # # # # # # # # #----------------------------#
#----------------------------#  START DOCTOR MODULE  #----------------------------#
#----------------------------# # # # # # # # # # # # #----------------------------#


# -------------------------
# DOCTOR DASHBOARD
# -------------------------
@login_required(login_url="login")
def doctor_dashboard_view(request):
    """
    Doctor main dashboard.
    Shows appointment stats and today's appointments.
    """

    user = request.user

    # Ensure logged-in user is a doctor
    if not hasattr(user, "doctorprofile"):
        messages.error(request, "You are not authorized to access this page.")
        return redirect("login")

    doctor = user.doctorprofile
    today = timezone.now().date()

    # Appointment stats
    total_appointments = Appointment.objects.filter(
        doctor=doctor
    ).count()

    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).count()

    pending_appointments = Appointment.objects.filter(
        doctor=doctor,
        status="pending"
    ).count()

    completed_appointments = Appointment.objects.filter(
        doctor=doctor,
        status="completed"
    ).count()

    cancelled_appointments = Appointment.objects.filter(
        doctor=doctor,
        status="cancelled"
    ).count()

    # Today's appointment list
    todays_list = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).order_by("appointment_time")

    context = {
        "doctor": doctor,
        "total_appointments": total_appointments,
        "today_appointments": today_appointments,
        "pending_appointments": pending_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "todays_list": todays_list,
    }

    return render(
        request,
        "users/doctor/d_dashboard.html",
        context
    )




# -------------------------
# DOCTOR VIEW APPOINTMENT
# -------------------------
@login_required(login_url="login")
def doctor_view_appointment(request, appointment_id):
    """
    Read-only appointment details for doctor.
    """

    user = request.user

    # Ensure doctor
    if not hasattr(user, "doctorprofile"):
        messages.error(request, "Unauthorized access.")
        return redirect("login")

    doctor = user.doctorprofile

    # Ownership check
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=doctor
    )

    context = {
        "appointment": appointment
    }

    return render(
        request,
        "users/doctor/d_view_appointment.html",
        context
    )


# -------------------------
# DOCTOR APPROVE APPOINTMENT
# -------------------------
@login_required(login_url="login")
def doctor_approve_appointment_view(request, appointment_id):

    if not hasattr(request.user, "doctorprofile"):
        return redirect("login")

    doctor = request.user.doctorprofile

    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor, status="pending")

    appointment.status = "approved"
    appointment.save()

    messages.success(
        request,
        "Appointment approved successfully."
    )

    return redirect("doctor_appointments")



# -------------------------
# DOCTOR CANCEL APPOINTMENT
# -------------------------
@login_required(login_url="login")
def doctor_cancel_appointment_view(request, appointment_id):
    """
    Doctor can cancel ONLY pending appointments.
    """

    user = request.user

    # Ensure doctor role
    if not hasattr(user, "doctorprofile"):
        messages.error(request, "Unauthorized access.")
        return redirect("login")

    doctor = user.doctorprofile

    # Fetch appointment with ownership check
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=doctor
    )

    # Allow cancel ONLY if status is pending
    if appointment.status != "pending":
        messages.warning(
            request,
            "Only pending appointments can be cancelled."
        )
        return redirect("doctor_appointments")

    # Cancel appointment
    appointment.status = "cancelled"
    appointment.save()

    messages.success(
        request,
        "Appointment cancelled successfully."
    )

    return redirect("doctor_appointments")





# -------------------------
# DOCTOR APPOINTMENTS
# -------------------------
@login_required(login_url="login")
def doctor_appointments_view(request):
    """
    Show all appointments of the logged-in doctor.
    """

    user = request.user

    # Ensure logged-in user is a doctor
    if not hasattr(user, "doctorprofile"):
        messages.error(request, "You are not authorized to access this page.")
        return redirect("login")

    doctor = user.doctorprofile

    # Fetch doctor's appointments
    appointments = Appointment.objects.filter(
        doctor=doctor
    ).order_by("-appointment_date")

    context = {
        "appointments": appointments
    }

    return render(
        request,
        "users/doctor/d_appointments.html",
        context
    )


# -------------------------
# DOCTOR PATIENTS
# -------------------------
@login_required(login_url="login")
def doctor_patients_view(request):
    """
    Show unique patients associated with the logged-in doctor.
    """

    # Step 1: Get logged-in user
    user = request.user

    # Step 2: Ensure user is a doctor
    if not hasattr(user, "doctorprofile"):
        messages.error(request, "You are not authorized to access this page.")
        return redirect("login")

    # Step 3: Fetch doctor profile
    doctor = user.doctorprofile

    # Step 4: Fetch appointments of this doctor
    # This returns a QuerySet of Appointment objects
    appointments = Appointment.objects.filter(doctor=doctor)

    # Step 5: Extract unique patient IDs from appointments
    patient_ids = appointments.values_list("patient_id", flat=True).distinct()

    # Step 6: Fetch PatientProfile objects using those IDs
    # Final QuerySet of patients
    patients = PatientProfile.objects.filter(
        id__in=patient_ids
    ).order_by("user__first_name")

    context = {
        "patients": patients
    }

    return render(
        request,
        "users/doctor/d_patients.html",
        context
    )


# ----------------------------
# DOCTOR VIEW PATIENT HISTORY
# ----------------------------
@login_required(login_url="login")
def doctor_view_patient_history(request, patient_id):
    """
    Show complete medical history of a patient (doctor-specific).
    """

    if not hasattr(request.user, "doctorprofile"):
        return redirect("login")

    doctor = request.user.doctorprofile

    patient = get_object_or_404(
        PatientProfile,
        id=patient_id
    )

    # Appointments with this doctor
    appointments = Appointment.objects.filter(
        doctor=doctor,
        patient=patient
    ).order_by("-appointment_date")

    # Prescriptions given by this doctor
    prescriptions = Prescription.objects.filter(
        doctor=doctor,
        patient=patient
    ).order_by("-created_at")

    context = {
        "patient": patient,
        "appointments": appointments,
        "prescriptions": prescriptions
    }

    return render(
        request,
        "users/doctor/d_patient_history.html",
        context
    )



# -------------------------
# DOCTOR PRESCRIPTIONS
# -------------------------
@login_required(login_url="login")
def doctor_prescriptions_list_view(request):
    """
    Show all prescriptions created by the logged-in doctor.
    """

    user = request.user

    if not hasattr(user, "doctorprofile"):
        messages.error(request, "Unauthorized access.")
        return redirect("login")

    doctor = user.doctorprofile

    # QuerySet: all prescriptions of this doctor
    prescriptions = Prescription.objects.filter(
        doctor=doctor
    ).order_by("-created_at")

    context = {
        "prescriptions": prescriptions
    }

    return render(
        request,
        "users/doctor/d_prescriptions.html",
        context
    )

# -------------------------
# DOCTOR CREATE PRESCRIPTION
# -------------------------

#Create Prescription (Appointment-wise)
@login_required(login_url="login")
def doctor_create_prescription_view(request, appointment_id):
    """
    Create prescription for a specific appointment.
    """

    user = request.user

    if not hasattr(user, "doctorprofile"):
        messages.error(request, "Unauthorized access.")
        return redirect("login")

    doctor = user.doctorprofile

    # Fetch appointment (ownership check)
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=doctor
    )

    # Prevent duplicate prescription
    if hasattr(appointment, "prescription"):
        messages.warning(request, "Prescription already exists.")
        return redirect("doctor_prescriptions")

    if request.method == "POST":
        diagnosis = request.POST.get("diagnosis")
        medicines = request.POST.get("medicines")
        notes = request.POST.get("notes")

        Prescription.objects.create(
            appointment=appointment,
            doctor=doctor,
            patient=appointment.patient,
            diagnosis=diagnosis,
            medicines=medicines,
            notes=notes
        )

        # Update appointment status
        appointment.status = "completed"
        appointment.save()

        messages.success(request, "Prescription created successfully.")
        return redirect("doctor_prescriptions")

    context = {
        "appointment": appointment
    }

    return render(
        request,
        "users/doctor/d_create_prescription.html",
        context
    )


# -------------------------
# DOCTOR MEDICAL RECORDS
# -------------------------
@login_required(login_url="login")
def doctor_medical_records_view(request):
    """
    List of patients for medical records (doctor specific).
    """

    if not hasattr(request.user, "doctorprofile"):
        messages.error(request, "Unauthorized access.")
        return redirect("login")

    doctor = request.user.doctorprofile

    # Get unique patients from appointments
    patient_ids = Appointment.objects.filter(
        doctor=doctor
    ).values_list("patient_id", flat=True).distinct()

    patients = PatientProfile.objects.filter(
        id__in=patient_ids
    )

    context = {
        "patients": patients
    }

    return render(
        request,
        "users/doctor/d_medical_records.html",
        context
    )


# -----------------------------
# DOCTOR MEDICAL RECORDS DETAIL
# -----------------------------
@login_required(login_url="login")
def doctor_patient_medical_record_detail(request, patient_id):
    """
    Detailed medical record of a specific patient.
    """

    if not hasattr(request.user, "doctorprofile"):
        messages.error(request, "Unauthorized access.")
        return redirect("login")

    doctor = request.user.doctorprofile

    patient = get_object_or_404(
        PatientProfile,
        id=patient_id
    )

    # Appointments of this doctor with this patient
    appointments = Appointment.objects.filter(
        doctor=doctor,
        patient=patient
    ).order_by("-appointment_date")

    # Prescriptions given by this doctor to this patient
    prescriptions = Prescription.objects.filter(
        doctor=doctor,
        patient=patient
    ).order_by("-created_at")

    context = {
        "patient": patient,
        "appointments": appointments,
        "prescriptions": prescriptions
    }

    return render(
        request,
        "users/doctor/d_medical_record_detail.html",
        context
    )


# --------------------------------
# DOCTOR AVAILABILITY (ADD & VIEW)
# --------------------------------
@login_required(login_url="login")
def doctor_availability_view(request):
    """
    Doctor can add and view their availability.
    """

    if not hasattr(request.user, "doctorprofile"):
        messages.error(request, "Unauthorized access.")
        return redirect("login")

    doctor = request.user.doctorprofile

    if request.method == "POST":
        day = request.POST.get("day")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        DoctorAvailability.objects.create(
            doctor=doctor,
            day=day,
            start_time=start_time,
            end_time=end_time
        )

        messages.success(request, "Availability added successfully.")
        return redirect("doctor_availability")

    availabilities = DoctorAvailability.objects.filter(
        doctor=doctor,
        is_active=True
    ).order_by("day", "start_time")

    context = {
        "availabilities": availabilities
    }

    return render(
        request,
        "users/doctor/d_availability.html",
        context
    )


# --------------------------------
# DOCTOR AVAILABILITY (DELETE)
# --------------------------------
@login_required(login_url="login")
def delete_doctor_availability(request, availability_id):

    if not hasattr(request.user, "doctorprofile"):
        messages.error(request, "Unauthorized access.")
        return redirect("login")

    doctor = request.user.doctorprofile

    availability = get_object_or_404(
        DoctorAvailability,
        id=availability_id,
        doctor=doctor
    )

    availability.delete()

    messages.success(request, "Availability removed.")
    return redirect("doctor_availability")


# ------------------------
# DOCTOR PROFILE SETTINGS
# ------------------------
@login_required(login_url="login")
def doctor_profile_settings_view(request):
    """
    Doctor can view and update their profile information.
    """

    if not hasattr(request.user, "doctorprofile"):
        messages.error(request, "Unauthorized access.")
        return redirect("login")

    doctor = request.user.doctorprofile
    user = request.user

    if request.method == "POST":
        # Update User table fields
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")

        # Update DoctorProfile fields
        doctor.phone = request.POST.get("phone")
        doctor.qualification = request.POST.get("qualification")
        doctor.experience = request.POST.get("experience")

        user.save()
        doctor.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("doctor_profile_settings")

    context = {
        "doctor": doctor,
        "user": user
    }

    return render(
        request,
        "users/doctor/d_profile_settings.html",
        context
    )




#----------------------------# # # # # # # # # # # #----------------------------#
#----------------------------#  END DOCTOR MODULE  #----------------------------#
#----------------------------# # # # # # # # # # # #----------------------------#






#----------------------------# # # # # # # # # # # # # # # # #----------------------------#
#----------------------------#  START HOSPITAL ADMIN MODULE  #----------------------------#
#----------------------------# # # # # # # # # # # # # # # # #----------------------------#

# -------------------------
# HOSPITAL ADMIN DASHBOARD
# -------------------------

def is_hospital_admin(user):                        # Common HOSPITAL ADMIN CHECK (Reusable)
    return hasattr(user, "hospitaladminprofile")


@login_required(login_url="login")
def hospital_admin_dashboard_view(request):
    user = request.user

    if not is_hospital_admin(user):       # Common HOSPITAL ADMIN CHECK (Reusable)
        messages.error(request, "You are not authorized to access this page.")
        return redirect("login")

    hospital_admin = user.hospitaladminprofile

    # Counts
    total_doctors = DoctorProfile.objects.count()
    approved_doctors = DoctorProfile.objects.filter(is_approved=True).count()

    total_patients = PatientProfile.objects.count()
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status="pending").count()
    cancelled_appointments = Appointment.objects.filter(status="cancelled").count()

    # Recent data
    recent_doctors = DoctorProfile.objects.order_by("-created_at")[:5]
    recent_patients = PatientProfile.objects.order_by("-created_at")[:5]
    recent_appointments = Appointment.objects.order_by("-created_at")[:5]

    context = {
        "hospital_admin": hospital_admin,

        "total_doctors": total_doctors,
        "approved_doctors": approved_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "cancelled_appointments": cancelled_appointments,

        "recent_doctors": recent_doctors,
        "recent_patients": recent_patients,
        "recent_appointments": recent_appointments,
    }

    return render(request, "users/hospital_admin/ha_dashboard.html", context)



#-----DOCTORS MANAGEMENT: Hospital Admin-------
@login_required(login_url="login")
def hospital_admin_doctors_view(request):
    if not is_hospital_admin(request.user):       # Common HOSPITAL ADMIN CHECK (Reusable)
        return redirect("login")

    doctors = DoctorProfile.objects.all()
    return render(
        request,
        "users/hospital_admin/ha_doctors.html",
        {"doctors": doctors}
    )


def approve_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    doctor.is_approved = True
    doctor.save()
    messages.success(request, "Doctor is approved")
    return redirect("hospital_admin_doctors")


def reject_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    doctor.is_approved = False
    doctor.is_active = False
    doctor.save()
    messages.warning(request, "Doctor is rejected")
    return redirect("hospital_admin_doctors")


def block_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    doctor.is_active=False
    doctor.save()
    messages.error(request, "Doctor is blocked")
    return redirect("hospital_admin_doctors")


def unblock_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    doctor.is_active=True
    doctor.save()
    messages.success(request, "Doctor is unblocked")
    return redirect("hospital_admin_doctors")




#------PATIENTS VIEW: Hospital Admin-------
@login_required(login_url="login")
def hospital_admin_patients_view(request):
    if not is_hospital_admin(request.user):       # Common HOSPITAL ADMIN CHECK (Reusable)
        return redirect("login")

    patients = PatientProfile.objects.all()
    return render(
        request,
        "users/hospital_admin/ha_patients.html",
        {"patients": patients}
    )


#------APPOINTMENTS VIEW: Hospital Admin-------
@login_required(login_url="login")
def hospital_admin_appointments_view(request):
    if not is_hospital_admin(request.user):       # Common HOSPITAL ADMIN CHECK (Reusable)
        return redirect("login")

    appointments = Appointment.objects.all().order_by("-created_at")
    
    return render(request, "users/hospital_admin/ha_appointments.html",{"appointments": appointments}
    )

#------VIEW APPOINTMENT: Hospital Admin-------
@login_required(login_url="login")
def hospital_admin_view_appointment(request, appointment_id):

    if not hasattr(request.user, "hospitaladminprofile"):
        messages.error(request, "Unauthorized access")
        return redirect("login")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    return render(
        request,
        "users/hospital_admin/ha_view_appointment.html",
        {"appointment": appointment}
    )



@login_required(login_url="login")
def hospital_admin_specialities_view(request):
    if not is_hospital_admin(request.user):       # Common HOSPITAL ADMIN CHECK (Reusable)
        return redirect("login")

    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            Speciality.objects.create(name=name)
            messages.success(request, "Speciality added successfully.")
        else:
            messages.error(request, "Speciality name is required.")

        return redirect("hospital_admin_specialities")

    specialities = Speciality.objects.all()

    return render(
        request,
        "users/hospital_admin/ha_specialities.html",
        {"specialities": specialities}
    )


@login_required(login_url="login")
def delete_speciality(request, speciality_id):
    if not is_hospital_admin(request.user):       # Common HOSPITAL ADMIN CHECK (Reusable)
        return redirect("login")

    speciality = get_object_or_404(Speciality, id=speciality_id)
    speciality.delete()
    messages.warning(request, "Speciality deleted.")

    return redirect("hospital_admin_specialities")

#------Hospital admin Profile update---------
@login_required(login_url="login")
def hospital_admin_profile_view(request):
    # 🔐 Authorization check
    if not is_hospital_admin(request.user):         # Common HOSPITAL ADMIN CHECK (Reusable)
        messages.error(request, "You are not authorized to access this page.")
        return redirect("login")

    profile = request.user.hospitaladminprofile

    # 📝 Update profile
    if request.method == "POST":
        profile.full_name = request.POST.get("full_name")
        profile.phone_number = request.POST.get("phone_number")
        profile.hospital_name = request.POST.get("hospital_name")
        profile.hospital_code = request.POST.get("hospital_code")
        profile.hospital_address = request.POST.get("hospital_address")

        profile.save()
        messages.success(request, "Hospital Admin profile updated successfully.")

        return redirect("hospital_admin_profile")

    # 👁 View profile
    context = {
        "profile": profile
    }

    return render(
        request,
        "users/hospital_admin/ha_profile.html",
        context
    )



@login_required(login_url="login")
def hospital_admin_reports_view(request):
    # 🔐 Authorization
    if not is_hospital_admin(request.user):
        messages.error(request, "You are not authorized to access this page.")
        return redirect("login")

    # 🔢 Counts
    total_doctors = DoctorProfile.objects.count()
    approved_doctors = DoctorProfile.objects.filter(is_approved=True).count()

    total_patients = PatientProfile.objects.count()

    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status="completed").count()
    pending_appointments = Appointment.objects.filter(status="pending").count()
    approved_appointments = Appointment.objects.filter(status="approved").count()
    cancelled_appointments = Appointment.objects.filter(status="cancelled").count()

    # 📋 Recent Data
    recent_doctors = DoctorProfile.objects.order_by("-created_at")[:5]
    recent_patients = PatientProfile.objects.order_by("-created_at")[:5]
    recent_appointments = Appointment.objects.order_by("-created_at")[:5]

    context = {
        "total_doctors": total_doctors,
        "approved_doctors": approved_doctors,
        "total_patients": total_patients,

        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "pending_appointments": pending_appointments,
        "approved_appointments": approved_appointments,
        "cancelled_appointments": cancelled_appointments,

        "recent_doctors": recent_doctors,
        "recent_patients": recent_patients,
        "recent_appointments": recent_appointments,
    }

    return render(
        request,
        "users/hospital_admin/ha_reports.html",
        context
    )


#----------------------------# # # # # # # # # # # # # # # #----------------------------#
#----------------------------#  END HOSPITAL ADMIN MODULE  #----------------------------#
#----------------------------# # # # # # # # # # # # # # # #----------------------------#





#---------------Logout Page-----------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")

#-------------------Create your views here----------------------------------------------------------

