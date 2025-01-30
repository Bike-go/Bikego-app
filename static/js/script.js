/* Image roller */

let currentSlide = 0;
const slides = document.querySelectorAll('.slide');
const indicators = document.querySelectorAll('.indicator');

function goToSlide(slideIndex) {
    slides[currentSlide].classList.remove('active');
    indicators[currentSlide].classList.remove('active');

    currentSlide = slideIndex;
    slides[currentSlide].classList.add('active');
    indicators[currentSlide].classList.add('active');
}

setInterval(() => {
    let nextSlide = (currentSlide + 1) % slides.length;
    goToSlide(nextSlide);
}, 8000);

function toggleMenu() {
    const sideMenu = document.getElementById("sideMenu");
    const overlay = document.getElementById("overlay");
    sideMenu.classList.toggle("open");
    overlay.classList.toggle("active");
}

// Добавьте обработчик события для кнопки меню
document.getElementById("btn_menu").addEventListener("click", toggleMenu);
