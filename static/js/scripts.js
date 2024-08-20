document.addEventListener('DOMContentLoaded', function() {
    // Get the fragment identifier (part after # in the URL)
    var hash = window.location.hash.substring(1); // Remove the #

    // Check if there's a matching element with that id
    if (hash) {
        var section = document.getElementById(hash);
        if (section) {
            // Apply the highlight class
            section.classList.add('highlight');
        }
    }
});
