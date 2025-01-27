/* ========================== 
   Ovládání postranního menu
========================== */

document.addEventListener('DOMContentLoaded', function() {
    const sideMenu = document.getElementById("sideMenu");
    const overlay = document.getElementById("overlay");
    const btnMenu = document.getElementById("btn_menu");

    btnMenu.addEventListener("click", toggleMenu);

    overlay.addEventListener("click", closeMenu);

    document.addEventListener("click", function(event) {
        if (!sideMenu.contains(event.target) && !btnMenu.contains(event.target)) {
            closeMenu();
        }
    });

    function toggleMenu() {
        sideMenu.classList.toggle("open");
        overlay.classList.toggle("active");
    }

    function closeMenu() {
        sideMenu.classList.remove("open");
        overlay.classList.remove("active");
    }
});



/* ========================== 
   Carousel (Přepínání obrázků)
========================== */


document.addEventListener('DOMContentLoaded', () => {
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

    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => goToSlide(index));
    });

    setInterval(() => {
        let nextSlide = (currentSlide + 1) % slides.length;
        goToSlide(nextSlide);
    }, 8000);
});


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
    const bikesPerPage = 8; // Počet kol na jednu stránku
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
   Admin menu script
========================== */

// Funkce pro otevření modálního okna pro editaci uživatele
function openEditUserModal(userId) {
    // Nastavíme modal pro uživatele podle ID (mohli bychom načítat data z serveru)
    document.getElementById('editUserModal').style.display = 'block';
    // Můžeme zde třeba přidat naplnění polí daty konkrétního uživatele
}

// Funkce pro otevření modálního okna pro editaci novinky
function openEditNewsModal(newsId) {
    document.getElementById('editNewsModal{{newsId}}').style.display = 'block';
    // Můžeme přidat načítání dat konkrétní novinky
}

// Funkce pro otevření modálního okna pro editaci biků
function openEditBikeModal(bikeId) {
    document.getElementById('editBikeModal').style.display = 'block';
    // Můžeme přidat načítání dat o konkrétním biku
}

// Funkce pro zavření modálního okna
function closeEditModal() {
    // Zavře všechny modální okna
    document.getElementById('editUserModal').style.display = 'none';
    document.getElementById('editNewsModal').style.display = 'none';
    document.getElementById('editBikeModal').style.display = 'none';
}

// Funkce pro změnu aktivního menu v sidebaru
function setActiveMenu(item) {
    let menuItems = document.querySelectorAll('.sidebar .list-group-item');
    menuItems.forEach(function (menuItem) {
        menuItem.classList.remove('active');
    });
    item.classList.add('active');
}

// Funkce pro odstranění uživatele
function deleteUser(userId) {
    if (confirm("Opravdu chcete odstranit tohoto uživatele?")) {
        // Volání serveru pro odstranění uživatele
        console.log("Uživatel s ID " + userId + " byl odstraněn.");
        // Zde bychom mohli použít AJAX pro odeslání požadavku na server pro odstranění
    }
}

// Funkce pro odstranění novinky
function deleteNews(newsId) {
    if (confirm("Opravdu chcete odstranit tuto novinku?")) {
        console.log("Novinka s ID " + newsId + " byla odstraněna.");
        // Opět bychom použili AJAX pro odeslání požadavku na server pro odstranění
    }
}

// Funkce pro odstranění biku
function deleteBike(bikeId) {
    if (confirm("Opravdu chcete odstranit tento bike?")) {
        console.log("Bike s ID " + bikeId + " byl odstraněn.");
        // Pro odstranění biku by se použil AJAX požadavek na server
    }
}

function openNewsModal() {
    document.getElementById('newsModal').style.display = 'block';
}

function openBikeModal() {
    document.getElementById('bikeModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}




/* ========================== 
   pujceni a vraceni kol
========================== */

// Mock API call to get rented bike data
async function fetchRentedBikes() {
    return [
        { id: 'B002', user: 'Jan Novak', time: '15:00', price: '200 Kč' },
        { id: 'B005', user: 'Eva Malá', time: '16:00', price: '150 Kč' }
    ];
}

// Mock API call to get ordered bike data
async function fetchOrderedBikes() {
    return [
        { id: 'B007', user: 'Karel Dvořák', date: '2024-12-15', time: '10:00' },
        { id: 'B008', user: 'Lucie Novotná', date: '2024-12-15', time: '11:30' }
    ];
}

// Populate rented bikes table
async function populateRentedBikes() {
    const rentedBikes = await fetchRentedBikes();
    const tableBody = document.querySelector('#rentedBikesTable tbody');
    const returnBikeSelect = document.querySelector('#returnBikeId');

    tableBody.innerHTML = '';
    returnBikeSelect.innerHTML = '<option value="">Vyberte ID kola</option>';

    rentedBikes.forEach(bike => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${bike.id}</td>
            <td>${bike.user}</td>
            <td>${bike.time}</td>
            <td>${bike.price}</td>
        `;
        tableBody.appendChild(row);

        const option = document.createElement('option');
        option.value = bike.id;
        option.textContent = bike.id;
        returnBikeSelect.appendChild(option);
    });
}

// Populate ordered bikes table
async function populateOrderedBikes() {
    const orderedBikes = await fetchOrderedBikes();
    const tableBody = document.querySelector('#orderedBikesTable tbody');
    const rentalBikeSelect = document.querySelector('#rentalBikeId');

    tableBody.innerHTML = '';
    rentalBikeSelect.innerHTML = '<option value="">Vyberte ID kola</option>';

    orderedBikes.forEach(bike => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${bike.id}</td>
            <td>${bike.user}</td>
            <td>${bike.date}</td>
            <td>${bike.time}</td>
        `;
        tableBody.appendChild(row);

        const option = document.createElement('option');
        option.value = bike.id;
        option.textContent = bike.id;
        rentalBikeSelect.appendChild(option);
    });
}

// Call populate functions on page load
document.addEventListener('DOMContentLoaded', () => {
    populateRentedBikes();
    populateOrderedBikes();
});


/* ========================== 
   servis
========================== */
document.addEventListener('DOMContentLoaded', function() {
    const updateButtons = document.querySelectorAll('.update-status');
    
    updateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bikeId = this.getAttribute('data-bike-id');
            const statusSelect = document.querySelector(`.bike-status[data-bike-id="${bikeId}"]`);
            const newStatus = statusSelect.value;

            // Odeslání AJAX požadavku na server pro aktualizaci statusu
            fetch('/update-bike-status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ bike_id: bikeId, status: newStatus })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Status úspěšně změněn.');
                } else {
                    alert('Chyba při změně statusu.');
                }
            })
            .catch(error => {
                alert('Došlo k chybě při komunikaci se serverem.');
            });
        });
    });
});


