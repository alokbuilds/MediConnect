from .models import PatientProfile, DoctorProfile, HospitalAdminProfile

def get_user_role(user):
    if user.is_superuser:
        return "django_admin"

    if hasattr(user, "hospitaladminprofile"):
        return "hospital_admin"

    if hasattr(user, "doctorprofile"):
        return "doctor"

    if hasattr(user, "patientprofile"):
        return "patient"

    return None



def is_patient(user):
    return PatientProfile.objects.filter(user=user).exists()

def is_doctor(user):
    return DoctorProfile.objects.filter(user=user).exists()

def is_admin(user):
    return HospitalAdminProfile.objects.filter(user=user).exists()