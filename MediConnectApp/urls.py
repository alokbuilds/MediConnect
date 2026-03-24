from django.urls import path
from MediConnectApp import views #from MediConnectApp import views

urlpatterns = [    
    path('', views.home, name="home"),

    # Authentication
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Home Pages    
    path('services', views.services_View, name='services'),
    path('about-us', views.about_View, name='about'),
    path('help', views.help_View, name='help'),
    path('contact-us', views.contact_View, name='contact'),

    # Patient URLs
    path("patient/dashboard/", views.patient_dashboard_view, name="patient_dashboard"),
    path("patient/book-appointment/", views.patient_book_appointment_view, name="patient_book_appointment"),
    path("patient/my-appointment/cancel/<int:appointment_id>/", views.cancel_appointment, name="cancel_appointment"),
    path("patient/my-appointments/", views.my_appointments_view, name="patient_my_appointments"),
    path("patient/doctors-list/", views.doctors_list_view, name="patient_doctors"),
    path("patient/medical-records/", views.medical_records_view, name="patient_medical_records"),
    path("patient/prescriptions/", views.patient_prescriptions_view, name="patient_prescriptions"),
    path("patient/profile/", views.patient_profile_view, name="patient_profile"),
    path("patient/profile/update/", views.update_patient_profile_view, name="update_patient_profile"),


    # Doctor URLs
    path("doctor/dashboard/", views.doctor_dashboard_view, name="doctor_dashboard"),

    path("doctor/appointments/", views.doctor_appointments_view, name="doctor_appointments"),

    path("doctor/patients/", views.doctor_patients_view, name="doctor_patients"),
    path("doctor/patient-history/<int:patient_id>/", views.doctor_view_patient_history, name="doctor_view_patient_history"),


    path("doctor/prescriptions/", views.doctor_prescriptions_list_view, name="doctor_prescriptions"),
    path("doctor/appointments/view/<int:appointment_id>/", views.doctor_view_appointment, name="doctor_view_appointment"),
    path("doctor/appointments/approve/<int:appointment_id>/", views.doctor_approve_appointment_view, name="doctor_approve_appointment"),
    path("doctor/appointments/cancel/<int:appointment_id>/", views.doctor_cancel_appointment_view, name="doctor_cancel_appointment"),
    path("doctor/prescriptions/create/<int:appointment_id>/", views.doctor_create_prescription_view, name="doctor_create_prescription"),

    path("doctor/medical-records/", views.doctor_medical_records_view, name="doctor_medical_records"),
    path("doctor/medical-records/<int:patient_id>/", views.doctor_patient_medical_record_detail, name="doctor_patient_medical_record_detail"),

    path("doctor/availability/", views.doctor_availability_view, name="doctor_availability"),
    path("doctor/availability/delete/<int:availability_id>/", views.delete_doctor_availability, name="delete_doctor_availability"),

    path("doctor/profile-settings/", views.doctor_profile_settings_view, name="doctor_profile_settings"),

    ###########################
    #   Hospital Admin URLs   #
    ###########################
    path("hospital-admin/dashboard/", views.hospital_admin_dashboard_view, name="hospital_admin_dashboard"),

    path("hospital-admin/doctors/", views.hospital_admin_doctors_view, name="hospital_admin_doctors"),
    path("hospital-admin/doctor/approve/<int:doctor_id>/", views.approve_doctor, name="approve_doctor"),
    path("hospital-admin/doctor/reject/<int:doctor_id>/", views.reject_doctor, name="reject_doctor"),
    path("hospital-admin/doctor/block/<int:doctor_id>/", views.block_doctor, name="block_doctor"),
    path("hospital-admin/doctor/unblock/<int:doctor_id>/", views.unblock_doctor, name="unblock_doctor"),

    path("hospital-admin/patients/", views.hospital_admin_patients_view, name="hospital_admin_patients"),

    path("hospital-admin/appointments/", views.hospital_admin_appointments_view, name="hospital_admin_appointments"),
    path("hospital-admin/appointment/view/<int:appointment_id>/", views.hospital_admin_view_appointment, name="hospital_admin_view_appointment"),

    path("hospital-admin/specialities/", views.hospital_admin_specialities_view, name="hospital_admin_specialities"),
    path("hospital-admin/specialities/delete/<int:speciality_id>/", views.delete_speciality, name="delete_speciality"),

    path("hospital-admin/profile/", views.hospital_admin_profile_view, name="hospital_admin_profile"),

    path("hospital-admin/reports/", views.hospital_admin_reports_view, name="hospital_admin_reports"),
]

