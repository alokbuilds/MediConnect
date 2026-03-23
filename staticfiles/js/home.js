// Auto-hide messages after 4 seconds
setTimeout(() => {
    document.querySelectorAll('.messages').forEach(msg => {
        msg.style.transition = "opacity 0.5s";
        msg.style.opacity = "0";
        setTimeout(() => msg.style.display = "none", 500);
    });
}, 4000);

// Enable/Disable Search Button based on input
function toggleSearchButton() {
    var searchInput = document.getElementById("searchInput");
    var searchButton = document.getElementById("searchButton");

    // Enable the button if the input has a value, disable otherwise
    searchButton.disabled = !searchInput.value.trim();
}

