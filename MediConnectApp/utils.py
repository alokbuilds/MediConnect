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
