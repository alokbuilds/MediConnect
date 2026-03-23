// Auto-hide messages after 4 seconds
setTimeout(() => {
    document.querySelectorAll('.message').forEach(msg => {
        msg.style.transition = "opacity 0.5s";
        msg.style.opacity = "0";
        setTimeout(() => msg.style.display = "none", 500);
    });
}, 4000);

// Show / Hide Password using Bootstrap toggle icon
const toggle = document.getElementById("togglePassword");
const password = document.getElementById("id_password");

toggle.addEventListener("click", function () {
    const type = password.type === "password" ? "text" : "password";
    password.type = type;
    this.innerHTML = type === "password"
        ? '<i class="bi bi-eye"></i>'
        : '<i class="bi bi-eye-slash"></i>';
});
