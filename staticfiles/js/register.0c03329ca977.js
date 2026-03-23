// Toggle Password Visibility
document.getElementById("togglePassword").addEventListener("click", function() {
    var id_password = document.getElementById("id_password");
    var type = id_password.getAttribute("type") === "password" ? "text" : "password";
    id_password.setAttribute("type", type);
    this.querySelector("i").classList.toggle("bi-eye");
    this.querySelector("i").classList.toggle("bi-eye-slash");
});

// Show/Hide Additional Fields Based on User Type
document.addEventListener("DOMContentLoaded", function () {

    const userType = document.getElementById("id_user_type");
    const doctorFields = document.getElementById("doctorFields");
    const adminFields = document.getElementById("hospitalAdminFields");
    
    const doctorAlert = document.getElementById("doctoralert");
    const hospitalAdminAlert = document.getElementById("hospitaladminalert");

    if (!userType || !doctorFields || !adminFields) {
        console.error("Required elements not found");
        return;
    }

    userType.addEventListener("change", function () {

        // Hide both sections first
        doctorFields.classList.add("d-none");
        adminFields.classList.add("d-none");
        doctorAlert.classList.add("d-none");
        hospitalAdminAlert.classList.add("d-none");

        // Show doctor fields
        if (this.value === "doctor") {
            doctorFields.classList.remove("d-none");
            doctorAlert.classList.remove("d-none");
        }

        // Show hospital admin fields
        if (this.value === "hospital_admin") {
            adminFields.classList.remove("d-none");
            hospitalAdminAlert.classList.remove("d-none");
        }
    });

});


document.addEventListener("DOMContentLoaded", function () {

    // Remove spaces from first name
    const firstNameInput = document.getElementById("id_first_name");
    if (firstNameInput) {
        firstNameInput.addEventListener("input", function () {
            this.value = this.value.replace(/\s/g, "");
        });
    }

    // Remove spaces from last name
    const lastNameInput = document.getElementById("id_last_name");
    if (lastNameInput) {
        lastNameInput.addEventListener("input", function () {
            this.value = this.value.replace(/\s/g, "");
        });
    }

    // Convert email to lowercase
    const emailInput = document.getElementById("id_email");
    if (emailInput) {
        emailInput.addEventListener("input", function () {
            this.value = this.value.toLowerCase();
            this.value = this.value.replace(/\s/g, "");
        });
    }

});

// Auto-hide messages after 4 seconds
setTimeout(() => {
    document.querySelectorAll('.message').forEach(msg => {
        msg.style.transition = "opacity 0.5s";
        msg.style.opacity = "0";
        setTimeout(() => msg.style.display = "none", 500);
    });
}, 4000);

