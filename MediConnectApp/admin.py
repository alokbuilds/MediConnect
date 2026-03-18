from django.contrib import admin
from .models import PatientProfile, DoctorProfile, HospitalAdminProfile, Appointment, Speciality, Prescription, DoctorAvailability

# Register your models here.


class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("patient_id", "user", "phone", "created_at")
    search_fields = ("patient_id", "user__first_name", "user__username")
    list_filter = ("created_at",)

admin.site.register(PatientProfile, PatientProfileAdmin)

class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("doctor_id", "user", "is_approved", "is_active", "created_at", "specialization", "phone", "experience")
    search_fields = ("doctor_id", "user__first_name", "user__username", "specialization")
    list_filter = ("specialization", "created_at")

admin.site.register(DoctorProfile, DoctorProfileAdmin)

class HospitalAdminProfileAdmin(admin.ModelAdmin):
    list_display = ("admin_id", "user", "full_name", "is_approved", "is_active", "hospital_code", "hospital_name", "phone_number", "updated_at", "created_at")
    search_fields = ("admin_id", "full_name", "hospital_name", "hospital_code")
    list_filter = ("hospital_name", "created_at")

admin.site.register(HospitalAdminProfile, HospitalAdminProfileAdmin)

class SpecialityAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)

admin.site.register(Speciality, SpecialityAdmin)

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("appointment_id", "patient", "doctor", "appointment_date", "appointment_time", "status", "created_at")
    search_fields = ("patient__patient_id", "doctor__doctor_id")
    list_filter = ("status", "appointment_date", "created_at")

admin.site.register(Appointment, AppointmentAdmin)

class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("appointment", "doctor", "patient", "created_at")
    search_fields = ("appointment__appointment_id", "doctor__doctor_id", "patient__patient_id")
    list_filter = ("created_at",)

admin.site.register(Prescription, PrescriptionAdmin)

class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("doctor", "day", "start_time", "end_time", "is_active", "created_at")
    search_fields = ("doctor__doctor_id",)
    list_filter = ("day", "is_active", "created_at")

admin.site.register(DoctorAvailability, DoctorAvailabilityAdmin)