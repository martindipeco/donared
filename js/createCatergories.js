document.addEventListener("DOMContentLoaded", () => {
  
    //mock
    const categories = [
        { name: "Electrónica", image: "../images/imagenesMock/1.jpg" },
        { name: "Hogar", image: "../images/imagenesMock/3.jpg" },
        { name: "Herramientas", image: "../images/imagenesMock/5.jpg" },
        { name: "Juguetes", image: "../images/imagenesMock/7.jpg" },
        { name: "Ropa", image: "../images/imagenesMock/6.jpg" },
        { name: "Jardín", image: "../images/imagenesMock/2.jpg" },
    ];

    createCategoryCards(categories);

});

function createCategoryCards(categories) {
    const categoriesContainer = document.getElementById("categories");

    categories.forEach(category => {
        const card = document.createElement("div");
        card.classList.add("category-card");
        card.style.backgroundImage = `url(${category.image})`;

        const title = document.createElement("div");
        title.classList.add("category-title");
        title.textContent = category.name;

        card.appendChild(title);
        categoriesContainer.appendChild(card);
    });
}
