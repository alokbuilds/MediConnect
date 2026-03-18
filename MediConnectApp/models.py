from django.db import models
from django.contrib.auth.models import User



#-----------Patient Profile Model-----------------------

class PatientProfile(models.Model):

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    patient_id = models.CharField(max_length=10, unique=True, blank=True)
    phone = models.CharField(max_length=15)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-generate Patient ID
        if not self.patient_id:
            last = PatientProfile.objects.order_by('-id').first()
            if last:
                num = int(last.patient_id.replace("PAT", ""))
                self.patient_id = f"PAT{num+1:04d}"
            else:
                self.patient_id = "PAT0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name




# ----------- Speciality Model -----------------------

class Speciality(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

#-----------Doctor Profile Model-----------------------

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    doctor_id = models.CharField(max_length=10, unique=True, blank=True)
    phone = models.CharField(max_length=15)
    specialization = models.ForeignKey(Speciality, on_delete=models.SET_NULL, null=True)
    qualification = models.CharField(max_length=100)
    experience = models.PositiveIntegerField()

    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-generate Doctor ID
        if not self.doctor_id:
            last = DoctorProfile.objects.order_by('-id').first()
            if last:
                num = int(last.doctor_id.replace("DOC", ""))
                self.doctor_id = f"DOC{num+1:04d}"
            else:
                self.doctor_id = "DOC0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
    

#-----------Hospital Admin Profile Model-----------------------

class HospitalAdminProfile(models.Model):
    # Django ka default User (username, password, email)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Extra fields for Hospital Admin
    admin_id = models.CharField(max_length=10, unique=True, blank=True)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

     # Hospital Info
    hospital_name = models.CharField(max_length=150, blank=True, null=True)
    hospital_code = models.CharField(max_length=20, blank=True, null=True)
    hospital_address = models.TextField(blank=True, null=True)


    # Status fields
    is_approved = models.BooleanField(default=False)  # approved/rejected
    is_active = models.BooleanField(default=True)   # active/inactive Hospital Admin
    created_at = models.DateTimeField(auto_now_add=True)  # first time
    updated_at = models.DateTimeField(auto_now=True)      # every update

    # autuo-generate admin id
    def save(self, *args, **kwargs):
        # Auto-generate Admin ID
        if not self.admin_id:
            last = HospitalAdminProfile.objects.order_by('-id').first()
            if last:
                num = int(last.admin_id.replace("HAD", ""))
                self.admin_id = f"HAD{num+1:04d}"
            else:
                self.admin_id = "HAD0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.admin_id} - {self.hospital_name}"


#-----------Appointment Model-----------------------

class Appointment(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    appointment_id = models.CharField(max_length=10, unique=True, blank=True)

    # Patient who booked the appointment
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)

    # Doctor with whom appointment is booked
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.appointment_id:
            last = Appointment.objects.order_by('-appointment_id').first()
            if last and last.appointment_id:
                num = int(last.appointment_id.replace("APT", ""))
                self.appointment_id = f"APT{num+1:04d}"
            else:
                self.appointment_id = "APT0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.appointment_id



#-----------MedicalRecord Model-----------------------

class MedicalRecord(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)

    diagnosis = models.TextField()
    notes = models.TextField(blank=True)

    record_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Record - {self.patient.patient_id}"


#-----------Prescription Model-----------------------
class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)

    # TEMPORARILY allow null
    diagnosis = models.TextField(blank=True, null=True)

    medicines = models.TextField()
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Prescription - {self.patient}"


#-----------Doctor Availability Model-----------------------
class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="availabilities")

    day = models.CharField(max_length=10,
        choices=[
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        ]
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doctor} - {self.day} ({self.start_time}-{self.end_time})"
    




    

'''
#-----------Doctor Hospital Mapping Model-----------------------

class DoctorHospital(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    hospital_admin = models.ForeignKey(HospitalAdminProfile, on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doctor.doctor_id} - {self.hospital_admin.hospital_name}"



#-----------Doctor Availability Model-----------------------

class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)

    day = models.CharField(max_length=20)  # Monday, Tuesday etc.
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor.doctor_id} - {self.day}"


#-----------Notification Model-----------------------

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


'''


