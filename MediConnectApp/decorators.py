from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .utils import is_patient, is_doctor, is_admin


def patient_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if not is_patient(request.user):
            messages.error(request, "Access denied (Patient only)")
            return redirect("login")

        return view_func(request, *args, **kwargs)
    return wrapper


def doctor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if not is_doctor(request.user):
            messages.error(request, "Access denied (Doctor only)")
            return redirect("login")

        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if not is_admin(request.user):
            messages.error(request, "Access denied (Admin only)")
            return redirect("login")

        return view_func(request, *args, **kwargs)
    return wrapper