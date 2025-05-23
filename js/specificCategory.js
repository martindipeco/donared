import { createCard } from "./createProductCard.js";

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("related-products-container");

    //mock
    const products = [
    {
        title: "Figura Warhammer Primaris",
        image: "../images/producto1.jpg",
        location: "Almagro",
        createdAt: "2025-05-15",
        postedBy: "Carlos Gómez"
    },
    {
        title: "Figura edición limitada",
        image: "../images/producto2.jpg",
        location: "Palermo",
        createdAt: "2025-05-20",
        postedBy: "Lucía Fernández"
    },
    {
        title: "Coleccionable Dark Angels",
        image: "../images/producto3.jpg",
        location: "Caballito",
        createdAt: "2025-05-22",
        postedBy: "Martín Pérez"
    },
    {
        title: "Figura McFarlane",
        image: "../images/producto4.jpg",
        location: "Villa Urquiza",
        createdAt: "2025-05-18",
        postedBy: "Juliana Sosa"
    },
    {
        title: "Figura Warhammer Primaris",
        image: "../images/producto1.jpg",
        location: "Almagro",
        createdAt: "2025-05-15",
        postedBy: "Carlos Gómez"
    },
    {
        title: "Figura edición limitada",
        image: "../images/producto2.jpg",
        location: "Palermo",
        createdAt: "2025-05-20",
        postedBy: "Lucía Fernández"
    },
    {
        title: "Coleccionable Dark Angels",
        image: "../images/producto3.jpg",
        location: "Caballito",
        createdAt: "2025-05-22",
        postedBy: "Martín Pérez"
    },
    {
        title: "Figura McFarlane",
        image: "../images/producto4.jpg",
        location: "Villa Urquiza",
        createdAt: "2025-05-18",
        postedBy: "Juliana Sosa"
    },
    {
        title: "Figura Warhammer Primaris",
        image: "../images/producto1.jpg",
        location: "Almagro",
        createdAt: "2025-05-15",
        postedBy: "Carlos Gómez"
    },
    {
        title: "Figura edición limitada",
        image: "../images/producto2.jpg",
        location: "Palermo",
        createdAt: "2025-05-20",
        postedBy: "Lucía Fernández"
    },
    {
        title: "Coleccionable Dark Angels",
        image: "../images/producto3.jpg",
        location: "Caballito",
        createdAt: "2025-05-22",
        postedBy: "Martín Pérez"
    },
    {
        title: "Figura McFarlane",
        image: "../images/producto4.jpg",
        location: "Villa Urquiza",
        createdAt: "2025-05-18",
        postedBy: "Juliana Sosa"
    }
];

    products.forEach(product => {
        const card = createCard(product);
        container.appendChild(card);
    });
});