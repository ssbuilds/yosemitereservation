// Initialize Feather icons
document.addEventListener('DOMContentLoaded', () => {
    feather.replace();
});

// Image carousel functionality
let currentImageIndex = 0;
const images = document.querySelectorAll('.image-carousel img');

function showNextImage() {
    images[currentImageIndex].style.display = 'none';
    currentImageIndex = (currentImageIndex + 1) % images.length;
    images[currentImageIndex].style.display = 'block';
}

// Initialize carousel
if (images.length > 0) {
    images.forEach(img => img.style.display = 'none');
    images[0].style.display = 'block';
    setInterval(showNextImage, 5000);
}
