function createCard(product) {
    const card = document.createElement("div");
    card.classList.add("card-relationed");

    const image = document.createElement("img");
    image.src = product.image;
    image.alt = product.title;
    image.style.width = "100%";

    const title = document.createElement("h3");
    title.textContent = product.title;

    const description = document.createElement("p");
    description.textContent = product.description;

    card.appendChild(image);
    card.appendChild(title);

    return card;
}

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("related-products-container");

    //mock
    const products = [
        {
            title: "Producto 1",
            image: "../images/McFarlane-Toys-Warhammer-40k-Dark-Angels-Intercessor-Artist-Proof-7-in-Collectible-Figure_268ddb18-3bf7-40d7-836b-a767b13df4a0.652a491010cf40948d44b4326d149db5.jpg"
        },
        {
            title: "Producto 2",
            image: "../images/McFarlane-Toys-Warhammer-40k-Dark-Angels-Intercessor-Artist-Proof-7-in-Collectible-Figure_268ddb18-3bf7-40d7-836b-a767b13df4a0.652a491010cf40948d44b4326d149db5.jpg"
        },
        {
            title: "Producto 3",
            image: "../images/McFarlane-Toys-Warhammer-40k-Dark-Angels-Intercessor-Artist-Proof-7-in-Collectible-Figure_268ddb18-3bf7-40d7-836b-a767b13df4a0.652a491010cf40948d44b4326d149db5.jpg"
        },
        {
            title: "Producto 4",
            image: "../images/McFarlane-Toys-Warhammer-40k-Dark-Angels-Intercessor-Artist-Proof-7-in-Collectible-Figure_268ddb18-3bf7-40d7-836b-a767b13df4a0.652a491010cf40948d44b4326d149db5.jpg"
        }
    ];

    products.forEach(product => {
        const card = createCard(product);
        container.appendChild(card);
    });
});