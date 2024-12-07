/* ========================== 
   Carousel (Přepínání obrázků)
========================== */

let currentSlide = 0;
const slides = document.querySelectorAll('.slide');
const indicators = document.querySelectorAll('.indicator');

// Funkce pro přepnutí na konkrétní obrázek
function goToSlide(slideIndex) {
    slides[currentSlide].classList.remove('active'); // Skrytí aktuálního obrázku
    indicators[currentSlide].classList.remove('active'); // Skrytí indikátoru aktuálního obrázku

    currentSlide = slideIndex; // Nastavení nového indexu obrázku
    slides[currentSlide].classList.add('active'); // Zobrazení nového obrázku
    indicators[currentSlide].classList.add('active'); // Aktivace indikátoru
}

// Automatické přepínání obrázků každých 8 sekund
setInterval(() => {
    let nextSlide = (currentSlide + 1) % slides.length; // Přepnutí na další obrázek
    goToSlide(nextSlide);
}, 8000);


/* ========================== 
   Ovládání postranního menu
========================== */

// Funkce pro otevření/zavření menu
function toggleMenu() {
    const sideMenu = document.getElementById("sideMenu");
    const overlay = document.getElementById("overlay");
    sideMenu.classList.toggle("open"); // Přepnutí třídy 'open' pro zobrazení menu
    overlay.classList.toggle("active"); // Zobrazení/zastavení overlay
}

// Přidání posluchače události pro tlačítko otevření menu
document.getElementById("btn_menu").addEventListener("click", toggleMenu);


/* ========================== 
   Ovládání filtrů (rozbalení a sbalení)
========================== */

// Funkce pro rozbalení a sbalení filtrů
document.addEventListener("DOMContentLoaded", () => {
    const toggleButtons = document.querySelectorAll(".toggle-btn");

    toggleButtons.forEach(button => {
        button.addEventListener("click", () => {
            const filterGroup = button.closest(".filters_item");
            const filterBody = filterGroup.querySelector(".subfilters");

            // Změna zobrazení filtrů
            if (filterBody.style.display === "none" || !filterBody.style.display) {
                filterBody.style.display = "flex"; // Rozbalení
                button.textContent = "−"; // Změna textu na "−"
            } else {
                filterBody.style.display = "none"; // Sbalení
                button.textContent = "+"; // Změna textu na "+"
            }
        });
    });
});


/* ========================== 
   Stránkování (Zobrazení pouze určitého počtu položek)
========================== */

document.addEventListener("DOMContentLoaded", () => {
    const bikes = document.querySelectorAll(".bike"); // Seznam všech kol
    const bikesPerPage = 12; // Počet kol na jednu stránku
    const paginationContainer = document.getElementById("pagination");

    // Funkce pro zobrazení konkrétní stránky
    const displayPage = (page) => {
        bikes.forEach((bike, index) => {
            if (index >= (page - 1) * bikesPerPage && index < page * bikesPerPage) {
                bike.style.display = "flex"; // Zobrazení kola
            } else {
                bike.style.display = "none"; // Skrytí kola
            }
        });
    };

    // Funkce pro nastavení stránkovací navigace
    const setupPagination = () => {
        const totalPages = Math.ceil(bikes.length / bikesPerPage); // Počet stránek
        paginationContainer.innerHTML = ""; // Vymazání předchozích stránkovacích odkazů
        for (let i = 1; i <= totalPages; i++) {
            const pageLink = document.createElement("a");
            pageLink.href = "#";
            pageLink.textContent = i; // Číslo stránky
            if (i === 1) pageLink.classList.add("active"); // Aktivace první stránky

            pageLink.addEventListener("click", (e) => {
                e.preventDefault();
                document.querySelector(".pages a.active")?.classList.remove("active"); // Odebrání aktivity z předchozí stránky
                pageLink.classList.add("active"); // Nastavení nové stránky jako aktivní
                displayPage(i); // Zobrazení vybrané stránky
            });

            paginationContainer.appendChild(pageLink); // Přidání odkazu na stránku
        }
    };

    // Inicializace
    displayPage(1); // Zobrazení první stránky
    setupPagination(); // Nastavení stránkování
});


/* ========================== 
   Řazení položek (Podle různých kritérií)
========================== */

