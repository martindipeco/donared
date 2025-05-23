import { createCard } from "./createProductCard.js";

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