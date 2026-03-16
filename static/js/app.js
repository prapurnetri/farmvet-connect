// FarmVet Connect - Client-side JS
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide success alerts after 5 seconds
    document.querySelectorAll('.alert-success').forEach(function(el) {
        setTimeout(function() {
            el.style.transition = 'opacity 0.5s';
            el.style.opacity = '0';
            setTimeout(function() { el.remove(); }, 500);
        }, 5000);
    });
});