document.addEventListener("DOMContentLoaded", () => {
    const sortingButton = document.getElementById("sorting_btn");
    const sortingOptions = sortingButton.querySelector(".sorting-options");
    const bikes = document.querySelectorAll(".bike");

    // Otevření/zakrytí seznamu možností pro řazení
    sortingButton.addEventListener("click", (e) => {
        e.stopPropagation();
        sortingOptions.style.display = sortingOptions.style.display === "none" ? "block" : "none";
    });

    // Zavření dropdownu při kliknutí mimo něj
    document.addEventListener("click", () => {
        sortingOptions.style.display = "none";
    });

    // Funkce pro řazení položek podle vybraného kritéria
    const sortBikes = (criteria) => {
        const bikesContainer = document.querySelector(".bike_collection");
        const bikesArray = Array.from(bikes);

        bikesArray.sort((a, b) => {
            if (criteria === "name") {
                return a.querySelector("h2").textContent.localeCompare(b.querySelector("h2").textContent); // Řazení podle názvu
            } else if (criteria === "type") {
                return a.querySelector("h4").textContent.localeCompare(b.querySelector("h4").textContent); // Řazení podle typu
            } else if (criteria === "price") {
                return parseInt(a.querySelector("p").textContent) - parseInt(b.querySelector("p").textContent); // Řazení podle ceny
            } else if (criteria === "availability") {
                return (b.querySelector(".fa-circle-check") ? 1 : 0) - (a.querySelector(".fa-circle-check") ? 1 : 0); // Řazení podle dostupnosti
            }
        });

        // Vyčištění a přeuspořádání položek
        bikesContainer.innerHTML = "";
        bikesArray.forEach(bike => bikesContainer.appendChild(bike)); // Zobrazení přeuspořádaných kol
    };

    // Posluchač pro výběr kritéria řazení
    sortingOptions.addEventListener("click", (e) => {
        if (e.target.tagName === "LI") {
            sortBikes(e.target.getAttribute("data-sort"));
            sortingOptions.style.display = "none"; // Skrytí seznamu po výběru
        }
    });
});


/* ========================== 
   Filtrování položek (Podle zvolených filtrů)
========================== */

document.addEventListener("DOMContentLoaded", () => {
    const filterInputs = document.querySelectorAll(".subfilters input[type='checkbox']");
    const bikes = document.querySelectorAll(".bike");

    // Funkce pro aplikování filtrů
    const filterBikes = () => {
        const filters = {};

        // Uložení aktivních filtrů
        document.querySelectorAll(".filters_item").forEach(filterGroup => {
            const category = filterGroup.querySelector(".filter_header span").textContent.toLowerCase();
            const checkedValues = Array.from(filterGroup.querySelectorAll("input[type='checkbox']:checked"))
                .map(input => input.parentElement.textContent.trim().toLowerCase());

            if (checkedValues.length) {
                filters[category] = checkedValues; // Uložení filtrovaných hodnot
            }
        });

        // Aplikování filtrů na zobrazené položky
        bikes.forEach(bike => {
            const matches = Object.entries(filters).every(([category, values]) => {
                const bikeCategoryValue = bike.dataset[category] ? bike.dataset[category].toLowerCase() : ""; 

                // Filtrování podle každé kategorie
                if (category === "kategorie") {
                    return values.includes(bikeCategoryValue); // Filtrování podle kategorie
                }
                if (category === "velikost") {
                    return values.includes(bikeCategoryValue); // Filtrování podle velikosti
                }
                if (category === "material rámu") {
                    return values.includes(bikeCategoryValue); // Filtrování podle materiálu rámu
                }
                if (category === "typ brzdy") {
                    return values.includes(bikeCategoryValue); // Filtrování podle typu brzdy
                }
                if (category === "znacka") {
                    return values.includes(bikeCategoryValue); // Filtrování podle značky
                }
                if (category === "barva") {
                    return values.includes(bikeCategoryValue); // Filtrování podle barvy
                }

                return true; // Pokud není žádný filtr pro tuto kategorii
            });

            bike.style.display = matches ? "flex" : "none"; // Zobrazení/skrytí kola podle filtru
        });
    };

    // Aplikování filtrů hned po změně checkboxu
    filterInputs.forEach(input => {
        input.addEventListener("change", filterBikes);
    });

    // Inicializace filtrů při načtení stránky
    filterBikes();
});