function togglePassword(passwordFieldId, toggleIconId) {

    const passwordField = document.getElementById(passwordFieldId);

    const toggleIcon = document.getElementById(toggleIconId);

/* ========================== 
   Admin menu script
========================== */

// Funkce pro otevření modálního okna pro editaci uživatele
function openEditUserModal(userId) {
    // Nastavíme modal pro uživatele podle ID (mohli bychom načítat data z serveru)
    document.getElementById('editUserModal').style.display = 'block';
    // Můžeme zde třeba přidat naplnění polí daty konkrétního uživatele
}

// Funkce pro otevření modálního okna pro editaci novinky
function openEditNewsModal(newsId) {
    document.getElementById('editNewsModal').style.display = 'block';
    // Můžeme přidat načítání dat konkrétní novinky
}

// Funkce pro otevření modálního okna pro editaci biků
function openEditBikeModal(bikeId) {
    document.getElementById('editBikeModal').style.display = 'block';
    // Můžeme přidat načítání dat o konkrétním biku
}

// Funkce pro zavření modálního okna
function closeEditModal() {
    // Zavře všechny modální okna
    document.getElementById('editUserModal').style.display = 'none';
    document.getElementById('editNewsModal').style.display = 'none';
    document.getElementById('editBikeModal').style.display = 'none';
}

// Funkce pro změnu aktivního menu v sidebaru
function setActiveMenu(item) {
    let menuItems = document.querySelectorAll('.sidebar .list-group-item');
    menuItems.forEach(function (menuItem) {
        menuItem.classList.remove('active');
    });
    item.classList.add('active');
}

// Funkce pro odstranění uživatele
function deleteUser(userId) {
    if (confirm("Opravdu chcete odstranit tohoto uživatele?")) {
        // Volání serveru pro odstranění uživatele
        console.log("Uživatel s ID " + userId + " byl odstraněn.");
        // Zde bychom mohli použít AJAX pro odeslání požadavku na server pro odstranění
    }
}

// Funkce pro odstranění novinky
function deleteNews(newsId) {
    if (confirm("Opravdu chcete odstranit tuto novinku?")) {
        console.log("Novinka s ID " + newsId + " byla odstraněna.");
        // Opět bychom použili AJAX pro odeslání požadavku na server pro odstranění
    }
}

// Funkce pro odstranění biku
function deleteBike(bikeId) {
    if (confirm("Opravdu chcete odstranit tento bike?")) {
        console.log("Bike s ID " + bikeId + " byl odstraněn.");
        // Pro odstranění biku by se použil AJAX požadavek na server
    }
}

function openNewsModal() {
    document.getElementById('newsModal').style.display = 'block';
}

function openBikeModal() {
    document.getElementById('bikeModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}


    // Toggle the type attribute

    if (passwordField.type === "password") {

        passwordField.type = "text";

        toggleIcon.classList.remove('fa-eye');

        toggleIcon.classList.add('fa-eye-slash');

    } else {

        passwordField.type = "password";

        toggleIcon.classList.remove('fa-eye-slash');

        toggleIcon.classList.add('fa-eye');

    }

}

/* ========================== 
   Profile page modalnni okna
========================== */

// Get modal elements
const editProfileModal = document.getElementById('editProfileModal');
const settingsModal = document.getElementById('settingsModal');

// Get buttons
const editProfileBtn = document.getElementById('editProfileBtn');
const settingsBtn = document.getElementById('settingsBtn');

// Get close buttons
const closeButtons = document.querySelectorAll('.modal .close');

// Event listeners to open modals
editProfileBtn.addEventListener('click', () => {
    editProfileModal.style.display = 'flex';
});

settingsBtn.addEventListener('click', () => {
    settingsModal.style.display = 'flex';
});

// Event listeners to close modals
closeButtons.forEach((close) => {
    close.addEventListener('click', () => {
        close.closest('.modal').style.display = 'none';
    });
});

// Close modals on outside click
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});
