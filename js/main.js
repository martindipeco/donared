// js/navbar-scroll.js
let lastScrollTop = 0;
const navbar = document.querySelector('.navbar');
const threshold = 50; // Cambia este número si quieres más o menos sensibilidad

let accumulatedScroll = 0;
let isNavbarHidden = false;

window.addEventListener('scroll', function () {
    const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
    const scrollDelta = currentScroll - lastScrollTop;

    // Scroll hacia abajo
    if (scrollDelta > 0) {
        accumulatedScroll += scrollDelta;
        if (accumulatedScroll > threshold && !isNavbarHidden) {
            navbar.style.top = "-100px";
            isNavbarHidden = true;
        }
    }
    // Scroll hacia arriba
    else {
        accumulatedScroll -= scrollDelta; // delta es negativo
        if (accumulatedScroll > threshold && isNavbarHidden) {
            navbar.style.top = "0";
            isNavbarHidden = false;
        }
    }

    lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
});

// Carrusel manual con botones
let currentSlide = 0;
const slides = document.querySelectorAll('.carousel-image');
const totalSlides = slides.length;

function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === index);
    });
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    showSlide(currentSlide);
}

function prevSlide() {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    showSlide(currentSlide);
}

// Inicializa el primer slide
document.addEventListener('DOMContentLoaded', () => {
    showSlide(currentSlide);
});
